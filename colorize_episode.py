#!/usr/bin/env python3
"""
colorize_episode.py
Standalone CLI tool to colorize videos with zero LLM token usage.
Supports:
  --mode direct: Frame-by-frame neural inference.
  --mode fast:   Motion-aware keyframe chroma propagation with direct fallback.
"""

import os
import sys
import glob
import json
import time
import fcntl
import argparse
import subprocess
from pathlib import Path
from collections import deque
import cv2
import numpy as np
import torch
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "DDColor"))

from ddcolor import DDColor, ColorizationPipeline, build_ddcolor_model
from temporal_chroma import ALGORITHM_VERSION, ShotChromaStabilizer, interpolate_chroma
from space_palette import apply_space_palette, find_credit_frame_ranges

DEFAULT_INPUT_DIR = Path(os.environ.get("LIS_INPUT_DIR", BASE_DIR / "input")).expanduser()
DEFAULT_OUTPUT_DIR = Path(os.environ.get("LIS_OUTPUT_DIR", BASE_DIR / "output")).expanduser()
LIVE_PREVIEWS_DIR = BASE_DIR / "live_previews"

def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def split_long_shots(shots, max_frames=240):
    """Yield bounded windows so a missed camera cut cannot exhaust MPS RAM."""
    for shot in shots:
        start = shot["start_frame"]
        final_end = shot["end_frame"]
        while start <= final_end:
            end = min(final_end, start + max_frames - 1)
            window = dict(shot)
            window["start_frame"] = start
            window["end_frame"] = end
            yield window
            start = end + 1

def detect_shots(video_path, threshold=24.0, min_shot_len_sec=0.8, cache_dir=None):
    if cache_dir:
        cache_file = cache_dir / "shots.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    shots = json.load(f)
                print(f"[1/3] Loaded {len(shots)} previously detected shots from cache.")
                return shots
            except Exception:
                pass

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 23.976
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    min_shot_frames = int(fps * min_shot_len_sec)

    shots = []
    prev_gray = None
    shot_start = 0
    shot_idx = 0

    print(f"\n[1/3] Detecting shots in '{video_path.name}' ({total_frames} frames, {total_frames/fps/60:.1f} min)...")
    pbar = tqdm(total=total_frames, unit="fr", desc="Shot Detection", ncols=90)

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small = cv2.resize(frame, (180, 131), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            mean_diff = np.mean(diff)

            if mean_diff > threshold and (frame_idx - shot_start) >= min_shot_frames:
                shots.append({
                    "shot_id": shot_idx,
                    "start_frame": shot_start,
                    "end_frame": frame_idx - 1,
                    "keyframe": shot_start + (frame_idx - shot_start) // 2
                })
                shot_idx += 1
                shot_start = frame_idx

        prev_gray = gray
        frame_idx += 1
        pbar.update(1)

    pbar.close()
    cap.release()

    if frame_idx > shot_start:
        shots.append({
            "shot_id": shot_idx,
            "start_frame": shot_start,
            "end_frame": frame_idx - 1,
            "keyframe": shot_start + (frame_idx - shot_start) // 2
        })

    print(f"[1/3] Identified {len(shots)} distinct camera shots.")
    if cache_dir:
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            with open(cache_dir / "shots.json", "w") as f:
                json.dump(shots, f)
        except Exception:
            pass
    return shots

def process_video(video_path, output_path, model, shots, mode="fast", sample_step=None, crf=18, preset="medium", chunk_size=500, model_size="large"):
    """
    Automated video colorization pipeline with chunked checkpointing:
    - Mode 'fast' (Default): Motion-aware keyframe chroma propagation.
    - Mode 'balanced': Denser motion-aware keyframe chroma propagation.
    - Mode 'direct': Per-frame neural inference (~3.8 fps, ~5.5 hours per episode).
    - Preserves 100% native luminance L in all modes.
    - Saves progress every chunk_size frames so work can resume safely.
    - Losslessly concatenates chunks and multiplexes audio tracks and chapters from source MKV.
    """
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 23.976
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    credit_ranges = find_credit_frame_ranges(video_path, fps, total_frames)

    def is_credit_frame(frame_number):
        return any(start <= frame_number < end for start, end in credit_ranges)

    ep_preview_dir = LIVE_PREVIEWS_DIR / video_path.stem
    ep_preview_dir.mkdir(parents=True, exist_ok=True)
    latest_preview_file = LIVE_PREVIEWS_DIR / "latest.jpg"

    cache_dir = BASE_DIR / ".cache" / video_path.stem
    if mode == "direct":
        step = 1
    elif mode == "balanced":
        step = sample_step or 8
    else:
        step = sample_step or 20

    # Never reuse chunks produced by the old coordinate-based interpolation,
    # or by a different model/mode/quality configuration.
    cache_variant = f"{ALGORITHM_VERSION}_{mode}_s{step}_{model_size}_crf{crf}_{preset}"
    chunks_dir = cache_dir / cache_variant
    chunks_dir.mkdir(parents=True, exist_ok=True)

    # Group shots into chunks of ~chunk_size frames
    chunks = []
    curr_chunk = []
    curr_frames = 0
    for shot in shots:
        shot_len = shot["end_frame"] - shot["start_frame"] + 1
        curr_chunk.append(shot)
        curr_frames += shot_len
        if curr_frames >= chunk_size:
            chunks.append(curr_chunk)
            curr_chunk = []
            curr_frames = 0
    if curr_chunk:
        chunks.append(curr_chunk)

    total_chunks = len(chunks)
    colorizer = ColorizationPipeline(model, input_size=512, device=next(model.parameters()).device)
    preview_interval = max(24, int(fps * 2))

    # Check already completed chunks
    completed_chunks = 0
    completed_frames = 0
    for idx, ch in enumerate(chunks):
        ts_file = chunks_dir / f"chunk_{idx:04d}.ts"
        done_file = chunks_dir / f"chunk_{idx:04d}.done"
        if ts_file.exists() and done_file.exists():
            completed_chunks += 1
            completed_frames += sum((s["end_frame"] - s["start_frame"] + 1) for s in ch)

    print(f"\n[2/3] Plan: {total_chunks} blocks (~{chunk_size} frames each)")
    print(f"👀 Live preview gallery: {ep_preview_dir}")
    print(f"💾 Resumable checkpoint directory: {chunks_dir}")

    if completed_chunks > 0:
        print(f"🔄 [RESUME] Found {completed_chunks}/{total_chunks} completed blocks ({completed_frames}/{total_frames} frames ready).")
        print(f"   Resuming automatically from block {completed_chunks + 1}...")

    if mode == "direct":
        mode_label = "Direct (Per-Frame)"
    elif mode == "balanced":
        mode_label = f"Balanced (Step {step})"
    else:
        mode_label = f"Fast (Step {step})"
    print(f"[3/3] Colorizing footage ({mode_label}) on the Metal GPU...")
    pbar = tqdm(total=total_frames, initial=completed_frames, unit="fr", desc=f"Colorize [{mode}]", ncols=90)
    start_time = time.time()
    frame_counter = completed_frames
    chroma_stabilizer = ShotChromaStabilizer()

    for chunk_idx, ch_shots in enumerate(chunks):
        ts_file = chunks_dir / f"chunk_{chunk_idx:04d}.ts"
        done_file = chunks_dir / f"chunk_{chunk_idx:04d}.done"

        if ts_file.exists() and done_file.exists():
            continue

        tmp_ts = chunks_dir / f"temp_{chunk_idx:04d}.ts"
        if tmp_ts.exists():
            tmp_ts.unlink()

        ffmpeg_cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostats", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "bgr24",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            str(tmp_ts)
        ]

        ffmpeg_log = chunks_dir / f"temp_{chunk_idx:04d}.ffmpeg.log"
        log_handle = open(ffmpeg_log, "wb")
        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=log_handle,
        )
        interrupted = False

        try:
            for shot in split_long_shots(ch_shots):
                start_f = shot["start_frame"]
                end_f = shot["end_frame"]
                shot_len = end_f - start_f + 1

                # Ensure VideoCapture is positioned at start_f
                cur_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                if cur_pos != start_f:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)

                # Read all frames of the shot sequentially (100% frame-accurate, zero seek error)
                shot_frames = []
                for _ in range(shot_len):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    shot_frames.append(frame)

                if not shot_frames:
                    continue

                if mode == "direct":
                    for local_idx, frame in enumerate(shot_frames):
                        frame_f = (frame / 255.0).astype(np.float32)
                        orig_lab = cv2.cvtColor(frame_f, cv2.COLOR_BGR2Lab)
                        orig_l = orig_lab[:, :, :1]

                        colorized_bgr = colorizer.process(frame)
                        colorized_f = (colorized_bgr / 255.0).astype(np.float32)
                        colorized_lab = cv2.cvtColor(colorized_f, cv2.COLOR_BGR2Lab)
                        ab = colorized_lab[:, :, 1:]
                        ab = apply_space_palette(
                            frame, ab, credit_hint=is_credit_frame(start_f + local_idx)
                        )
                        ab = chroma_stabilizer.stabilize(ab, shot["shot_id"])

                        clean_lab = np.concatenate((orig_l, ab), axis=-1)
                        clean_bgr = cv2.cvtColor(clean_lab, cv2.COLOR_LAB2BGR)
                        clean_uint8 = np.clip(clean_bgr * 255.0, 0, 255).astype(np.uint8)

                        proc.stdin.write(clean_uint8.tobytes())
                        pbar.update(1)
                        frame_counter += 1
                        if frame_counter % preview_interval == 0:
                            preview_name = f"frame_{frame_counter:06d}.jpg"
                            cv2.imwrite(str(ep_preview_dir / preview_name), clean_uint8, [cv2.IMWRITE_JPEG_QUALITY, 90])
                            cv2.imwrite(str(latest_preview_file), clean_uint8, [cv2.IMWRITE_JPEG_QUALITY, 85])

                else:
                    # Keyframe sampling strictly within shot boundaries
                    n_frames = len(shot_frames)
                    sample_indices = list(range(0, n_frames, step))
                    if sample_indices[-1] != n_frames - 1:
                        sample_indices.append(n_frames - 1)

                    keyframe_chroma = {}
                    for kf in sample_indices:
                        col = colorizer.process(shot_frames[kf])
                        col_f = (col / 255.0).astype(np.float32)
                        lab = cv2.cvtColor(col_f, cv2.COLOR_BGR2Lab)
                        keyframe_chroma[kf] = lab[:, :, 1:]

                    sample_keys = sorted(keyframe_chroma.keys())
                    for i, frame in enumerate(shot_frames):
                        frame_f = (frame / 255.0).astype(np.float32)
                        orig_l = cv2.cvtColor(frame_f, cv2.COLOR_BGR2Lab)[:, :, :1]

                        if len(sample_keys) == 1 or i <= sample_keys[0]:
                            target_ab = keyframe_chroma[sample_keys[0]]
                        elif i >= sample_keys[-1]:
                            target_ab = keyframe_chroma[sample_keys[-1]]
                        else:
                            for k_idx in range(len(sample_keys) - 1):
                                if sample_keys[k_idx] <= i <= sample_keys[k_idx+1]:
                                    k1, k2 = sample_keys[k_idx], sample_keys[k_idx+1]
                                    break
                            w2 = (i - k1) / max(1, k2 - k1)
                            target_ab, flow_confidence, motion = interpolate_chroma(
                                frame,
                                shot_frames[k1],
                                shot_frames[k2],
                                keyframe_chroma[k1],
                                keyframe_chroma[k2],
                                w2,
                            )

                            # Fast-moving graphics and occlusions are safer with
                            # direct inference than with any temporal propagation.
                            if flow_confidence < 0.62:
                                direct = colorizer.process(frame)
                                direct_lab = cv2.cvtColor(
                                    (direct / 255.0).astype(np.float32), cv2.COLOR_BGR2Lab
                                )
                                target_ab = direct_lab[:, :, 1:]

                        target_ab = apply_space_palette(
                            frame, target_ab, credit_hint=is_credit_frame(start_f + i)
                        )
                        target_ab = chroma_stabilizer.stabilize(
                            target_ab, shot["shot_id"]
                        )

                        clean_lab = np.concatenate((orig_l, target_ab), axis=-1)
                        clean_bgr = cv2.cvtColor(clean_lab, cv2.COLOR_LAB2BGR)
                        clean_uint8 = np.clip(clean_bgr * 255.0, 0, 255).astype(np.uint8)

                        proc.stdin.write(clean_uint8.tobytes())
                        pbar.update(1)
                        frame_counter += 1
                        if frame_counter % preview_interval == 0:
                            preview_name = f"frame_{frame_counter:06d}.jpg"
                            cv2.imwrite(str(ep_preview_dir / preview_name), clean_uint8, [cv2.IMWRITE_JPEG_QUALITY, 90])
                            cv2.imwrite(str(latest_preview_file), clean_uint8, [cv2.IMWRITE_JPEG_QUALITY, 85])

                # Release decoded frames and Metal's cached intermediates at
                # every bounded window. This prevents multi-thousand-frame
                # shots from exhausting unified memory and pausing MPS.
                del shot_frames
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()

        except KeyboardInterrupt:
            interrupted = True
            if proc.stdin:
                try:
                    proc.stdin.close()
                except Exception:
                    pass
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            raise
        finally:
            if not interrupted and proc.stdin:
                try:
                    proc.stdin.close()
                except Exception:
                    pass
            if not interrupted:
                proc.wait()
            log_handle.close()

        if proc.returncode != 0:
            err = ffmpeg_log.read_text(errors="ignore") if ffmpeg_log.exists() else ""
            print(f"\n[ERROR] FFmpeg failed in block {chunk_idx}: {err}")
            return False

        if tmp_ts.exists():
            tmp_ts.rename(ts_file)
            done_file.write_text("done")
            if ffmpeg_log.exists():
                ffmpeg_log.unlink()

    pbar.close()
    cap.release()

    # Final lossless concatenation + audio/chapter muxing
    print(f"\n[Final assembly] Joining {total_chunks} blocks and remuxing audio tracks...")
    concat_list = cache_dir / "concat_list.txt"
    with open(concat_list, "w") as f:
        for idx in range(total_chunks):
            ch_ts = chunks_dir / f"chunk_{idx:04d}.ts"
            f.write(f"file '{ch_ts.resolve()}'\n")

    temp_final = output_path.with_suffix(".temp.mp4")
    concat_cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostats", "-y",
        "-fflags", "+genpts",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-i", str(video_path),
        "-map", "0:v:0",
        "-map", "1:a?",
        "-map_metadata", "1",
        "-map_chapters", "1",
        "-c", "copy",
        "-shortest",
        "-movflags", "+faststart",
        str(temp_final)
    ]

    try:
        res = subprocess.run(
            concat_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Final assembly exceeded five minutes; checkpoints were preserved.")
        return False
    if res.returncode != 0:
        err = res.stderr.decode("utf-8", errors="ignore")
        print(f"\n[ERROR] Final concatenation failed: {err}")
        return False

    temp_final.rename(output_path)

    # Clean up checkpoint chunks upon full completion
    for idx in range(total_chunks):
        ts_f = chunks_dir / f"chunk_{idx:04d}.ts"
        dn_f = chunks_dir / f"chunk_{idx:04d}.done"
        if ts_f.exists():
            ts_f.unlink()
        if dn_f.exists():
            dn_f.unlink()
    if concat_list.exists():
        concat_list.unlink()

    elapsed = time.time() - start_time
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n✅ Completed successfully in {elapsed/60:.1f} minutes ({total_frames/elapsed:.1f} fps).")
    print(f"📦 Final file: {output_path} ({file_size_mb:.1f} MB)\n")
    return True

def find_episode_file(input_dir, ep_num):
    patterns = [
        f"*S01E{ep_num:02d}*.mkv",
        f"*s01e{ep_num:02d}*.mkv",
        f"*S01E{ep_num}*.mkv",
        f"*E{ep_num:02d}*.mkv"
    ]
    for pat in patterns:
        matches = list(input_dir.glob(pat))
        if matches:
            return matches[0]
    return None

def main():
    parser = argparse.ArgumentParser(description="Lost in Space - Local Batch Video Colorizer")
    parser.add_argument("target", nargs="?", default="1", help="Episode to process: number (e.g. '1', '2'), range ('1-3'), 'all', or path to a .mkv file")
    parser.add_argument("-all", "--all", dest="process_all", action="store_true", help="Process all MKV files in the input directory")
    parser.add_argument("--mode", type=str, default="fast", choices=["fast", "balanced", "direct"], help="Mode: 'fast' (optical flow, step 20), 'balanced' (optical flow, step 8), 'direct' (per-frame inference)")
    parser.add_argument("--sample-step", type=int, default=None, help="Keyframe sample step (default: 20 in fast, 8 in balanced)")
    parser.add_argument("--input-dir", type=str, default=str(DEFAULT_INPUT_DIR), help="Directory containing B&W episodes")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Destination directory for colorized episodes")
    parser.add_argument("--crf", type=int, default=18, help="H.264 quality CRF (default: 18)")
    parser.add_argument("--preset", type=str, default="medium", choices=["ultrafast", "fast", "medium", "slow"], help="x264 preset")
    parser.add_argument("--model-size", type=str, default="large", choices=["tiny", "large"], help="DDColor model size")
    parser.add_argument("--chunk-size", type=int, default=500, help="Checkpoint block size (default: 500 frames)")
    parser.add_argument("--force", action="store_true", help="Force reprocessing by ignoring completed episodes")

    args = parser.parse_args()

    # Metal/MPS and the checkpoint writer must have a single owner. A second
    # invocation previously caused both FFmpeg processes to write temp_*.ts
    # concurrently and left the GPU call in an uninterruptible wait.
    lock_path = BASE_DIR / ".colorize.lock"
    lock_handle = open(lock_path, "a+")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_handle.seek(0)
        owner = lock_handle.read().strip() or "unknown"
        print(f"Error: another colorizer process is already active (PID {owner}).")
        print("Do not start a second instance; use the session that is already running.")
        sys.exit(2)
    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(str(os.getpid()))
    lock_handle.flush()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    target_files = []
    target = "all" if args.process_all else args.target.strip()

    if target.endswith(".mkv") or target.endswith(".mp4"):
        fpath = Path(target)
        if not fpath.exists():
            print(f"Error: file not found: {fpath}")
            sys.exit(1)
        target_files.append(fpath)
    elif target.lower() == "all":
        target_files = sorted(list(input_dir.glob("*.mkv")))
    elif "-" in target:
        start_ep, end_ep = map(int, target.split("-"))
        for ep in range(start_ep, end_ep + 1):
            f = find_episode_file(input_dir, ep)
            if f:
                target_files.append(f)
            else:
                print(f"Warning: episode {ep} was not found in {input_dir}")
    elif target.isdigit():
        ep = int(target)
        f = find_episode_file(input_dir, ep)
        if f:
            target_files.append(f)
        else:
            print(f"Error: episode {ep} was not found in {input_dir}")
            sys.exit(1)
    else:
        print(f"Unrecognized target: {target}")
        sys.exit(1)

    if not target_files:
        print("No files found to process.")
        sys.exit(1)

    if args.mode == "fast":
        step_val = args.sample_step or 20
        mode_str = f"FAST WITH OPTICAL FLOW (keyframe step {step_val})"
    elif args.mode == "balanced":
        step_val = args.sample_step or 8
        mode_str = f"BALANCED WITH OPTICAL FLOW (keyframe step {step_val})"
    else:
        step_val = 1
        mode_str = "DIRECT (Maximum fidelity, ~5.5 h/ep, per-frame)"

    print("=" * 70)
    print("   LOST IN SPACE - AUTOMATED LOCAL COLORIZER (ZERO TOKENS)")
    print("=" * 70)
    print(f"GPU Device      : {get_device()} (Apple Silicon Metal)")
    print(f"Quality Mode    : {mode_str}")
    print(f"DDColor Model   : {args.model_size.upper()}")
    print(f"Checkpoints     : Every {args.chunk_size} frames -> Auto-Resume enabled")
    print(f"Total Episodes  : {len(target_files)}")
    for i, tf in enumerate(target_files, 1):
        print(f"  {i}. {tf.name}")
    print(f"Live Gallery    : {LIVE_PREVIEWS_DIR}")
    print("=" * 70)

    device = get_device()
    model_name = "ddcolor_modelscope.pth" if args.model_size == "large" else "ddcolor_paper_tiny.pth"
    model_path = BASE_DIR / "models" / model_name

    if not model_path.exists():
        print(f"Downloading model weights for {model_name}...")
        subprocess.run([
            "curl", "-L",
            f"https://huggingface.co/piddnad/DDColor-models/resolve/main/{model_name}",
            "-o", str(model_path)
        ], check=True)

    print(f"\nLoading neural network on {device}...")
    model = build_ddcolor_model(
        DDColor,
        model_path=str(model_path),
        input_size=512,
        model_size=args.model_size,
        device=device
    )

    for idx, video_file in enumerate(target_files, 1):
        out_name = video_file.stem.replace(".REMASTERED.BDRip.x264-PHASE", "") + ".Colorized.latino.mp4"
        out_path = output_dir / out_name
        cache_dir = BASE_DIR / ".cache" / video_file.stem

        if out_path.exists() and out_path.stat().st_size > 50 * 1024 * 1024 and not args.force:
            size_mb = out_path.stat().st_size / (1024 * 1024)
            print(f"\n⏩ [SKIP] Episode [{idx}/{len(target_files)}] is already completed:")
            print(f"   File: {out_name} ({size_mb:.1f} MB)")
            print(f"   Destination: {out_path}")
            print(f"   (To force reprocessing run: {sys.argv[0]} {args.target} --force)")
            continue

        if args.force and cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir, ignore_errors=True)

        print(f"\n>>> PROCESSING [{idx}/{len(target_files)}]: {video_file.name}")
        shots = detect_shots(video_file, cache_dir=cache_dir)
        process_video(video_file, out_path, model, shots, mode=args.mode, sample_step=args.sample_step, crf=args.crf, preset=args.preset, chunk_size=args.chunk_size, model_size=args.model_size)

    print("\n🎉 All selected episodes have been colorized!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
colorize_video.py
Full automated video colorization pipeline with Apple Silicon Metal MPS acceleration.
Supports CLI arguments:
  python colorize_video.py --input <path> --output <path> [--shots <path>]
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
import cv2
import numpy as np
import torch
from tqdm import tqdm

# Add DDColor to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "DDColor"))

from ddcolor import DDColor, ColorizationPipeline, build_ddcolor_model
from temporal_chroma import interpolate_chroma
from space_palette import apply_space_palette, find_credit_frame_ranges

def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

def colorize_shot(cap, shot, colorizer, temp_dir, fps, credit_ranges):
    start_frame = shot["start_frame"]
    end_frame = shot["end_frame"]
    num_frames = end_frame - start_frame + 1

    sample_step = 36 # ~1.5s interval
    sample_indices = list(range(start_frame, end_frame + 1, sample_step))
    if sample_indices[-1] != end_frame:
        sample_indices.append(end_frame)

    keyframe_chroma = {}
    keyframe_frames = {}
    for kf_idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, kf_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        colorized_bgr = colorizer.process(frame)
        colorized_f = (colorized_bgr / 255.0).astype(np.float32)
        colorized_lab = cv2.cvtColor(colorized_f, cv2.COLOR_BGR2Lab)
        ab = colorized_lab[:, :, 1:]
        keyframe_chroma[kf_idx] = ab
        keyframe_frames[kf_idx] = frame

    if not keyframe_chroma:
        return

    sample_keys = sorted(keyframe_chroma.keys())

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    for f_idx in range(start_frame, end_frame + 1):
        ret, frame = cap.read()
        if not ret:
            break

        frame_f = (frame / 255.0).astype(np.float32)
        orig_lab = cv2.cvtColor(frame_f, cv2.COLOR_BGR2Lab)
        orig_l = orig_lab[:, :, :1]

        if len(sample_keys) == 1 or f_idx <= sample_keys[0]:
            target_ab = keyframe_chroma[sample_keys[0]]
        elif f_idx >= sample_keys[-1]:
            target_ab = keyframe_chroma[sample_keys[-1]]
        else:
            k1 = sample_keys[0]
            k2 = sample_keys[-1]
            for i in range(len(sample_keys) - 1):
                if sample_keys[i] <= f_idx <= sample_keys[i+1]:
                    k1 = sample_keys[i]
                    k2 = sample_keys[i+1]
                    break
            weight2 = (f_idx - k1) / max(1, (k2 - k1))
            target_ab, confidence, motion = interpolate_chroma(
                frame, keyframe_frames[k1], keyframe_frames[k2],
                keyframe_chroma[k1], keyframe_chroma[k2], weight2
            )
            if confidence < 0.62:
                direct = colorizer.process(frame)
                direct_lab = cv2.cvtColor(
                    (direct / 255.0).astype(np.float32), cv2.COLOR_BGR2Lab
                )
                target_ab = direct_lab[:, :, 1:]

        credit_hint = any(start <= f_idx < end for start, end in credit_ranges)
        target_ab = apply_space_palette(frame, target_ab, credit_hint=credit_hint)

        final_lab = np.concatenate((orig_l, target_ab), axis=-1)
        final_bgr = cv2.cvtColor(final_lab, cv2.COLOR_LAB2BGR)
        final_uint8 = np.clip(final_bgr * 255.0, 0, 255).astype(np.uint8)

        out_frame_path = temp_dir / f"frame_{f_idx:06d}.png"
        cv2.imwrite(str(out_frame_path), final_uint8)

def main():
    parser = argparse.ArgumentParser(description="Automated Video Colorizer with Lum Preservation")
    parser.add_argument("--input", type=str, default=str(BASE_DIR / "input" / "s01e01_test_clip.mkv"), help="Input video path")
    parser.add_argument("--output", type=str, default=str(BASE_DIR / "output" / "s01e01_pilot_colorized.mp4"), help="Output video path")
    parser.add_argument("--shots", type=str, default="", help="Path to shots.json (if empty, searches next to video or in keyframes)")

    args = parser.parse_args()
    video_path = Path(args.input)
    final_output_path = Path(args.output)
    final_output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.shots:
        shots_json_path = Path(args.shots)
    else:
        candidates = [
            video_path.parent / "shots.json",
            BASE_DIR / "keyframes" / "shots.json"
        ]
        shots_json_path = next((p for p in candidates if p.exists()), None)
        if not shots_json_path:
            raise FileNotFoundError("Could not find shots.json. Please run split_shots.py first or specify --shots.")

    temp_frames_dir = final_output_path.parent / f"temp_{video_path.stem}"
    temp_frames_dir.mkdir(parents=True, exist_ok=True)

    with open(shots_json_path, "r", encoding="utf-8") as f:
        shots = json.load(f)

    device = get_device()
    print(f"[Colorizer] Initializing DDColor on {device}...")

    model_path = BASE_DIR / "models" / "ddcolor_modelscope.pth"
    model_size = "large"
    if not model_path.exists():
        model_path = BASE_DIR / "models" / "ddcolor_paper_tiny.pth"
        model_size = "tiny"

    model = build_ddcolor_model(
        DDColor,
        model_path=str(model_path),
        input_size=512,
        model_size=model_size,
        device=device
    )
    colorizer = ColorizationPipeline(model, input_size=512, device=device)

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 23.976
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    credit_ranges = find_credit_frame_ranges(video_path, fps, total_frames)

    print(f"[Colorizer] Processing {len(shots)} shots ({total_frames} frames) at {fps:.3f} fps...")
    pbar = tqdm(total=len(shots), desc="Shots")

    for shot in shots:
        colorize_shot(cap, shot, colorizer, temp_frames_dir, fps, credit_ranges)
        pbar.update(1)

    pbar.close()
    cap.release()

    print("[Colorizer] Assembling final video and muxing audio...")
    cmd = [
        "ffmpeg", "-y",
        "-r", str(fps),
        "-i", str(temp_frames_dir / "frame_%06d.png"),
        "-i", str(video_path),
        "-map", "0:v:0",
        "-map", "1:a?",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(final_output_path)
    ]
    subprocess.run(cmd, check=True)
    print(f"[Colorizer] Finished! Output saved to:\n  {final_output_path}")

    print("[Colorizer] Cleaning up temporary frames...")
    for f in temp_frames_dir.glob("frame_*.png"):
        f.unlink()
    try:
        temp_frames_dir.rmdir()
    except Exception:
        pass

if __name__ == "__main__":
    main()

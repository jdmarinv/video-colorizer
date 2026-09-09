#!/usr/bin/env python3
"""
split_shots.py
Detects shot transitions in a video file and extracts representative keyframes for each shot.
Supports CLI arguments: python split_shots.py <video_path> [--out_dir <dir>]
"""

import os
import sys
import json
import argparse
from pathlib import Path
import cv2
import numpy as np
from tqdm import tqdm

def detect_shots(video_path, threshold=24.0, min_shot_len_sec=0.8):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 23.976
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    min_shot_frames = int(fps * min_shot_len_sec)

    shots = []
    prev_gray = None
    shot_start = 0
    shot_idx = 0

    print(f"[ShotDetector] Scanning {total_frames} frames ({total_frames / fps:.2f}s) at threshold {threshold}...")
    pbar = tqdm(total=total_frames, unit="frame")

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
                    "start_time": round(shot_start / fps, 3),
                    "end_time": round((frame_idx - 1) / fps, 3),
                    "duration": round((frame_idx - shot_start) / fps, 3),
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
            "start_time": round(shot_start / fps, 3),
            "end_time": round((frame_idx - 1) / fps, 3),
            "duration": round((frame_idx - shot_start) / fps, 3),
            "keyframe": shot_start + (frame_idx - shot_start) // 2
        })

    return shots

def extract_keyframes(video_path, shots, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    print(f"[KeyframeExtractor] Extracting keyframes for {len(shots)} shots...")

    for shot in shots:
        key_idx = shot["keyframe"]
        cap.set(cv2.CAP_PROP_POS_FRAMES, key_idx)
        ret, frame = cap.read()
        if ret:
            out_file = output_dir / f"shot_{shot['shot_id']:03d}_kf_{key_idx:06d}.jpg"
            cv2.imwrite(str(out_file), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            shot["keyframe_path"] = str(out_file)

    cap.release()

def main():
    parser = argparse.ArgumentParser(description="Shot boundary detector & keyframe extractor")
    parser.add_argument("video", nargs="?", default="/Users/jdmarinv/Dev/lost_in_space_colorize/input/s01e01_test_clip.mkv", help="Input video path")
    parser.add_argument("--threshold", type=float, default=24.0, help="Shot difference threshold")
    parser.add_argument("--out_dir", type=str, default="/Users/jdmarinv/Dev/lost_in_space_colorize/keyframes", help="Output directory")

    args = parser.parse_args()
    video_file = Path(args.video)
    base_out = Path(args.out_dir)
    shots_dir = base_out / "shots"

    shots = detect_shots(video_file, threshold=args.threshold)
    print(f"[ShotDetector] Found {len(shots)} distinct shots.")

    extract_keyframes(video_file, shots, shots_dir)

    shots_json_path = base_out / "shots.json"
    with open(shots_json_path, "w", encoding="utf-8") as f:
        json.dump(shots, f, indent=2)

    print(f"[ShotDetector] Saved shots metadata to {shots_json_path}")

if __name__ == "__main__":
    main()

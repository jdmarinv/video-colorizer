"""Motion-aware chroma propagation for video colorization."""

import cv2
import numpy as np


ALGORITHM_VERSION = "motion-v6-s02e11-credits"


def _gray_half(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.resize(gray, None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA)


def _warp_to_target(source_frame, target_frame, source_ab):
    """Warp chroma from source-frame coordinates into target-frame coordinates."""
    source_gray = _gray_half(source_frame)
    target_gray = _gray_half(target_frame)

    # DIS estimates, for each target pixel, where its content lived in source.
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST)
    dis.setUseSpatialPropagation(True)
    flow_half = dis.calc(target_gray, source_gray, None)

    height, width = target_frame.shape[:2]
    flow = cv2.resize(flow_half, (width, height), interpolation=cv2.INTER_LINEAR) / 0.35
    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
    )
    map_x = grid_x + flow[:, :, 0]
    map_y = grid_y + flow[:, :, 1]
    warped_ab = cv2.remap(
        source_ab, map_x, map_y, cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT101,
    )

    # A photometric check lowers the weight where content is newly exposed or
    # where flow cannot establish a trustworthy correspondence.
    source_full_gray = cv2.cvtColor(source_frame, cv2.COLOR_BGR2GRAY)
    target_full_gray = cv2.cvtColor(target_frame, cv2.COLOR_BGR2GRAY)
    warped_gray = cv2.remap(
        source_full_gray, map_x, map_y, cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT101,
    )
    error = cv2.absdiff(target_full_gray, warped_gray).astype(np.float32) / 255.0
    confidence = np.exp(-np.square(error / 0.12)).astype(np.float32)
    motion_p95 = float(np.percentile(np.linalg.norm(flow, axis=2), 95))
    return warped_ab, confidence, motion_p95


def interpolate_chroma(frame, previous_frame, next_frame, previous_ab, next_ab, alpha):
    """Interpolate two colorized keyframes after aligning both to ``frame``."""
    previous_warped, previous_confidence, previous_motion = _warp_to_target(
        previous_frame, frame, previous_ab
    )
    next_warped, next_confidence, next_motion = _warp_to_target(
        next_frame, frame, next_ab
    )

    previous_weight = (1.0 - alpha) * previous_confidence
    next_weight = alpha * next_confidence
    total_weight = previous_weight + next_weight
    blended = (
        previous_warped * previous_weight[:, :, None]
        + next_warped * next_weight[:, :, None]
    ) / np.maximum(total_weight[:, :, None], 1e-6)

    confidence = float(np.mean(np.maximum(previous_confidence, next_confidence)))
    motion = max(previous_motion, next_motion)
    return blended, confidence, motion

"""Stable, reference-derived palette rules for outer-space shots.

The neural model still supplies the base chroma.  These rules only constrain
materials whose canonical colours are known from the colour seasons: deep
space/window glass, warm nebulas, white helmets, and the silver Jupiter 2.
Luminance is never modified here.
"""

import json
import subprocess

import cv2
import numpy as np


PALETTE_VERSION = "space-s3-and-s02e11-credits-v2"


def find_credit_frame_ranges(video_path, fps, total_frames):
    """Locate the standard 56-second opening and final credit rolls."""
    try:
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_chapters", "-of", "json",
                str(video_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        chapters = json.loads(probe.stdout).get("chapters", [])
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        chapters = []

    duration = total_frames / fps
    ranges = []

    # On the Blu-ray masters the animated opening is its own chapter and is
    # consistently about 55-57 seconds, regardless of cold-open length.
    for chapter in chapters:
        start = float(chapter["start_time"])
        end = float(chapter["end_time"])
        if start < min(1200.0, duration * 0.5) and 54.0 <= end - start <= 58.5:
            ranges.append((round(start * fps), round(end * fps)))
            break

    # Some discs fold the closing credits into the final story chapter. Their
    # actual roll remains the final ~59 seconds used by the S02E11 reference.
    end_start = max(0.0, duration - 59.0)
    if chapters:
        last_start = float(chapters[-1]["start_time"])
        last_duration = duration - last_start
        if 45.0 <= last_duration <= 75.0:
            end_start = last_start
    ranges.append((round(end_start * fps), total_frames))
    return ranges


def _space_score(gray):
    """Return whether the frame looks like a star field, plus diagnostics."""
    height = max(1, round(gray.shape[0] * 320 / gray.shape[1]))
    small = cv2.resize(gray, (320, height), interpolation=cv2.INTER_AREA)
    dark_fraction = float(np.mean(small < 55))

    # Stars are compact *bright* highlights over a slowly varying dark
    # background. Requiring absolute brightness prevents 35 mm grain in a
    # dark cave/interior from being mistaken for a star field.
    top_hat = cv2.subtract(small, cv2.GaussianBlur(small, (0, 0), 2.0))
    components = ((top_hat > 20) & (small > 75)).astype(np.uint8)
    _, _, stats, _ = cv2.connectedComponentsWithStats(components, 8)
    star_count = sum(
        1 for _, _, width, height, area in stats[1:]
        if 1 <= area <= 35 and width <= 9 and height <= 9
    )
    edge_fraction = float(np.mean(cv2.Canny(small, 40, 100) > 0))
    bright_fraction = float(np.mean(small > 100))
    has_star_field = star_count >= 45 and bright_fraction >= 0.012
    has_diffuse_nebula = bright_fraction >= 0.06 and edge_fraction < 0.115
    is_space = (
        dark_fraction >= 0.50
        and edge_fraction < 0.155
        and (has_star_field or has_diffuse_nebula)
    )
    return is_space, dark_fraction, star_count, edge_fraction, bright_fraction


def _large_components(mask, minimum_fraction=0.0025):
    binary = (mask > 0.25).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    minimum_area = max(12, int(mask.size * minimum_fraction))
    kept = np.zeros(mask.shape, np.float32)
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] >= minimum_area:
            kept[labels == label] = 1.0
    return kept


def apply_space_palette(
    frame_bgr, chroma_ab, return_diagnostics=False, credit_hint=False
):
    """Constrain canonical colours in detected space shots.

    ``chroma_ab`` uses OpenCV's float CIE LAB convention (a/b centred at 0).
    The returned array has the same shape/type and is intended to be combined
    with the untouched L channel by the caller.
    """
    gray_u8 = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    is_space, dark_fraction, star_count, edge_fraction, bright_fraction = _space_score(gray_u8)
    is_space = is_space or credit_hint
    diagnostics = {
        "is_space": is_space,
        "is_credit": credit_hint,
        "dark_fraction": dark_fraction,
        "star_count": star_count,
        "edge_fraction": edge_fraction,
        "bright_fraction": bright_fraction,
        "deep_fraction": 0.0,
        "nebula_fraction": 0.0,
        "neutral_fraction": 0.0,
    }
    if not is_space:
        return (chroma_ab, diagnostics) if return_diagnostics else chroma_ab

    gray = gray_u8.astype(np.float32) / 255.0
    ab = chroma_ab.astype(np.float32, copy=True)
    blurred = cv2.GaussianBlur(gray, (0, 0), 3.0)
    local_variance = cv2.GaussianBlur(gray * gray, (0, 0), 3.0) - blurred * blurred
    local_std = np.sqrt(np.maximum(local_variance, 0.0))
    dark_density = cv2.blur((gray < 0.23).astype(np.float32), (31, 31))

    # Deep space and the view through the observation window carry only a
    # restrained blue cast.  Feathering avoids visible mask boundaries.
    deep = np.clip((0.27 - gray) / 0.15, 0.0, 1.0)
    deep = cv2.GaussianBlur(deep, (0, 0), 1.2)
    deep_b = -6.0 if credit_hint else -3.8
    deep_target = np.dstack((np.full_like(gray, -0.4), np.full_like(gray, deep_b)))
    deep_weight = (0.52 * deep)[:, :, None]
    ab = ab * (1.0 - deep_weight) + deep_target * deep_weight

    # Diffuse detail surrounded by black space is a nebula/star cloud.  Keep
    # it warm and yellowish across the shot instead of accepting hue changes
    # independently predicted by DDColor keyframes.
    nebula = np.clip((gray - 0.06) / 0.16, 0.0, 1.0)
    nebula *= np.clip((0.72 - gray) / 0.24, 0.0, 1.0)
    nebula *= np.clip((dark_density - 0.05) / 0.32, 0.0, 1.0)
    nebula *= np.clip(local_std / 0.012, 0.0, 1.0)
    if credit_hint:
        credit_cloud = np.clip((gray - 0.015) / 0.10, 0.0, 1.0)
        credit_cloud *= np.clip((0.62 - gray) / 0.22, 0.0, 1.0)
        credit_cloud *= np.clip(dark_density / 0.28, 0.0, 1.0)
        credit_cloud *= np.clip(local_std / 0.008, 0.0, 1.0)
        nebula = np.maximum(nebula, credit_cloud)
        nebula_target = np.dstack(
            (np.full_like(gray, 3.2), np.full_like(gray, -17.0))
        )
    else:
        # Correct unstable violet/blue predictions in live-action space shots.
        # Already-warm material and ordinary interiors pass through.
        needs_warm = np.clip((3.0 - chroma_ab[:, :, 1]) / 12.0, 0.0, 1.0)
        nebula *= needs_warm
        nebula_target = np.dstack(
            (np.full_like(gray, 1.8), np.full_like(gray, 10.5))
        )
    nebula = cv2.GaussianBlur(nebula, (0, 0), 1.1)
    palette_strength = 0.98 if credit_hint else 0.92
    warm_weight = (palette_strength * nebula)[:, :, None]
    ab = ab * (1.0 - warm_weight) + nebula_target * warm_weight

    # Smooth, coherent light surfaces are helmets or spacecraft hull.  Faces
    # retain their model chroma; the remaining surfaces converge on neutral
    # white/silver with a very slight cool reflection from space.
    smooth = np.clip((0.14 - local_std) / 0.09, 0.0, 1.0)
    light = np.clip((gray - 0.22) / 0.25, 0.0, 1.0)
    neutral_candidate = smooth * light
    neutral = _large_components(neutral_candidate)
    neutral *= neutral_candidate
    neutral = cv2.GaussianBlur(neutral, (0, 0), 1.0)
    silver_target = np.dstack((np.full_like(gray, -0.25), np.full_like(gray, -1.6)))
    neutral_weight = (0.98 * neutral)[:, :, None]
    ab = ab * (1.0 - neutral_weight) + silver_target * neutral_weight

    if credit_hint:
        # S02E11 uses orange for closing-credit lettering and for the opening
        # title/tether. Smooth white and silver surfaces stay neutral.
        detail = np.clip(local_std / 0.045, 0.0, 1.0)
        lettering = np.clip((gray - 0.42) / 0.28, 0.0, 1.0) * detail
        lettering *= (1.0 - neutral * 0.85)
        lettering = cv2.GaussianBlur(lettering, (0, 0), 0.7)
        orange = np.dstack((np.full_like(gray, 18.0), np.full_like(gray, 43.0)))
        lettering_weight = (0.88 * lettering)[:, :, None]
        ab = ab * (1.0 - lettering_weight) + orange * lettering_weight

    diagnostics.update({
        "deep_fraction": float(np.mean(deep)),
        "nebula_fraction": float(np.mean(nebula)),
        "neutral_fraction": float(np.mean(neutral)),
    })
    result = ab.astype(chroma_ab.dtype, copy=False)
    return (result, diagnostics) if return_diagnostics else result

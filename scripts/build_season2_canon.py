#!/usr/bin/env python3
"""Extract the approved Season 2 canon reference frames for vegetation, interiors, and monsters."""

import json
import subprocess
from pathlib import Path
import cv2
import numpy as np

SOURCE = Path("/Users/jdmarinv/Downloads/Lost in Space 1965 Season 2 Complete WEB x264 [i_c]")
OUTPUT = Path(__file__).resolve().parents[1] / "references" / "season2_canon"

REFERENCES = [
    # ==========================================
    # VEGETATION (planetary alien flora)
    # ==========================================
    (
        "vegetacion",
        "vegetacion_swamp_giant_leaves",
        "S02E04",
        "00:20:00",
        ["Dr. Smith"],
        "Giant leaves and exotic alien swamp plants with red flowers and mist."
    ),
    (
        "vegetacion",
        "vegetacion_desert_shrubs_camp",
        "S02E08",
        "00:02:40",
        ["Will", "Dr. Smith", "Robot", "Chariot"],
        "Reddish shrubs, desert brush, and alien flora beside the Chariot."
    ),
    (
        "vegetacion",
        "vegetacion_camp_trees_moss",
        "S02E10",
        "00:23:00",
        ["John", "Don", "Maureen", "Penny", "Judy", "Cousin Smith"],
        "Alien trees, twisted branches, and rocky ground at the Robinson camp."
    ),
    (
        "vegetacion",
        "vegetacion_hydroponics_flowers",
        "S02E15",
        "00:12:30",
        ["Frog Creature"],
        "Giant alien flower with bright red petals and green leaves beside the frog creature."
    ),
    (
        "vegetacion",
        "vegetacion_green_dimension_shrubs",
        "S02E16",
        "00:37:05",
        ["Penny", "Will"],
        "Dense green alien shrubs with bright yellow flowers and fruit."
    ),
    (
        "vegetacion",
        "vegetacion_forest_rocks_logs",
        "S02E17",
        "00:17:40",
        [],
        "Planetary set with red coral plants, orange shrubs, and alien trees."
    ),
    (
        "vegetacion",
        "vegetacion_tropical_alien_palms",
        "S02E21",
        "00:24:00",
        ["Don", "Maureen", "Judy"],
        "Exterior alien foliage with long-leaf plants and shrubs."
    ),
    (
        "vegetacion",
        "vegetacion_cultivated_alien_crops",
        "S02E25",
        "00:21:00",
        ["John", "Don", "Colonists"],
        "Alien garden and cultivated crops with exotic flowers and fences."
    ),
    (
        "vegetacion",
        "vegetacion_surface_wild_flora",
        "S02E30",
        "00:04:30",
        ["Penny", "Reptilian Creature"],
        "Planetary vegetation with dry shrubs and wild flora beside Penny and the alien."
    ),

    # ==========================================
    # INTERIORS (Jupiter 2 and interior sets)
    # ==========================================
    (
        "interiores",
        "interior_jupiter2_flight_deck_controls",
        "S02E01",
        "00:48:00",
        ["John", "Maureen", "Will", "Don"],
        "Jupiter 2 command deck with illuminated consoles, radar displays, and navigation dome."
    ),
    (
        "interiores",
        "interior_jupiter2_living_quarters_group",
        "S02E28",
        "00:07:35",
        ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Robot"],
        "Jupiter 2 living quarters with red swivel chairs, chess set, and central console."
    ),
    (
        "interiores",
        "interior_jupiter2_bridge_console_smith",
        "S02E15",
        "00:17:10",
        ["John", "Maureen", "Judy", "Penny", "Robot"],
        "Flight deck with illuminated instrument panels, cryogenic tubes, and crew."
    ),
    (
        "interiores",
        "interior_jupiter2_airlock_panels",
        "S02E02",
        "00:22:15",
        ["Lorelei", "Dr. Smith", "Robot"],
        "Decompression chamber and airlock with partitions and control panels."
    ),
    (
        "interiores",
        "interior_circus_tent_marvello",
        "S02E05",
        "00:18:00",
        ["Dr. Marvello"],
        "Interior of the space circus tent with red and gold curtains and main stage."
    ),
    (
        "interiores",
        "interior_hades_cavern_throne",
        "S02E12",
        "00:06:30",
        ["Morbus"],
        "Underground Hades chamber with purple columns, torches, and infernal set dressing."
    ),
    (
        "interiores",
        "interior_dream_lab_red_table",
        "S02E14",
        "00:14:30",
        ["Sesemar", "Radion"],
        "Alien dream laboratory with a scarlet round table and electronic panels."
    ),
    (
        "interiores",
        "interior_viking_great_hall",
        "S02E20",
        "00:20:00",
        ["Brynhilda", "Dr. Smith"],
        "Space Viking hall with banquet table, shields, horns, and torches."
    ),
    (
        "interiores",
        "interior_robot_electronic_organs",
        "S02E26",
        "00:24:15",
        ["Will", "Dr. Smith"],
        "Robot B-9 interior with giant red gears, illuminated valves, and capacitors."
    ),
    (
        "interiores",
        "interior_electronic_data_bank",
        "S02E16",
        "00:35:40",
        ["Urso"],
        "Memory bank and gold electronic circuits with sliding illuminated trays."
    ),

    # ==========================================
    # MONSTERS AND ALIEN CREATURES
    # ==========================================
    (
        "monstruos",
        "monster_nerim_rock_beast",
        "S02E01",
        "00:38:30",
        [],
        "Nerim rock-and-mud monster with raised arms in front of the Chariot windshield."
    ),
    (
        "monstruos",
        "monster_lorelei_green_siren",
        "S02E02",
        "00:22:15",
        ["Lorelei"],
        "Lorelei space siren in a glowing yellow outfit inside the airlock."
    ),
    (
        "monstruos",
        "monster_tiabo_alien_warrior",
        "S02E04",
        "00:25:00",
        ["Tiabo"],
        "Tiabo, an alien warrior with bright red beard, reddish hair, and textured skin."
    ),
    (
        "monstruos",
        "monster_yeti_space_circus",
        "S02E05",
        "00:07:00",
        ["Dr. Marvello", "Robinsons"],
        "White-furred space Yeti in a containment cage with Dr. Marvello and the Robinsons."
    ),
    (
        "monstruos",
        "monster_gamma6_alien_master",
        "S02E08",
        "00:06:20",
        ["Master of Gamma 6"],
        "Alien fighter and master with a green headband, red jewel, and studded armor."
    ),
    (
        "monstruos",
        "monster_morbus_devil_alien",
        "S02E12",
        "00:06:30",
        ["Morbus"],
        "Morbus, lord of Hades, in a bright metallic red suit with goatee and demonic face."
    ),
    (
        "monstruos",
        "monster_radion_golden_bubble",
        "S02E14",
        "00:41:10",
        ["Radion", "Sesemar"],
        "Radion, a full-body gold android monster beside the alien scientist Sesemar."
    ),
    (
        "monstruos",
        "monster_keema_golden_man",
        "S02E15",
        "00:24:20",
        ["Keema"],
        "Keema, an alien with completely metallic gold skin and clothing."
    ),
    (
        "monstruos",
        "monster_gundar_frog_warlord",
        "S02E15",
        "00:30:00",
        ["Gundar"],
        "Gundar, a reptilian monster with a frog-like head and dark robe."
    ),
    (
        "monstruos",
        "monster_athena_green_girl",
        "S02E16",
        "00:12:30",
        ["Athena"],
        "Athena, an alien woman with emerald-green skin and a transparent gold helmet."
    ),
    (
        "monstruos",
        "monster_questing_beast_dragon",
        "S02E17",
        "00:22:20",
        ["Questing Beast", "Penny"],
        "Alien dragon or beast with red scales, fangs, and a pink bow beside Penny."
    ),
    (
        "monstruos",
        "monster_brynhilda_viking",
        "S02E20",
        "00:34:30",
        ["Brynhilda", "Will"],
        "Space Viking queen with a winged helmet and battle armor beside Will."
    ),
    (
        "monstruos",
        "monster_thor_viking_warrior",
        "S02E20",
        "00:28:30",
        ["Thor"],
        "Thor, a space Viking warrior with red beard, horned helmet, and furs."
    ),
    (
        "monstruos",
        "monster_idak_alpha12",
        "S02E24",
        "00:20:15",
        ["IDAK Alpha 12"],
        "IDAK Alpha 12, a super-soldier android with silver face, blue suit, and red cape."
    ),
    (
        "monstruos",
        "monster_verda_android",
        "S02E24",
        "00:28:20",
        ["Verda"],
        "Verda the android in a metallic silver dress with spiral hair ornaments."
    ),
    (
        "monstruos",
        "monster_mechanical_men_army",
        "S02E28",
        "00:09:30",
        ["Dr. Smith", "Mechanical Men"],
        "Army of alien mini-robots with silver heads tying up Dr. Smith."
    ),
    (
        "monstruos",
        "monster_reptile_creature",
        "S02E30",
        "00:04:30",
        ["Reptilian Creature", "Penny"],
        "Green reptilian alien creature with a black robe and bracers."
    ),
    (
        "monstruos",
        "monster_arcon_white_ascetic",
        "S02E30",
        "00:38:20",
        ["Arcon"],
        "Arcon, an ascetic alien with ash-white skin and a black robe."
    )
]


def episode_path(code: str) -> Path:
    ep_num = int(code[4:6])
    matches = sorted(SOURCE.glob(f"*s02e{ep_num:02d}*.mkv"))
    if not matches:
        matches = sorted(SOURCE.glob(f"*S02E{ep_num:02d}*.mkv"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one file for {code}; found: {matches}")
    return matches[0]


def create_contact_sheet(images_info, category, output_path, cols=3, thumb_w=480, thumb_h=324):
    """Generate a clean visual contact sheet with labels for each thumbnail."""
    if not images_info:
        return

    n = len(images_info)
    rows = (n + cols - 1) // cols
    margin = 12
    banner_h = 36
    cell_w = thumb_w
    cell_h = thumb_h + banner_h

    total_w = cols * cell_w + (cols + 1) * margin
    total_h = rows * cell_h + (rows + 1) * margin

    # Dark studio background
    sheet = np.full((total_h, total_w, 3), 24, dtype=np.uint8)

    for idx, (img_path, title, subtitle) in enumerate(images_info):
        r = idx // cols
        c = idx % cols

        x0 = margin + c * (cell_w + margin)
        y0 = margin + r * (cell_h + margin)

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        thumb = cv2.resize(img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
        sheet[y0 : y0 + thumb_h, x0 : x0 + thumb_w] = thumb

        # Banner for label
        banner_y0 = y0 + thumb_h
        cv2.rectangle(sheet, (x0, banner_y0), (x0 + thumb_w, banner_y0 + banner_h), (36, 36, 36), -1)

        # Label text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text1 = title[:38]
        text2 = subtitle[:44]
        cv2.putText(sheet, text1, (x0 + 8, banner_y0 + 16), font, 0.44, (240, 240, 240), 1, cv2.LINE_AA)
        cv2.putText(sheet, text2, (x0 + 8, banner_y0 + 30), font, 0.38, (170, 200, 220), 1, cv2.LINE_AA)

    cv2.imwrite(str(output_path), sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"Contact sheet generated: {output_path.name} ({n} images)")


def build_palette():
    return {
        "version": 1,
        "season": 2,
        "purpose": "Canonical chromatic reference labels for Lost in Space Season 2 (CBS 1966–1967).",
        "categories": {
            "interiores": {
                "jupiter2_console_blue": "#1E4B82",
                "jupiter2_console_amber": "#D47C28",
                "jupiter2_walls_cream": "#C8C4B7",
                "jupiter2_chairs_red": "#B32624",
                "hades_throne_purple": "#572B62",
                "hades_fiery_red": "#A6251B",
                "dream_lab_scarlet": "#BA201D",
                "robot_circuits_pulsing_red": "#C62316",
                "viking_hall_timber_brown": "#4E3727"
            },
            "vegetacion": {
                "swamp_leaf_green": "#4E6A3B",
                "alien_fern_olive": "#657A42",
                "desert_shrub_red_amber": "#9C472E",
                "alien_flower_crimson": "#B52528",
                "alien_bush_canary_yellow": "#C9BA3E",
                "moss_rock_khaki": "#7A7B54",
                "tropical_foliage_deep_green": "#2B522F"
            },
            "monstruos": {
                "nerim_stone_mud_gray": "#635D55",
                "lorelei_siren_glow_green": "#4BA859",
                "tiabo_hair_bright_red": "#AC3724",
                "yeti_fur_warm_white": "#DDD9CE",
                "gamma6_master_emerald": "#2E7C4A",
                "morbus_devil_metallic_red": "#B81D1B",
                "radion_bubble_gold": "#C29B48",
                "keema_golden_man_metallic": "#D4A738",
                "gundar_frog_skin_dark_green": "#384E32",
                "athena_skin_emerald_green": "#58A366",
                "questing_beast_scales_terracotta": "#9E4334",
                "idak_body_blue": "#284A88",
                "idak_cape_red": "#B32624",
                "idak_face_silver": "#A9ADB3",
                "arcon_skin_ash_white": "#C2C4C6"
            }
        }
    }


def build_readme(manifest_count):
    """Return the maintained English reference-bank guide."""
    return '# Season 2 Visual Canon (1966–1967)\n\nThis bank contains 37 high-fidelity reference frames extracted from Season 2 color episodes. It is the closest chronological source for colorizing black-and-white Season 1 because it shares the studio sets, original Robot B-9 design, Chariot, props, and 1966 planetary wardrobe.\n\n## 1. Vegetation (`vegetacion/`)\n\n- **Giant leaves and ferns:** matte olive, moss, and sage greens.\n- **Desert shrubs and alien flora:** localized red, beige, canary yellow, and ochre around the Robinson camp.\n- **Hydroponic flowers:** bright crimson accents surrounded by dense green foliage.\n- **Continuity rule:** trunks, rocks, and soil retain neutral brown and ochre tones without absorbing green from nearby leaves.\n\n## 2. Interiors (`interiores/`)\n\n- **Jupiter 2 bridge and controls:** pearl-gray or beige metal consoles with cobalt blue, red, and amber illuminated controls.\n- **Living quarters:** red swivel chairs, neutral cream walls, padded acoustic panels, colored blankets, and sliding partitions.\n- **Alien sets:** the scarlet dream laboratory, purple and fire-lit Hades throne room, Viking great hall, illuminated data banks, and the glowing internal mechanisms of Robot B-9.\n\n## 3. Monsters and Alien Creatures (`monstruos/`)\n\nEach creature has an independent color identity and must never be processed with an averaged monster palette:\n\n- **Keema:** reflective metallic gold skin and suit.\n- **Gundar:** dark-green amphibian head and black robe.\n- **Athena:** emerald-green skin and transparent gold helmet.\n- **IDAK Alpha 12:** polished silver face, blue armor, and red cape.\n- **Questing Beast:** terracotta or brick-red scales and a pink bow.\n- **Morbus:** reflective fire-red satin clothing.\n- **Space Yeti:** warm white fur.\n- **Arcon:** ash-white face and black robe.\n- **Mechanical Men:** silver heads and metallic bodies.\n- **Nerim:** mud-and-stone texture.\n- **Tiabo:** bright red hair and beard.\n\n## 4. Metadata and Utilities\n\n- `manifest.json` records source episode, exact timestamp, visible elements, and usage notes.\n- `palette.json` provides representative HEX color centers by category.\n- `CONTACT_SHEET_*.jpg` files provide quick visual inspection grids for calibration.\n\nRegenerate the bank with:\n\n```bash\n.venv/bin/python scripts/build_season2_canon.py\n```\n'


def main() -> None:
    manifest = []
    category_images = {"vegetacion": [], "interiores": [], "monstruos": []}

    print("=" * 70)
    print("   SEASON 2 VISUAL CANON EXTRACTION (LOST IN SPACE)")
    print("=" * 70)

    for category, name, episode, timestamp, characters, notes in REFERENCES:
        source = episode_path(episode)
        destination = OUTPUT / category / f"{name}__{episode}_{timestamp.replace(':', '-')}.png"
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Extract a lossless PNG frame
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", timestamp, "-i", str(source), "-frames:v", "1",
            "-compression_level", "3", str(destination),
        ]
        subprocess.run(cmd, check=True)

        manifest.append({
            "category": category,
            "file": str(destination.relative_to(OUTPUT)),
            "source_episode": episode,
            "timestamp": timestamp,
            "characters": characters,
            "notes": notes,
        })

        title = name.replace("vegetacion_", "").replace("interior_", "").replace("monster_", "")
        subtitle = f"{episode} @ {timestamp}"
        category_images[category].append((destination, title, subtitle))
        print(f"[{category.upper()}] Extracted {destination.name}")

    # Write manifest.json
    manifest_path = OUTPUT / "manifest.json"
    manifest_path.write_text(
        json.dumps({"version": 1, "season": 2, "references": manifest}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nManifest saved to {manifest_path}")

    # Write palette.json
    palette_path = OUTPUT / "palette.json"
    palette_path.write_text(
        json.dumps(build_palette(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Palette saved to {palette_path}")

    # Write README.md
    readme_path = OUTPUT / "README.md"
    readme_path.write_text(build_readme(len(manifest)), encoding="utf-8")
    print(f"Documentation saved to {readme_path}")

    # Generate visual contact sheets
    print("\nGenerating visual contact sheets...")
    for cat, items in category_images.items():
        sheet_path = OUTPUT / f"CONTACT_SHEET_{cat.upper()}.jpg"
        create_contact_sheet(items, cat, sheet_path, cols=3)

    print("\n🎉 Season 2 canonical reference bank completed successfully!")


if __name__ == "__main__":
    main()

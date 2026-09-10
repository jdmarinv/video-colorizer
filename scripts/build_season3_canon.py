#!/usr/bin/env python3
"""Extract the approved Season 3 wardrobe and environment reference frames."""

from pathlib import Path
import json
import subprocess

SOURCE = Path("/Users/jdmarinv/Movies/Perdidos en el Espacio/MKV con audio latino/Temporada 3")
OUTPUT = Path(__file__).resolve().parents[1] / "references" / "season3_canon"

REFERENCES = [
    ("interiors", "interior_flight_uniform_group", "S03E04", "00:06:30", ["John", "Maureen", "Judy", "Penny", "Will", "Don"], "Silver flight uniforms with red piping."),
    ("interiors", "interior_flight_uniform_men", "S03E10", "00:19:00", ["John", "Don"], "Neutral reflective silver with narrow red piping."),
    ("interiors", "interior_planetary_group", "S03E07", "00:39:00", ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Dr. Smith"], "Complete planetary palette under interior lighting."),
    ("interiors", "interior_judy_penny", "S03E10", "00:11:30", ["Judy", "Penny"], "Judy in green and pink; Penny in purple and yellow."),
    ("interiors", "interior_smith_will", "S03E10", "00:21:30", ["Dr. Smith", "Will"], "Smith in black with green trim and lavender collar; Will in purple, yellow, and green."),
    ("exteriors", "exterior_planetary_group", "S03E06", "00:09:00", ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Dr. Smith"], "Group planetary palette under daylight."),
    ("exteriors", "exterior_john_don", "S03E06", "00:29:00", ["John", "Don"], "John in taupe/mauve and Don in green, both with yellow collars."),
    ("exteriors", "exterior_smith", "S03E09", "00:29:00", ["Dr. Smith"], "Blue-black base, green trim, and lavender collar."),
    ("exteriors", "exterior_group_continuity", "S03E09", "00:21:30", ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Dr. Smith"], "Exterior continuity reference for the complete cast."),
    ("space", "space_eva_suit", "S03E01", "00:11:30", ["John"], "White helmet, metallic ring, red-orange torso, and silver sleeves."),
    ("space", "space_jupiter2_hull", "S03E01", "00:16:30", [], "Silver/cool-gray Jupiter 2 exterior hull."),
    ("space", "space_window_deep_blue", "S03E10", "00:24:00", ["John", "Don", "Will"], "Deep-blue window view with neutral silver uniforms."),
    ("space", "space_nebula_and_ship", "S03E03", "00:16:30", [], "Deep-blue star field and blue-gray metallic spacecraft."),
    ("space", "space_window_nebula", "S03E01", "00:49:00", ["Don"], "Warm yellowish nebula seen from the interior with stable black space."),
    ("caves", "cave_warm_rock", "S03E18", "00:04:00", ["Will", "Dr. Smith"], "Brown and ochre rock under warm light with nearly neutral shadows."),
    ("caves", "cave_wall_robot", "S03E18", "00:06:30", [], "Gray-brown cave wall behind the Robot for texture control."),
    ("caves", "cave_entrance_daylight", "S03E22", "00:34:00", ["John", "Will", "Dr. Smith"], "Transition between warm interior rock and cool exterior light."),
    ("caves", "cave_equipment_warm", "S03E18", "00:46:30", ["Penny"], "Cave lit with amber and red; rock remains brown rather than purple."),
    ("vegetation", "vegetation_dense_daylight", "S03E23", "00:19:00", ["Maureen", "Penny", "Will"], "Dense green foliage under neutral daylight."),
    ("vegetation", "vegetation_red_green", "S03E23", "00:21:30", ["Maureen", "Penny", "Will", "Dr. Smith"], "Green plants with localized red accents and beige ground."),
    ("vegetation", "vegetation_full_set", "S03E23", "00:34:00", ["Maureen", "John", "Don"], "Wide view of the reused vegetation set."),
    ("vegetation", "vegetation_night", "S03E08", "00:39:00", [], "Dark green foliage under night lighting; use only for night scenes."),
    ("monsters", "monster_rock_gray", "S03E16", "00:26:30", [], "Charcoal-gray rock creature with gray-green reflections and blue medallion."),
    ("monsters", "monster_rock_full_body", "S03E16", "00:11:30", ["John", "Maureen", "Dr. Smith"], "Full-body scale and separation of the creature against the interior."),
    ("monsters", "monster_green_faced", "S03E20", "00:36:30", ["Dr. Smith"], "Pale olive-green face, orange hair, and crimson/gray uniform."),
    ("monsters", "monster_red_plant", "S03E23", "00:24:00", [], "Terracotta-red plant creature with stable color across its relief."),
    ("monsters", "monster_leaf_face", "S03E23", "00:44:00", [], "Gray-green face surrounded by naturally green leaves."),
    ("monsters", "monster_blue_face", "S03E22", "00:39:00", [], "Blue-gray skin, cream hair, and purple/orange clothing."),
]


def episode_path(code: str) -> Path:
    matches = sorted(SOURCE.glob(f"Lost.in.Space.{code}.*.mkv"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one file for {code}; found: {matches}")
    return matches[0]


def main() -> None:
    manifest = []
    for category, name, episode, timestamp, characters, notes in REFERENCES:
        source = episode_path(episode)
        destination = OUTPUT / category / f"{name}__{episode}_{timestamp.replace(':', '-')}.png"
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", timestamp, "-i", str(source), "-frames:v", "1",
            "-compression_level", "3", str(destination),
        ], check=True)
        manifest.append({
            "category": category,
            "file": str(destination.relative_to(OUTPUT)),
            "source_episode": episode,
            "timestamp": timestamp,
            "characters": characters,
            "notes": notes,
        })
    (OUTPUT / "manifest.json").write_text(
        json.dumps({"version": 1, "references": manifest}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(manifest)} references in {OUTPUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Extract the approved Season 3 wardrobe and environment reference frames."""

from pathlib import Path
import json
import subprocess

SOURCE = Path("/Users/jdmarinv/Movies/Perdidos en el Espacio/MKV con audio latino/Temporada 3")
OUTPUT = Path(__file__).resolve().parents[1] / "references" / "season3_canon"

REFERENCES = [
    ("interiors", "interior_flight_uniform_group", "S03E04", "00:06:30", ["John", "Maureen", "Judy", "Penny", "Will", "Don"], "Uniformes de vuelo plateados; ribetes rojos."),
    ("interiors", "interior_flight_uniform_men", "S03E10", "00:19:00", ["John", "Don"], "Plateado neutro reflectante; ribete rojo estrecho."),
    ("interiors", "interior_planetary_group", "S03E07", "00:39:00", ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Dr. Smith"], "Paleta planetaria completa bajo luz interior."),
    ("interiors", "interior_judy_penny", "S03E10", "00:11:30", ["Judy", "Penny"], "Judy verde y rosa; Penny púrpura y amarillo."),
    ("interiors", "interior_smith_will", "S03E10", "00:21:30", ["Dr. Smith", "Will"], "Smith negro con verde y cuello lavanda; Will púrpura, amarillo y verde."),
    ("exteriors", "exterior_planetary_group", "S03E06", "00:09:00", ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Dr. Smith"], "Paleta planetaria de grupo bajo luz diurna."),
    ("exteriors", "exterior_john_don", "S03E06", "00:29:00", ["John", "Don"], "John topo/malva; Don verde; ambos con cuello amarillo."),
    ("exteriors", "exterior_smith", "S03E09", "00:29:00", ["Dr. Smith"], "Negro azulado, ribete verde y cuello lavanda."),
    ("exteriors", "exterior_group_continuity", "S03E09", "00:21:30", ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Dr. Smith"], "Control de continuidad exterior de todo el reparto."),
    ("space", "space_eva_suit", "S03E01", "00:11:30", ["John"], "Casco blanco, aro metálico, torso rojo-anaranjado y mangas plateadas."),
    ("space", "space_jupiter2_hull", "S03E01", "00:16:30", [], "Casco exterior de Júpiter 2 plateado/gris frío."),
    ("space", "space_window_deep_blue", "S03E10", "00:24:00", ["John", "Don", "Will"], "Ventanal con azul profundo; uniformes plateados neutros."),
    ("space", "space_nebula_and_ship", "S03E03", "00:16:30", [], "Campo estelar azul profundo y nave metálica azul-gris."),
    ("space", "space_window_nebula", "S03E01", "00:49:00", ["Don"], "Nebulosa cálida amarillosa vista desde interior; negro espacial estable."),
    ("caves", "cave_warm_rock", "S03E18", "00:04:00", ["Will", "Dr. Smith"], "Roca marrón y ocre bajo luz cálida; sombras casi neutras."),
    ("caves", "cave_wall_robot", "S03E18", "00:06:30", [], "Pared de cueva marrón grisácea detrás del Robot; control de textura."),
    ("caves", "cave_entrance_daylight", "S03E22", "00:34:00", ["John", "Will", "Dr. Smith"], "Transición entre roca cálida interior y luz exterior fría."),
    ("caves", "cave_equipment_warm", "S03E18", "00:46:30", ["Penny"], "Cueva iluminada con ámbar y rojo; roca permanece marrón, no púrpura."),
    ("vegetation", "vegetation_dense_daylight", "S03E23", "00:19:00", ["Maureen", "Penny", "Will"], "Follaje denso verde bajo luz diurna neutra."),
    ("vegetation", "vegetation_red_green", "S03E23", "00:21:30", ["Maureen", "Penny", "Will", "Dr. Smith"], "Plantas verdes con acentos rojos y suelo beige."),
    ("vegetation", "vegetation_full_set", "S03E23", "00:34:00", ["Maureen", "John", "Don"], "Plano amplio del decorado vegetal reciclado."),
    ("vegetation", "vegetation_night", "S03E08", "00:39:00", [], "Follaje verde oscuro bajo iluminación nocturna; usar sólo para noche."),
    ("monsters", "monster_rock_gray", "S03E16", "00:26:30", [], "Criatura pétrea gris carbón con reflejos verde-gris y medallón azul."),
    ("monsters", "monster_rock_full_body", "S03E16", "00:11:30", ["John", "Maureen", "Dr. Smith"], "Escala completa y separación de la criatura contra el interior."),
    ("monsters", "monster_green_faced", "S03E20", "00:36:30", ["Dr. Smith"], "Rostro verde oliva pálido, pelo naranja y uniforme carmesí/gris."),
    ("monsters", "monster_red_plant", "S03E23", "00:24:00", [], "Criatura vegetal rojo terracota, sin variación cromática por relieve."),
    ("monsters", "monster_leaf_face", "S03E23", "00:44:00", [], "Rostro verde grisáceo rodeado por hojas verdes naturales."),
    ("monsters", "monster_blue_face", "S03E22", "00:39:00", [], "Piel azul grisácea, cabello crema y vestuario púrpura/naranja."),
]


def episode_path(code: str) -> Path:
    matches = sorted(SOURCE.glob(f"Lost.in.Space.{code}.*.mkv"))
    if len(matches) != 1:
        raise RuntimeError(f"Se esperaba un archivo para {code}; encontrados: {matches}")
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
    print(f"Generadas {len(manifest)} referencias en {OUTPUT}")


if __name__ == "__main__":
    main()

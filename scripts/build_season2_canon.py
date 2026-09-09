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
    # VEGETACIÓN (Flora alienígena planetaria)
    # ==========================================
    (
        "vegetacion",
        "vegetacion_swamp_giant_leaves",
        "S02E04",
        "00:20:00",
        ["Dr. Smith"],
        "Hojas gigantes y plantas exóticas de pantano alienígena con flores rojas y niebla."
    ),
    (
        "vegetacion",
        "vegetacion_desert_shrubs_camp",
        "S02E08",
        "00:02:40",
        ["Will", "Dr. Smith", "Robot", "Chariot"],
        "Arbustos rojizos, matorrales desérticos y flora alienígena junto al Chariot."
    ),
    (
        "vegetacion",
        "vegetacion_camp_trees_moss",
        "S02E10",
        "00:23:00",
        ["John", "Don", "Maureen", "Penny", "Judy", "Cousin Smith"],
        "Árboles alienígenas, ramas retorcidas y suelo rocoso del campamento Robinson."
    ),
    (
        "vegetacion",
        "vegetacion_hydroponics_flowers",
        "S02E15",
        "00:12:30",
        ["Criatura Rana"],
        "Flor alienígena gigante con pétalos rojos brillantes y hojas verdes con la criatura rana."
    ),
    (
        "vegetacion",
        "vegetacion_green_dimension_shrubs",
        "S02E16",
        "00:37:05",
        ["Penny", "Will"],
        "Matorrales alienígenas verdes tupidos con flores y frutos amarillos brillantes."
    ),
    (
        "vegetacion",
        "vegetacion_forest_rocks_logs",
        "S02E17",
        "00:17:40",
        [],
        "Decorado planetario con plantas coralinas rojas, arbustos anaranjados y árboles alienígenas."
    ),
    (
        "vegetacion",
        "vegetacion_tropical_alien_palms",
        "S02E21",
        "00:24:00",
        ["Don", "Maureen", "Judy"],
        "Follaje alienígena exterior con plantas y arbustos de hojas alargadas."
    ),
    (
        "vegetacion",
        "vegetacion_cultivated_alien_crops",
        "S02E25",
        "00:21:00",
        ["John", "Don", "Colonas"],
        "Jardín y cultivos alienígenas de las colonas con flores exóticas y vallas."
    ),
    (
        "vegetacion",
        "vegetacion_surface_wild_flora",
        "S02E30",
        "00:04:30",
        ["Penny", "Criatura Reptiloide"],
        "Vegetación planetaria con arbustos secos y flora silvestre junto a Penny y el alienígena."
    ),

    # ==========================================
    # INTERIORES (Júpiter 2 y sets interiores)
    # ==========================================
    (
        "interiores",
        "interior_jupiter2_flight_deck_controls",
        "S02E01",
        "00:48:00",
        ["John", "Maureen", "Will", "Don"],
        "Puente de mando del Júpiter 2 con consolas retroiluminadas, radares y cúpula de navegación."
    ),
    (
        "interiores",
        "interior_jupiter2_living_quarters_group",
        "S02E28",
        "00:07:35",
        ["John", "Maureen", "Judy", "Penny", "Will", "Don", "Robot"],
        "Salón de descanso del Júpiter 2 con sillones giratorios rojos, ajedrez y consola central."
    ),
    (
        "interiores",
        "interior_jupiter2_bridge_console_smith",
        "S02E15",
        "00:17:10",
        ["John", "Maureen", "Judy", "Penny", "Robot"],
        "Puente de vuelo con paneles de instrumentos luminosos, tubos criogénicos y tripulación."
    ),
    (
        "interiores",
        "interior_jupiter2_airlock_panels",
        "S02E02",
        "00:22:15",
        ["Lorelei", "Dr. Smith", "Robot"],
        "Cámara de descompresión y esclusa con mamparas y paneles de control."
    ),
    (
        "interiores",
        "interior_circus_tent_marvello",
        "S02E05",
        "00:18:00",
        ["Dr. Marvello"],
        "Interior de la carpa del circo cósmico con cortinas rojas, doradas y escenario principal."
    ),
    (
        "interiores",
        "interior_hades_cavern_throne",
        "S02E12",
        "00:06:30",
        ["Morbus"],
        "Cámara subterránea de Hades con columnas púrpuras, antorchas y decorado infernal."
    ),
    (
        "interiores",
        "interior_dream_lab_red_table",
        "S02E14",
        "00:14:30",
        ["Sesemar", "Radion"],
        "Laboratorio de sueños alienígena con mesa redonda escarlata y paneles electrónicos."
    ),
    (
        "interiores",
        "interior_viking_great_hall",
        "S02E20",
        "00:20:00",
        ["Brynhilda", "Dr. Smith"],
        "Salón vikingo espacial con mesa de banquete, escudos de armas, cuernos y antorchas."
    ),
    (
        "interiores",
        "interior_robot_electronic_organs",
        "S02E26",
        "00:24:15",
        ["Will", "Dr. Smith"],
        "Interior anatómico del Robot B-9 con engranajes rojos gigantes, válvulas luminosas y condensadores."
    ),
    (
        "interiores",
        "interior_electronic_data_bank",
        "S02E16",
        "00:35:40",
        ["Urso"],
        "Banco de memoria y circuitos electrónicos dorados con bandejas luminosas deslizantes."
    ),

    # ==========================================
    # MONSTRUOS Y CRIATURAS ALIENÍGENAS
    # ==========================================
    (
        "monstruos",
        "monster_nerim_rock_beast",
        "S02E01",
        "00:38:30",
        [],
        "Monstruo Nerim de roca y barro con brazos alzados frente al parabrisas del Chariot."
    ),
    (
        "monstruos",
        "monster_lorelei_green_siren",
        "S02E02",
        "00:22:15",
        ["Lorelei"],
        "Sirena espacial Lorelei en traje amarillo resplandeciente en la esclusa."
    ),
    (
        "monstruos",
        "monster_tiabo_alien_warrior",
        "S02E04",
        "00:25:00",
        ["Tiabo"],
        "Tiabo, guerrero alienígena de barba roja brillante, cabello rojizo y piel texturizada."
    ),
    (
        "monstruos",
        "monster_yeti_space_circus",
        "S02E05",
        "00:07:00",
        ["Dr. Marvello", "Robinsons"],
        "Yeti cósmico de pelaje blanco en jaula de contención con Dr. Marvello y Robinsons."
    ),
    (
        "monstruos",
        "monster_gamma6_alien_master",
        "S02E08",
        "00:06:20",
        ["Maestro de Gamma 6"],
        "Luchador y maestro alienígena con diadema verde de gema roja y coraza tachonada."
    ),
    (
        "monstruos",
        "monster_morbus_devil_alien",
        "S02E12",
        "00:06:30",
        ["Morbus"],
        "Morbus, señor de Hades con traje rojo metálico brillante, perilla y rostro demoníaco."
    ),
    (
        "monstruos",
        "monster_radion_golden_bubble",
        "S02E14",
        "00:41:10",
        ["Radion", "Sesemar"],
        "Radion, monstruo androide dorado de cuerpo entero junto al científico alienígena Sesemar."
    ),
    (
        "monstruos",
        "monster_keema_golden_man",
        "S02E15",
        "00:24:20",
        ["Keema"],
        "Keema, alienígena con traje y piel completamente dorada metálica."
    ),
    (
        "monstruos",
        "monster_gundar_frog_warlord",
        "S02E15",
        "00:30:00",
        ["Gundar"],
        "Gundar, monstruo reptil con cabeza de rana y túnica oscura."
    ),
    (
        "monstruos",
        "monster_athena_green_girl",
        "S02E16",
        "00:12:30",
        ["Athena"],
        "Athena, mujer alienígena de piel verde esmeralda y escafandra dorada transparente."
    ),
    (
        "monstruos",
        "monster_questing_beast_dragon",
        "S02E17",
        "00:22:20",
        ["Questing Beast", "Penny"],
        "Dragón/bestia alienígena con escamas rojas, colmillos y lazo rosa junto a Penny."
    ),
    (
        "monstruos",
        "monster_brynhilda_viking",
        "S02E20",
        "00:34:30",
        ["Brynhilda", "Will"],
        "Reina vikinga espacial con casco alado y coraza de batalla junto a Will."
    ),
    (
        "monstruos",
        "monster_thor_viking_warrior",
        "S02E20",
        "00:28:30",
        ["Thor"],
        "Thor, guerrero vikingo espacial con barba roja, casco de cuernos y pieles."
    ),
    (
        "monstruos",
        "monster_idak_alpha12",
        "S02E24",
        "00:20:15",
        ["IDAK Alpha 12"],
        "IDAK Alpha 12, androide super-soldado con rostro plateado, traje azul y capa roja."
    ),
    (
        "monstruos",
        "monster_verda_android",
        "S02E24",
        "00:28:20",
        ["Verda"],
        "Verda la androide con vestido metálico plateado y peinado con espirales."
    ),
    (
        "monstruos",
        "monster_mechanical_men_army",
        "S02E28",
        "00:09:30",
        ["Dr. Smith", "Mechanical Men"],
        "Ejército de mini-robots androides alienígenas con cabezas plateadas atando al Dr. Smith."
    ),
    (
        "monstruos",
        "monster_reptile_creature",
        "S02E30",
        "00:04:30",
        ["Criatura Reptiloide", "Penny"],
        "Criatura alienígena reptiloide verde con túnica negra y brazaletes."
    ),
    (
        "monstruos",
        "monster_arcon_white_ascetic",
        "S02E30",
        "00:38:20",
        ["Arcon"],
        "Arcon, ser alienígena asceta de piel blanca ceniza y túnica negra."
    )
]


def episode_path(code: str) -> Path:
    ep_num = int(code[4:6])
    matches = sorted(SOURCE.glob(f"*s02e{ep_num:02d}*.mkv"))
    if not matches:
        matches = sorted(SOURCE.glob(f"*S02E{ep_num:02d}*.mkv"))
    if len(matches) != 1:
        raise RuntimeError(f"Se esperaba 1 archivo para {code}; encontrados: {matches}")
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

        # Labels text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text1 = title[:38]
        text2 = subtitle[:44]
        cv2.putText(sheet, text1, (x0 + 8, banner_y0 + 16), font, 0.44, (240, 240, 240), 1, cv2.LINE_AA)
        cv2.putText(sheet, text2, (x0 + 8, banner_y0 + 30), font, 0.38, (170, 200, 220), 1, cv2.LINE_AA)

    cv2.imwrite(str(output_path), sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"Hoja de contactos generada: {output_path.name} ({n} imágenes)")


def build_palette():
    return {
        "version": 1,
        "season": 2,
        "purpose": "Etiquetas cromáticas de referencia canónica para la Temporada 2 de Perdidos en el Espacio (CBS 1966-1967).",
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
    return f"""# Canon visual de la Temporada 2 (1966-1967)

Este banco reúne {manifest_count} fotogramas de referencia de alta fidelidad extraídos de los episodios en color de la **Temporada 2** de *Perdidos en el Espacio*. Constituye la base cronológica más directa y precisa para la colorización de la Temporada 1 en blanco y negro, al compartir los mismos decorados de estudio, el diseño original del Robot B-9, el carro de exploración Chariot y los vestuarios planetarios de 1966.

---

## 1. Vegetación (`vegetacion/`)

La Temporada 2 introdujo decorados exóticos de flora alienígena con una riqueza cromática muy característica:
- **Hojas y helechos gigantes:** Verdes oliva, musgo y salvia con textura mate natural (S02E04, S02E21).
- **Matorrales y flora desértica:** Tonos rojizos, beige, amarillos canarios y ocre alrededor del campamento Robinson (S02E08, S02E16).
- **Flores y especímenes hidropónicos:** Acentos puntuales de rojo carmesí brillante sobre follaje verde denso (S02E15).
- **Regla de oro:** Los troncos, rocas y tierra deben conservar su neutralidad marrón ocre sin teñirse del verde de las hojas circundantes.

---

## 2. Interiores (`interiores/`)

Los interiores reflejan la estética de ciencia ficción "Space Age / Technicolor 1966":
- **Puente y controles del Júpiter 2:** Consolas metálicas gris perla/beige, paneles con botones retroiluminados en azul cobalto, rojo y ámbar (S02E01, S02E15).
- **Cabinas de descanso y salón:** Sillones giratorios rojos, paredes en crema neutro con paneles acústicos acolchados, mantas de colores y mamparas corredizas (S02E28).
- **Sets alienígenas:** El laboratorio escarlata de Sesemar (S02E14), el trono subterráneo de Hades en púrpura y fuego (S02E12), el gran salón vikingo espacial con banquete (S02E20), los bancos de datos electrónicos luminosos (S02E16) y el interior anatómico pulsante del Robot B-9 con engranajes y válvulas luminosas incandescentes (S02E26).

---

## 3. Monstruos y Criaturas Alienígenas (`monstruos/`)

Cada criatura posee una identidad cromática única y no debe ser tratada con paletas promedio:
- **Keema (The Golden Man):** Piel y traje de oro metálico reflectante brillante (S02E15).
- **Gundar (Warlord Frog):** Cabeza de anfibio verde oscuro y túnica negra (S02E15).
- **Athena (The Green Dimension):** Piel y rostro verde esmeralda con casco espacial dorado (S02E16).
- **IDAK Alpha 12:** Androide super-soldado con rostro plateado pulido, armadura azul y capa roja (S02E24).
- **Questing Beast:** Dragón alienígena con escamas terracota/rojo ladrillo y lazo rosa (S02E17).
- **Morbus:** Diablo señor de Hades en satén rojo fuego metálico (S02E12).
- **Yeti Cósmico:** Pelaje blanco crema en jaula iluminada (S02E05).
- **Arcon:** Rostro asceta blanco ceniza con túnica negra (S02E30).
- **Mechanical Men:** Mini-robots androides alienígenas con cabezas plateadas (S02E28).
- **Nerim:** Monstruo de barro y piedra de la mina de combustible (S02E01).
- **Tiabo:** Guerrero alienígena con barba y cabello rojo brillante (S02E04).

---

## 4. Metadatos y Utilidades

- **`manifest.json`:** Registro JSON exhaustivo con episodio de origen, código de tiempo exacto, personajes/elementos presentes y notas de uso.
- **`palette.json`:** Muestras de color HEX representativas por categoría.
- **Hojas de contacto (`CONTACT_SHEET_*.jpg`):** Cuadrículas de inspección rápida para calibración visual inmediata en DaVinci Resolve.

Para regenerar el banco completo:
```bash
.venv/bin/python scripts/build_season2_canon.py
```
"""


def main() -> None:
    manifest = []
    category_images = {"vegetacion": [], "interiores": [], "monstruos": []}

    print("=" * 70)
    print("   EXTRACCIÓN DEL CANON VISUAL DE LA TEMPORADA 2 (LOST IN SPACE)")
    print("=" * 70)

    for category, name, episode, timestamp, characters, notes in REFERENCES:
        source = episode_path(episode)
        destination = OUTPUT / category / f"{name}__{episode}_{timestamp.replace(':', '-')}.png"
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Extract PNG lossless frame
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
        print(f"[{category.upper()}] Extraído {destination.name}")

    # Write manifest.json
    manifest_path = OUTPUT / "manifest.json"
    manifest_path.write_text(
        json.dumps({"version": 1, "season": 2, "references": manifest}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nManifest guardado en {manifest_path}")

    # Write palette.json
    palette_path = OUTPUT / "palette.json"
    palette_path.write_text(
        json.dumps(build_palette(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Paleta guardada en {palette_path}")

    # Write README.md
    readme_path = OUTPUT / "README.md"
    readme_path.write_text(build_readme(len(manifest)), encoding="utf-8")
    print(f"Documentación guardada en {readme_path}")

    # Generate visual contact sheets
    print("\nGenerando hojas de contacto visuales...")
    for cat, items in category_images.items():
        sheet_path = OUTPUT / f"CONTACT_SHEET_{cat.upper()}.jpg"
        create_contact_sheet(items, cat, sheet_path, cols=3)

    print("\n🎉 ¡Banco de referencias canónicas de la Temporada 2 completado con éxito!")


if __name__ == "__main__":
    main()

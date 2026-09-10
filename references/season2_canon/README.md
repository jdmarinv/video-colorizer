# Season 2 Visual Canon (1966–1967)

This bank contains 37 high-fidelity reference frames extracted from Season 2 color episodes. It is the closest chronological source for colorizing black-and-white Season 1 because it shares the studio sets, original Robot B-9 design, Chariot, props, and 1966 planetary wardrobe.

## 1. Vegetation (`vegetacion/`)

- **Giant leaves and ferns:** matte olive, moss, and sage greens.
- **Desert shrubs and alien flora:** localized red, beige, canary yellow, and ochre around the Robinson camp.
- **Hydroponic flowers:** bright crimson accents surrounded by dense green foliage.
- **Continuity rule:** trunks, rocks, and soil retain neutral brown and ochre tones without absorbing green from nearby leaves.

## 2. Interiors (`interiores/`)

- **Jupiter 2 bridge and controls:** pearl-gray or beige metal consoles with cobalt blue, red, and amber illuminated controls.
- **Living quarters:** red swivel chairs, neutral cream walls, padded acoustic panels, colored blankets, and sliding partitions.
- **Alien sets:** the scarlet dream laboratory, purple and fire-lit Hades throne room, Viking great hall, illuminated data banks, and the glowing internal mechanisms of Robot B-9.

## 3. Monsters and Alien Creatures (`monstruos/`)

Each creature has an independent color identity and must never be processed with an averaged monster palette:

- **Keema:** reflective metallic gold skin and suit.
- **Gundar:** dark-green amphibian head and black robe.
- **Athena:** emerald-green skin and transparent gold helmet.
- **IDAK Alpha 12:** polished silver face, blue armor, and red cape.
- **Questing Beast:** terracotta or brick-red scales and a pink bow.
- **Morbus:** reflective fire-red satin clothing.
- **Space Yeti:** warm white fur.
- **Arcon:** ash-white face and black robe.
- **Mechanical Men:** silver heads and metallic bodies.
- **Nerim:** mud-and-stone texture.
- **Tiabo:** bright red hair and beard.

## 4. Metadata and Utilities

- `manifest.json` records source episode, exact timestamp, visible elements, and usage notes.
- `palette.json` provides representative HEX color centers by category.
- `CONTACT_SHEET_*.jpg` files provide quick visual inspection grids for calibration.

Regenerate the bank with:

```bash
.venv/bin/python scripts/build_season2_canon.py
```

# Canon visual de la Temporada 2 (1966-1967)

Este banco reúne 37 fotogramas de referencia de alta fidelidad extraídos de los episodios en color de la **Temporada 2** de *Perdidos en el Espacio*. Constituye la base cronológica más directa y precisa para la colorización de la Temporada 1 en blanco y negro, al compartir los mismos decorados de estudio, el diseño original del Robot B-9, el carro de exploración Chariot y los vestuarios planetarios de 1966.

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

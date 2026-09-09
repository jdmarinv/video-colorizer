# Canon visual de la temporada 3

Estos fotogramas son referencias positivas extraídas de los másteres a color de la temporada 3. Están separados por contexto para impedir que el colorizador transfiera una paleta correcta a una escena equivocada. `manifest.json` conserva episodio, tiempo, personajes visibles y propósito de cada imagen.

## Interiores

En los interiores de la Júpiter 2 aparecen dos estados de vestuario:

- **Uniforme de vuelo:** tela plateada neutra y reflectante, con ribetes rojos estrechos. No debe convertirse en azul, rosa o verde por reflejos de los paneles.
- **Ropa planetaria:** se conserva la combinación asignada a cada personaje descrita abajo. La iluminación interior puede bajar la saturación, pero no cambia la identidad del color.

## Exteriores planetarios

La combinación canónica más repetida es:

| Personaje | Prenda base | Cuello y pecho | Ribetes y bandas |
|---|---|---|---|
| John Robinson | topo grisáceo con matiz malva | cuello amarillo; panel verde | bandas verde y púrpura |
| Don West | verde esmeralda | cuello amarillo; panel amarillo/verde | bandas púrpura y rosa |
| Will Robinson | púrpura | cuello amarillo; panel verde | verde en cuello y puños |
| Dr. Smith | negro o azul marino muy oscuro | cuello alto lavanda | V y puños verde brillante |
| Judy Robinson | vestido/jumper verde | mangas y canesú rosa | medias y botas verdes |
| Penny Robinson | púrpura/lavanda | mangas amarillas; panel verde | detalles verdes |
| Maureen Robinson | púrpura/lavanda | cuello rosa claro | variación tonal púrpura |

Esta tabla describe el vestuario planetario estándar, no disfraces propios de la trama. Los abrigos, ropa térmica, uniformes plateados y trajes EVA se deben resolver con referencias de su propia escena.

## Espacio

- El casco de los trajes EVA es blanco neutro o gris muy claro; el aro y los herrajes son metálicos.
- El torso acolchado EVA es rojo-anaranjado y las mangas son plateadas.
- El casco de la Júpiter 2 es plateado o gris frío, nunca púrpura ni rojo.
- El negro espacial permanece casi neutro. La ventana puede aportar un matiz azul profundo y estable.
- Las nubes difusas próximas al traje EVA son cálidas, crema o amarillosas. Los campos estelares lejanos y ciertos objetos espaciales también aparecen en azul profundo. Se elige la referencia por tipo de plano y el color permanece estable durante toda la toma.

## Cuevas

- La roca base suele ser marrón grisácea, ocre o carbón. Los reflejos ámbar proceden de lámparas y antorchas, no de una roca naranja uniforme.
- Las sombras conservan poca saturación. No deben llenarse de violeta, verde o rojo por inferencia semántica.
- Las entradas de cueva mezclan luz exterior fría con roca interior cálida. Esa transición no se debe igualar a una sola temperatura de color.

## Vegetación

- El decorado diurno combina verdes oliva, esmeralda y verde grisáceo. Las plantas rojas son elementos localizados y no deben teñir el follaje vecino.
- Los troncos y el suelo permanecen beige, marrón u ocre aunque estén rodeados de verde.
- La referencia nocturna está separada: sirve para planos nocturnos y no debe oscurecer ni azular las escenas diurnas.

## Criaturas y monstruos

Cada criatura se trata como una identidad independiente. La carpeta incluye controles para la criatura pétrea gris, el alienígena de rostro verde, el hombre vegetal rojo, el rostro de hojas verdes y el personaje de piel azul grisácea. No se crea una “paleta de monstruo” promedio ni se propaga el color de una criatura a otra.

## Uso

Las imágenes son controles de continuidad y fuentes para igualación cromática. No se debe promediar toda la carpeta en una sola paleta. Se elige primero el contexto (`interiors`, `exteriors`, `space`, `caves`, `vegetation` o `monsters`) y después el personaje o elemento visible. Para regenerar exactamente el banco:

```bash
python3 scripts/build_season3_canon.py
```

# Índice de referencias canónicas

El colorizador dispone de dos bancos de fotogramas reales en color. Los manifiestos son la fuente de verdad; una imagen que no figure en ellos se considera una toma alternativa y no se selecciona automáticamente.

| Banco | Uso principal | Manifiesto | Paleta |
|---|---|---|---|
| `season2_canon` | Referencia cronológicamente más cercana para colorizar la temporada 1: vestuario de 1966, Júpiter 2, vegetación, utilería y criaturas recicladas. | `season2_canon/manifest.json` | `season2_canon/palette.json` |
| `season3_canon` | Continuidad adicional: uniformes plateados, vestuario planetario posterior, espacio, cuevas, vegetación y criaturas reutilizadas. | `season3_canon/manifest.json` | `season3_canon/palette.json` |

## Orden de selección

1. Coincidencia del mismo objeto, traje, criatura o decorado reciclado.
2. Coincidencia del contexto y la iluminación: interior, exterior diurno, exterior nocturno, cueva o espacio.
3. Para la temporada 1, preferir temporada 2 cuando ambas referencias representan el mismo elemento, porque es la continuidad de producción más cercana.
4. Usar temporada 3 para completar elementos ausentes en temporada 2 o confirmar que un color permaneció estable.
5. No mezclar el vestuario naranja/verde de temporada 2 con el vestuario púrpura/verde ni con los uniformes plateados de temporada 3.

Las imágenes fuera de los manifiestos pueden conservarse como alternativas para inspección manual, pero no forman parte del conjunto aprobado.

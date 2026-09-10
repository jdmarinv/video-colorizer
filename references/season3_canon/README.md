# Season 3 Visual Canon

These positive reference frames come from the Season 3 color masters. They are separated by context so the colorizer does not transfer a valid palette into the wrong scene. `manifest.json` records the episode, timestamp, visible characters, and purpose of every image.

## Interiors

- **Flight uniform:** neutral reflective silver fabric with narrow red piping. Panel reflections must not turn it blue, pink, or green.
- **Planetary clothing:** preserve the character-specific combinations below. Interior lighting may lower saturation but does not change each garment's identity.

## Planetary Exteriors

| Character | Base garment | Collar and chest | Trim and bands |
|---|---|---|---|
| John Robinson | gray taupe with a mauve cast | yellow turtleneck; green panel | green and purple bands |
| Don West | emerald green | yellow turtleneck; yellow/green panel | purple and pink bands |
| Will Robinson | purple | yellow turtleneck; green panel | green collar and cuffs |
| Dr. Smith | black or very dark navy | lavender turtleneck | bright green V and cuffs |
| Judy Robinson | green jumper dress | pink sleeves and yoke | green tights and boots |
| Penny Robinson | purple/lavender | yellow sleeves; green panel | green details |
| Maureen Robinson | purple/lavender | pale pink collar | purple tonal variation |

This table describes standard planetary clothing. Coats, thermal clothing, silver uniforms, plot-specific costumes, and EVA suits require their own scene references.

## Space

- EVA helmets are neutral white or very light gray; rings and fittings are metallic.
- The quilted EVA torso is red-orange and the sleeves are silver.
- The Jupiter 2 hull is silver or cool gray, never purple or red.
- Space remains nearly neutral black. Windows may add a stable deep-blue cast.
- Diffuse clouds near the EVA suit are warm cream or yellowish. Distant star fields and some objects also appear deep blue. Select by shot type and keep color stable throughout the shot.

## Caves

- Base rock is generally gray-brown, ochre, or charcoal. Amber reflections come from lamps and torches rather than uniformly orange rock.
- Shadows retain low saturation and must not fill with violet, green, or red.
- Cave entrances mix cool exterior light with warm interior rock. Do not normalize this transition to one color temperature.

## Vegetation

- Daylight sets combine olive, emerald, and gray-green foliage. Red plants are localized elements and must not tint neighboring leaves.
- Trunks and ground remain beige, brown, or ochre even when surrounded by green.
- The night reference is separate and must only guide night scenes.

## Creatures and Monsters

Treat every creature as a separate identity. The bank includes the gray rock creature, pale olive-faced alien, terracotta plant man, gray-green leaf face, and blue-gray character. Never average these into a generic monster palette or propagate one creature's color to another.

## Use

Select the context first (`interiors`, `exteriors`, `space`, `caves`, `vegetation`, or `monsters`), followed by the visible character or element. Regenerate the bank with:

```bash
python3 scripts/build_season3_canon.py
```

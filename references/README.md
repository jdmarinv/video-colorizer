# Canonical Reference Index

The colorizer includes two banks of real color frames. Their manifests are the source of truth: an image not declared in a manifest is an alternate shot and is not selected automatically.

| Bank | Primary use | Manifest | Palette |
|---|---|---|---|
| `season2_canon` | Closest chronological reference for Season 1: 1966 wardrobe, Jupiter 2 sets, vegetation, props, and reused creatures. | `season2_canon/manifest.json` | `season2_canon/palette.json` |
| `season3_canon` | Additional continuity: silver uniforms, later planetary wardrobe, space, caves, vegetation, and reused creatures. | `season3_canon/manifest.json` | `season3_canon/palette.json` |

## Selection Order

1. Match the same object, costume, creature, or reused set.
2. Match context and lighting: interior, daylight exterior, night exterior, cave, or space.
3. When colorizing Season 1, prefer Season 2 when both banks show the same element because it is the closest production continuity.
4. Use Season 3 to cover elements absent from Season 2 or confirm that a color remained stable.
5. Never mix the orange-and-green Season 2 wardrobe with the purple-and-green or silver Season 3 wardrobe.

Images outside the manifests may remain available for manual inspection, but they are not part of the approved automatic set.

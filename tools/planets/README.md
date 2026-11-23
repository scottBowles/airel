# Planet texture generator

Generates each planet's surface textures from a **feature spec**: a list of named landmarks
with latitude, longitude, size and shape, taken from the lore (DB notes and session logs).
Landmarks go exactly where the spec puts them; seeded noise adds natural detail around
them. The same latitudes/longitudes become the place pins in the app, so the map and the
pins always agree.

```sh
python3 tools/planets/magmus.py                     # 4096×2048, into web/static/system/magmus (~4 min)
python3 tools/planets/magmus.py --width 1024 --out /tmp/m   # quick draft (~12 s)
python3 tools/planets/preview_map.py /tmp/m /tmp/m.png       # flat map with pins
```

```sh
python3 tools/planets/gonhirrim.py                  # the gas giant (~2 min)
python3 tools/planets/moons.py [durinfol ironfist …] # Gonhirrim's moons, 2048×1024 (~75 s each)
python3 tools/planets/hyang_wan.py                  # island water world (~13 min; --clouds-only ~3 min)
python3 tools/planets/felucia.py                    # jungle world with seas and rivers (~10 min)
python3 tools/planets/terran.py                     # planet-wide city, brightest night side (~10 min)
python3 tools/planets/janus.py                      # tidally locked: desert day, dark night (~9 min)
```

Moons also write `clouds.webp` (white where cloudy) for the app's cloud layer. Their render
settings (size, orbit, atmosphere and cloud colour) are in `web/src/lib/system/bodies.ts`.

Needs Python 3 with `numpy` and `Pillow` (`apt-get install python3-numpy python3-pil`).

## Output (per planet, in `web/static/system/<slug>/`)

| File | Use |
| --- | --- |
| `albedo.webp` | base colour (sRGB) |
| `emissive.webp` | glow: lava, city lights (sRGB; brightness set in the app) |
| `roughness.webp`, `normal.webp`, `height.webp` | surface detail (linear) |
| `pins.json` | place pins: DB place name, lat/lon, and `confidence` |

All maps are equirectangular: left edge 180° W, right edge 180° E, top the north pole.
`web/src/lib/system/geo.ts` maps lat/lon onto three.js's sphere the same way (tested).

`confidence` on a pin: **lore** = the logs fix the spot; **layout** = the logs give the
area; **guess** = nothing in the lore yet, placed to fit. Correct a guess by editing the spec
and re-running.

## Adding a planet

Copy `magmus.py`: write the spec from the planet's DB notes and the session logs that
mention its places (see `.ideas/projects/solar-system-3d/`), then tune the colour and
emission sections to the planet's character. Preview the flat map, then look at it in the
app at `/system/lab`.

The original Blender and Sketchfab models in the `solars` repo are kept as they are; this
generator makes new textures alongside them.

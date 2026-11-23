# Making a planet: workflow, checks and lessons

For anyone (person or agent) building a body's textures with this generator. Read this, then
`README.md` here, then the look-and-feel lessons in `.ideas/projects/solar-system-3d/README.md`
("Look-and-feel lessons"). The user reviews every planet; the aim is that they never have to
point out something a careful look would have caught.

## Inputs

- The body's lore brief: `.ideas/projects/solar-system-3d/bodies/<body>.md` (canon quotes,
  visual cues, places with lat/lon and confidence, a feature-spec draft, open questions).
- The user's answers: the top of `bodies/QUESTIONS.md` ("User's answers") and `assets.md`
  ("User's answers"). **These override the briefs' defaults.** A brief written before an answer
  may still propose what the answer ruled out.
- The closest existing generator as a pattern. `janus.py` (desert, towns, fixed sun) and
  `felucia.py` (vegetation, seas, rivers, clouds) are the most developed; `terran.py` for
  cities; `magmus.py` for emissive surfaces; `moons.py` for small bodies.
- Shared helpers: `planetgen.py` (grid, noise, fbm, ridged, ramp, smoothstep, normal map,
  savers, pins) and `clouds.py` (cloud layers).

## Conventions

- Equirectangular maps, left edge 180° W, top the north pole. `make_grid` gives
  `xyz = (cos lat cos lon, cos lat sin lon, sin lat)`.
- A script takes `--width` (default 4096) and `--out` (default `web/static/system/<slug>`)
  and writes `albedo`, `emissive`, `normal`, `roughness`, `height` (+ `clouds`,
  `clouds-normal` if it has clouds) as `.webp`, and `pins.json` via `write_pins`.
- A fixed `SEED`; everything random comes from it, so a rebuild is identical.
- Every pin is a DB place name with `confidence` lore / layout / guess. Places with no DB
  entry get no pin unless the brief says otherwise.
- Docstring at the top: the lore in short and every interpretation you made, with its source.

## Workflow

1. **Spec first.** Write the feature spec as constants (sites, sizes) with a comment per
   feature citing the lore or saying it's invented.
2. **Draft at 1024** into a scratch folder (`--width 1024 --out <scratch>/<body>_1024`):
   seconds to a minute. Look at the flat map (`preview_map.py`) and the inspector (below).
   Iterate here; fine detail can't be judged at this size, but layout, proportions and colour
   can.
3. **Full build at 4096 into scratch**, never straight into `web/static`. About 10 minutes;
   run it in the background.
4. **Inspect the full build** (below) and fix what it shows. Repeat 3–4 as needed.
5. Only then copy into `web/static/system/<slug>/`.

## Checks

### The inspector

```sh
python3 tools/planets/inspect_planet.py <maps folder> <out folder> [--sun LAT,LON]
```

Renders the maps on a lit sphere and writes `discs.png` (four sides), `places.png` (each pin
close up, lit and at night, at the app's closest zoom), `suspects.png` (the tiles that score
worst on automatic checks for stripes, speckle, thin dark lines and hard edges, each lit and
close up), and `report.txt` (scores and colour statistics). `--sun` fixes the sun for a
tidally locked world.

**Read every image it writes.** For each suspect, decide in words whether it's a fault and
why. A suspect isn't automatically a fault (salt flats should have edges), but the user has
flagged every one of these kinds of patterns before. Compare scores against Janus as a
baseline: `inspect_planet.py web/static/system/janus <out> --sun 0,0`.

### Questions to answer about every build

Write down the answers; don't just think them.

- **What does the real thing look like from orbit?** Name the Earth (or Mars, or Io)
  analogue and its real colours. Hot deserts are light tan, not dark. Rainforest is deep
  even green. If you claim an analogue looks a certain way, be sure; the user checks.
- **What's visible at this scale?** One 4096 texel is ~10 km on an Earth-sized planet. Rivers,
  wadis, roads and flash-flood channels are far below that. Drawing them big enough to see
  makes them wrong. Leave them out or let them emerge as tone.
- **Do features make physical sense together?** Lava on high ground, salt in the lowest
  basins, never touching. Rivers run downhill to the sea. Cities near water. Check where
  different features meet.
- **Proportions:** what fraction is each feature, and is that what the lore implies? (Janus's
  dark lava and white salt came out at similar sizes and counts; the user asked why.)
- **Population:** does the density of lights match the lore? Janus's Mezzolux is "where most
  people live" but nothing like Terran.
- **Both sides:** lit and night, and the terminator. What does the dark side show?

### Patterns that have failed review

- **Closed wandering lines** (worm tracks). `veins` or `|noise|` lines drawn large loop back
  on themselves. Real drainage branches and runs downhill. Use only at fine scale as tone
  (Felucia's canopy) or not at all.
- **One sine wave** (corduroy). Dunes, ridges or bands from a single `sin` at one spacing.
  Break crests into lengths, vary the spacing so crests fork, fade them at the edges.
- **Fingerprint swirls.** Stripes bent by a warp field into concentric loops.
- **Texel-scale noise** (TV static): noise whose frequency is near the texel size. Keep the
  finest noise at several texels.
- **Camouflage print:** thresholded noise at one scale gives flat blotches of two tones.
- **Hard cut-outs:** a narrow `smoothstep` on a noise field gives shapes with sharp, ragged
  edges. Natural boundaries are soft or graded unless they're cliffs or coasts.
- **Black webbing:** a noise mask multiplied over lights or colour leaves a dark net.
- **Reticles:** rings and spokes around a light read as targeting marks. A town at night is a
  bright core, street lights thinning outward, and a road or two as dotted lines.
- **Accent colours read as damage** from orbit (rust, burns, clearings).
- **Many separate systems layered** that don't join up. One coherent field driving several
  features beats several independent ones.
- **Even-toned patches** read as farm fields.
- **Bright thread webs** (Mystra): `billow` (`1 - |noise|`) at fine scale, or thresholded,
  peaks along the noise's zero-crossings and draws a net of thin bright threads over cloud.
  Use plain fbm for the fine scales.
- **Honeycomb or chicken wire** (Mystra): Worley cells in cloud read as a net up close.
- **Noise too weak to matter:** `fbm` returns roughly ±0.17 (standard deviation), not ±1.
  An amplitude chosen as if it were ±1 moves a border or coast by a sixth of what was meant,
  and shapes stay ovals and straight lines. Measure what the noise actually does.
- **Too regular placement:** things evenly spaced, or all the same size, look placed.

## Fresh-eyes review

Before showing the user, have a separate reviewer (a fresh agent with no stake in the work)
look at the inspector images and the flat map, with this file and the lore brief. Ask it to
list everything a picky viewer would notice, most noticeable first, with the image and spot
for each, and to say what the real analogue looks like. Then fix, or note why not. Include in-app screenshots if the planet is wired into the lab:
the real renderer's lighting and cloud colour change how things read. (A subagent can't start
another agent; if you're one, say so in your report and whoever integrates runs the review.)

## Shared code

`planetgen.py`, `clouds.py`, everything in `web/` and the docs are shared by every planet. When
several planets are being built in parallel, a planet's builder touches only its own script
and output folder, and writes down any change it needs to shared code (with the reason)
instead of making it. Whoever integrates makes those changes once.

## Hand-off report

When a planet is ready for review, report:

- the files written, and the maps folder to inspect;
- what each feature is and where the lore says so, and every guess made;
- the answers to the questions above;
- what the inspector flagged and what you did about each;
- what you couldn't fix or aren't sure of;
- anything needed from shared code or the app (`bodies.ts` settings: radius, glow,
  atmosphere, clouds, twilight).

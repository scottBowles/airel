# Asset assessment: suns, planets and moons

Compares each body's lore (production DB `Place` description + notes, and the "On the
Planets" primer log) and its reference images (the `imageIds` on its `Place`, on
Cloudinary) with the current models from `solars/static/models`. Written Nov 2026.

**The reference images are inspiration, not canon.** The user picked them because they had
the right character (mood, palette, feel). They don't show the geography in the
descriptions. Where an image and the text disagree, the text wins.

The existing `.glb`s (Blender and Sketchfab) stay as they are. New work goes in new files.

## Summary

| Body | Lore in short | Reference image | Current model | Verdict |
| --- | --- | --- | --- | --- |
| The Yellow Sun | "Yellow refining fire, with the heat of purity" | Golden-orange sun with flares | Sketchfab `YellowStar`: flat pale yellow, no glow | **Replace** with a shader sun: hot gold-white, steady, purer |
| The Red Sun | "Red wild fire, burning with the heat of passion" | Roiling red-orange, big prominence | Sketchfab `RedSun`: peach/salmon, calm | **Replace** with a shader sun: deep red, turbulent, flares |
| Magmus | Fire world; lava flows and geysers; habitable underworld; 12 Solidlands, 3 Wells (two polar caps, an equatorial archipelago) | Dark crust with glowing lava cracks and rivers | Orange/black blotches, evenly bright, no glow | **Rework**: dark basalt, emissive lava veins visible on the night side, authored landmarks |
| Felucia | Humid, colourful jungle; wildlands; hopeful | Bright lush green, white clouds, little ocean | Green patches on a dark-blue ocean | **Rework**: mostly jungle, vivid, cloudy, small seas |
| Terran | Planet-sized metropolis, "Chicago across a planet", parks, Senate, Champion City | City-light grids and circular arcologies covering the planet | None (the `Terran.glb` from the bake test is Earth-like and wrong) | **New**: urban grey surface, emissive city grid, a few parks and seas |
| Hyang Wan | High-tech water planet, always raining; islands (Mulgogi, Hatatori) | Deep teal ocean with swirls, island lights; second image has a ring | Mostly dark ocean, a few green islands | **Rework**: teal swirling ocean, heavy rain clouds, lit islands. No ring (not canon) |
| Gonhirrim | Gas giant, perpetual storms, seven inhabited moons; "the eighth moon" is its core | Pink/orange/yellow banded giant with moons; a diagram of seven moons in a ring | None | **New**: banded gas giant shader with a storm, plus seven moons |
| Gonhirrim's 7 moons | Broadly similar but each with its own character. Broadbeam (Gliten, air), Firebeard (Tyronóë, dreams), Blacklock (Moronóë, hearth), Durinfol (Thiton, water/life; capital Erebôr), Ironfist (Mazoë, justice), Stiffbeard (Yafel, knowledge), Stonefoot (Glitonea, earth). Dwarven mining moons | Only the ring diagram | None | **New**: one shared rocky, mined-moon base; per-moon variation drawn from its god |
| Hielo | Frozen, largely uninhabitable; "not a planet": it sits **in the asteroid belt**, which runs between the suns, a little nearer the Yellow Sun | Grey-white cratered body | Grey/white icy | **Keep**, maybe more craters. Needs an asteroid belt to sit in |
| Mystra | "The pink Dagobah": swampy, mystic, pilgrimage site | Vivid pink planet with white clouds | Olive-green (and `Mystra2` is similar) | **Rework**: pink swamp world, misty clouds |
| Genussa | "Vegas of planets", sleazy metropolis, "Nega-Terran"; four quadrants G1–G4 | Dark planet webbed with orange city lights | Blue ocean with green/tan continents | **New**: dark city world with neon light, four quadrants visible |
| Janus | Half light, half dark, a little Mezzolux; dark east, light west (from the butte description) | Lit orange/rust half, black other half | Tan/blue noise, no halves | **Rework**: tidally locked to the Red Sun, so the sun's light makes the halves. The surface should also differ by side (see below) |
| Didymus | Twin planets, broken from one; lots of sand, few waters | Two small bodies, one pale banded, one light blue | None | **New**: two small desert bodies with fractured faces, orbiting each other. Sand per the text; the image is only for mood |
| Chromium | "The dark planet." No one has gone there; dragons are said to live there. Its delegates used to come to interplanetary meetings, then stopped. Figure-eight orbit around both suns | None | None (red sphere in `solars`) | **New**: near-black and unknown (see below) |

Also needed, not bodies: **the crew's ship** (the Kontularien) for the fly-through, and
**an asteroid belt** (where Hielo sits).

## Notes on the current Blender models

- Several share the same continent shapes in different colours (Janus, Genussa, Mystra and
  Hyang Wan): one noise setup, recoloured. None has authored geography.
- They're 1024 px textures: fine from orbit, soft close up.
- `Janus` / `Janus2`, `Mystra` / `Mystra2` are two takes each. Neither take matches the lore.
- Their UV layout hasn't been checked. For pins on a map they need a known lat/long
  layout (see below).

## User's answers (Nov 2026)

- **Hielo** is in the asteroid belt. The belt runs between the two suns, a little nearer the
  Yellow Sun. Model the belt as instanced rocks along an arc, with Hielo as its largest body.
- **Didymus**: the description is canon (sand, few waters). The image was only the best one
  found showing two close planets.
- **Hyang Wan**: no ring unless the lore mentions one; it doesn't.
- **Chromium** is "the dark planet". Nobody has been there; lore says dragons live there.
  Not much description exists. Plan: keep it mysterious. A near-black, low-reflectance
  world under dark storm cloud, a faint ember glow in fissures and the odd flash of
  lightning. Its display reads "uncharted"; it has no places in the DB.
- **Gonhirrim's moons**: broadly similar, with enough difference for character. Plan:
  one shared mined-rock base (mining scars, lit settlements) varied by each moon's god:
  - Broadbeam (Gliten, air/balance): hazy thin atmosphere
  - Firebeard (Tyronóë, dreams/psyche): violet tint
  - Blacklock (Moronóë, wisdom/hearth): warm-lit settlements
  - Durinfol (Thiton, water/life): ice and water, some green; capital Erebôr
  - Ironfist (Mazoë, justice/courage): iron-red rock
  - Stiffbeard (Yafel, knowledge/temperance): pale stone
  - Stonefoot (Glitonea, earth/law): heavily cratered
- **Janus**: the user let lighting and the tidal lock make the halves. Open to whatever
  looks best. Recommended: keep lighting doing day and night, and also vary the surface
  by side. Day side scorched and arid; night side dark rock and ice with faint
  settlement lights (people live there); the Mezzolux a habitable band at the terminator.
  With lighting alone, the dark half is one black disc with nothing to see or click.

## System layout (user's sketch)

[`system-sketch.jpg`](system-sketch.jpg) is the user's rough hand-drawn map, top-down:

- **Yellow Sun** upper left, drawn small; **Red Sun** lower right, drawn much larger.
- **The asteroid belt** is a long arc between them, passing nearer the Yellow Sun.
- Planets are numbered 1–10, with a legend: 1 Magmus, 2 Felucia, 3 Terran, 4 Hyang Wan,
  5 Gonhirrim, 6 Hielo, then 7–10 (the legend reads like Mystra?, Genussa, Janus,
  Didymus).
- Coloured diamonds, with a second legend: **Vostok, Galileo, Tiberius, Lizhi, Aryabhata**.
  They sit along lines between the suns. What they are (stations? relays?) is unconfirmed.

It's rough, so treat it as relative placement, not exact positions.

## Specific geography: authored control maps, noise for detail

Descriptions name real features: Vale of Cleaveland "nested between two mountains",
Magmus's polar Wells and equatorial archipelago, Ymir the tallest mountain, Kenaz a raised
crater lake, Hyang Wan's islands, the butte in Janus's Mezzolux. Pure noise can't put those
where the story says. The plan:

1. **Each planet gets a feature spec**: a small data file listing features with type,
   lat/long, size and shape: `mountain_range`, `valley`, `lake`, `island`,
   `archipelago`, `polar_cap`, `crater`, `lava_river`, `city`, `terminator_band`. An agent
   writes it from the place descriptions; the DM corrects it.
2. **The bake script turns the spec into control masks** (height, land/water, biome,
   emissive) in lat/long layout. Noise only adds detail within those masks, so mountains
   are where the spec says and look natural up close.
3. **Place pins come from the same spec**, so they agree with the terrain by construction:
   "Vale of Cleaveland" sits between the two ridges that were drawn for it.
4. **Where the lore says nothing, noise decides**, seeded per planet so it's stable.
5. **Scale has limits.** At 4k, a texel on an Earth-sized planet is about 10 km. Continents,
   caps, archipelagos and big ranges read from orbit; a lake or a town doesn't. Fine detail
   belongs on the ship's display (a zoomed regional map) rather than on the globe.

Storage: place lat/long lives in the DB (the DM edits it per place). The feature specs and
rendering settings live in code with the bake scripts, since they're tied to the textures
and there won't be new planets.

Some lore is dynamic: Magmus's capital "moves with the lava", so its pin could drift.

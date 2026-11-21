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
| Hyang Wan | High-tech water planet, always raining; islands (Mulgogi, Hatatori) | Deep teal ocean with swirls, island lights; second image has a ring | Mostly dark ocean, a few green islands | **Rework**: teal swirling ocean, heavy rain clouds, lit islands. (The ring is just from an inspiration image) |
| Gonhirrim | Gas giant, perpetual storms, seven inhabited moons; "the eighth moon" is its core | Pink/orange/yellow banded giant with moons; a diagram of seven moons in a ring | None | **New**: banded gas giant shader with a storm, plus seven moons |
| Gonhirrim's 7 moons | Broadbeam (Gliten, air), Firebeard (Tyronóë, dreams), Blacklock (Moronóë, hearth), Durinfol (Thiton, water/life; capital Erebôr), Ironfist (Mazoë, justice), Stiffbeard (Yafel, knowledge), Stonefoot (Glitonea, earth). Dwarven mining moons | Only the ring diagram | None | **New**: one rocky, mined moon base, varied per moon's god |
| Hielo | Frozen, largely uninhabitable; "not a planet", in the asteroid belt | Grey-white cratered body | Grey/white icy | **Keep**, maybe more craters. Needs an asteroid belt to sit in |
| Mystra | "The pink Dagobah": swampy, mystic, pilgrimage site | Vivid pink planet with white clouds | Olive-green (and `Mystra2` is similar) | **Rework**: pink swamp world, misty clouds |
| Genussa | "Vegas of planets", sleazy metropolis, "Nega-Terran"; four quadrants G1–G4 | Dark planet webbed with orange city lights | Blue ocean with green/tan continents | **New**: dark city world with neon light, four quadrants visible |
| Janus | Half light, half dark, a little Mezzolux; dark east, light west (from the butte description) | Lit orange/rust half, black other half | Tan/blue noise, no halves | **Rework**: tidally locked; scorched light side, black/icy dark side, Mezzolux band at the terminator |
| Didymus | Twin planets, broken from one; lots of sand, few waters | Two small bodies, one pale banded, one light blue | None | **New**: two small desert bodies with fractured faces, orbiting each other. Sand per the text; the image is only for mood |
| Chromium | Planet of Dragons; no one returns; figure-eight orbit around both suns | None | None (red sphere in `solars`) | **New**, design open: ask the user |

Also needed, not bodies: **the crew's ship** (the Kontularien) for the fly-through, and
**an asteroid belt** (where Hielo sits).

## Notes on the current Blender models

- Several share the same continent shapes in different colours (Janus, Genussa, Mystra and
  Hyang Wan): one noise setup, recoloured. None has authored geography.
- They're 1024 px textures: fine from orbit, soft close up.
- `Janus` / `Janus2`, `Mystra` / `Mystra2` are two takes each. Neither take matches the lore.
- Their UV layout hasn't been checked. For pins on a map they need a known lat/long
  layout (see below).

## Lore questions for the user

1. **Hielo**: DB parent is the Yellow Sun, notes say it's in the asteroid belt and "not a
   planet", and Gonhirrim's notes mention it near the moons. Where does it go?
2. **Chromium**: no image. Dragons, mystery, figure-eight orbit. Any picture in mind?
3. **Gonhirrim's moons**: are they distinct worlds (each themed by its god), or broadly
   alike mining moons?

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

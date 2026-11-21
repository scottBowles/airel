# Chromium — lore brief

DB `Place` **Chromium** `UGxhY2U6Mw==` (PLANET, **no parent**), description "Planet of Dragons". No reference image. No child places.
The user's ruling (assets.md) is "the dark planet": nobody has been there. Keep it mysterious and show "uncharted".

## 1. Canon summary

- "Planet of the Dragons. Unheard from, and anyone who goes there doesn't come back." (*On the Planets*, 2013-01-01, "Both Suns:" section; same text in the Chromium notes)
- "They have seats in the Senate, but no one ever comes. There was one instance where a delegate from Chromium appeared in the Senate in the early stages to assert that they don't want any part in this, then she turned into a Dragon and flew away." (same). The Senate is on Terran.
- "It has a figure-eight orbit around the two suns. It has the opportunity." The sentence is cut off in both the primer and the DB.
- **The Halls of the Pantheon are on Chromium.** In a vision of the Pantheon Wars: "the pantheon gathers on Chromium where the halls of the Pantheon are", and the gods vote there on wiping out all mortals. Gliten's compromise sends each god to sleep "encapsulated in one of the planets" (*Iconic Conflicts*, 2021-01-18).
- Bruno's song *Into the Black* "mentions Chromium as this land of mystery" (*Into the Black*, 2021-05-10).
- Race *Dragon*: "Mysterious Denizens of Chromium".
- Dragons met elsewhere (not said to come from Chromium):
  - Raltak/Raltach, a 20-ft "skeleton dragon whose eye-sockets glow a familiar shade of green", sleeping in a Magmus mountain cave. He flies off "straight up" to meet the party at the arena in Champion City on Terran (*Raltak's Promise*, 2024-10-21).
  - An 8-ft ancient dragon skull forge-anvil on Magmus (*Forge Foraging and Forigins*, 2024-08-26).
  - "I miss when dragons were dragons" (*Raltak's Promise*).

## 2. Visual cues

Stated: none at all. There's no colour, surface, size or moon in any source.

Inferred / design (from the user's plan):
- **Surface:** near-black, low-reflectance world under dark storm cloud.
- **Lights and night side:** faint ember glow in fissures (dragon fire, or the Halls), occasional lightning.
- **Name hint (inference only):** "Chromium" may nod to chrome or to D&D *chromatic* dragons. A faint iridescent or metallic sheen at the cloud tops or the limb could carry it without breaking "dark".
- **Size:** unknown. Treat it as mid-size.
- **Orbit:**
  - A figure-eight around both suns (stated). The `solars` prototype already does this (`getFigureEightPositionForAngle`).
  - Its crossover point lies between the suns, where the belt runs, so it must pass through, over or under the belt (inference).
  - It isn't in the sketch: the legend's 1–10 has no Chromium.

## 3. Places

| Name | Type | DB id | Parent | Geographic clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
|---|---|---|---|---|---|---|---|
| Chromium | PLANET | `UGxhY2U6Mw==` | (none) | "figure-eight orbit around the two suns" | — | — | — |
| Halls of the Pantheon | — | — | Chromium | "the pantheon gathers on Chromium where the halls of the Pantheon are" (vision) | 0, 0 | guess | No clue. Equator, front face, so it reads as the one landmark. Could stay hidden ("uncharted"). |

## 4. Feature-spec draft

| Feature | Type | Centre lat, lon | Size (deg) | Source / note |
|---|---|---|---|---|
| Dark basalt base | base | all | — | User plan: albedo ~0.04 |
| Storm cloud deck | clouds | global | ~70% cover, slow | User plan |
| Ember fissures | lava_river (dim emissive) | scattered | thin, 5–30° long | User plan; dragons (inference) |
| Lightning | flash (shader) | random | — | User plan |
| Halls of the Pantheon | city (faint glow) or hidden | 0, 0 | 1–2° | *Iconic Conflicts* vision. Optional. |
| Iridescent sheen | atmosphere tint | limb | — | Inference from the name. Optional. |

## 5. Contradictions and open questions for the DM

1. **"It has the opportunity"…** to do what? The sentence is cut off. If it means something like *to visit both suns' worlds* or *to align with something*, the orbit animation should show it.
2. **Orbit geometry:** how big is the figure-eight relative to the planets' orbits? Does it pass between the suns through the asteroid belt, or tilted out of the plane? What's its period relative to the planets?
3. **Halls of the Pantheon:** are they really on Chromium in the present day, or only in the vision? Should the display show them or keep "uncharted"?
4. **Look:** any colour, sheen or moons you picture? Is "dark" literal (dark surface) or reputational (unknown)?
5. **Raltak:** is he a Chromium dragon? Does Chromium relate to the dragon skulls and bones on Magmus?
6. **Senate:** does Chromium still hold empty seats? This matters for any Senate scene on Terran.

## 6. Sources read

- DB: place Chromium, race Dragon, item Soul Blade ("Forged out of fossilized dragon eyes"), artifact Dragon skull forge-anvil. assets.md rulings. `solars` README notes on `Chromium.svelte`.
- Logs: *On the Planets* (2013-01-01), *Iconic Conflicts* (2021-01-18), *Into the Black* (2021-05-10), *Forge Foraging and Forigins* (2024-08-26), *Disturbed Slumber* (2024-09-09), *Raltak's Promise* (2024-10-21), *Bargain in the Ash Pit* (2025-03-27).
- All 152 logs were searched for Chromium and dragon. Only the primer, *Iconic Conflicts* and *Into the Black* name Chromium.

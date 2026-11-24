# Hielo and the asteroid belt — lore brief

DB `Place` **Hielo** `UGxhY2U6MTY=` (PLANET, parent The Yellow Sun), description "The Ice Planet".
The party's visit to Hielo happened **before the logs start** (2018-08), so there's no on-site description. What we know comes from later references and DB entities.

## 1. Canon summary

- "Not a planet (messed up, right?). In the asteroid belt, rather than orbiting a sun. Frozen, largely uninhabitable." (Hielo notes; *On the Planets*, 2013-01-01: "Hielo-- Not a planet. Frozen, largely uninhabitable.")
- "Hielo is in fact the Pluto of this world. It is an oversized asteroid. But if you wanted to categorize the 'planets', like the map on Thorin's rocket that once was a tower, it didn't include Hielo." (DM ruling, *Shellback Ceremony*, 2019-04-11)
- "…some are uninhabited except like Hielo, where there are some natural creatures, but no people." (*On the Planets*, Gonhirrim section)
- "Between the suns, he couldn't be on a planet with an orbit. He could be on the asteroid belt, which includes Hielo." Including Hielo among the worlds is "politically incorrect" (*Into the Black*, 2021-05-10).
- The user's ruling (assets.md): the belt runs between the two suns, a little nearer the Yellow Sun, and Hielo is its largest body.
- What was on Hielo (all from references back to the pre-log visit):
  - **Ice caves**: the Whidmore sign "was found on the energy supply canisters in the ice caves" (association *Whidmore Corporation*).
  - **A cave**: "the picture we found among the Roper's effects in the cave on Hielo" (*Exhuming Nora Omundsen*, 2019-06-20; artifact *The Locket*).
  - **Hammer and Kiln**: "Dwarven corporation who was mixing Hiobium on Hielo" (association).
  - **Bode Augur**: "discovered in self-exile on the ice rock of Hielo" (character); "exiled himself to Hielo" (*Shadows of Betrayal*, 2022-08-22); "We found him on Hielo" (*Searching Dhund Hal Ka's Backpack*, 2022-08-01).
  - **Scientists died there.** The party is "wanted for murder on Hielo" (*Shadows of Betrayal*). "Our suspected ties to the death of scientists on Hielo" (*WINEPRESS*, 2020-09-14). "Daryo's talking about Hielo. Wanted for questioning." (*Off the Grid*, 2019-08-01)
  - **Werewolves**: "the werewolves on Hielo" (*Monkey Lips at the Orange Star*, 2022-11-21). Keiko, "Met on Hielo… Izar suspects she's a werewolf" (character).
  - **Others**: "what Heath (with the) ledger had on Hielo" (2018-10-02 log); character *Hielo's Monster* (no text).
- **Asteroid belt in the logs:** fleeing Hyang Wan, Izar asks about evading "through the asteroid belt, but Atchi says we're a couple hours from there, and going through the gates would be faster anyway" (*Space Battle*, 2019-04-25).

## 2. Visual cues

Stated:
- Frozen ice body ("The Ice Planet", "the ice rock").
- "Pluto of this world", an "oversized asteroid".
- Has ice caves and at least one cave.
- Small industrial and scientific presence (Hammer and Kiln Hiobium works, Whidmore energy canisters, scientists), plus wild creatures and werewolves. No native people.

Inferred:
- **Surface:** grey-white and bluish ice, heavily cratered like an asteroid.
- **Pluto look:** the reference image (`dnd/celslfuppdaeh39o9zfq`, inspiration only) is a Pluto-like world with a smooth bright plain and rough dark terrain. A smooth pale plain against cratered darker ground would fit.
- **Atmosphere:** none, or a faint haze. No clouds.
- **Night side:** almost black, with a few tiny lights at a mining or research site.
- **Size:** the largest belt body, much smaller than the planets. The sketch draws it about the size of Terran, which is too big.
- **Shape:** round enough to be "the Pluto", so a near-sphere with low-relief lumps.
- **Moons:** none stated.
- **Orbit:** inside the belt, which is not "a planet with an orbit" (see the questions).

Belt (inferred from the sketch and the user's ruling):
- A long arc of rocks between the suns. In the sketch it curves around the Yellow Sun side: a circle fit puts its centre beyond the Yellow Sun, and it passes ~40% of the sun-to-sun distance from the Yellow Sun versus ~55% from the Red.
- Gonhirrim sits on its inner edge. Hielo sits about midway along the sun-to-sun line.
- Dense enough to hide a ship in ("evade through the asteroid belt").

## 3. Places

None of these have DB rows except Hielo. All are from references to the pre-log visit. Positions are all `guess`.

| Name | Type | DB id | Parent | Geographic clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
|---|---|---|---|---|---|---|---|
| Hielo | PLANET | `UGxhY2U6MTY=` | The Yellow Sun (notes say: in the belt) | "In the asteroid belt, rather than orbiting a sun" | — | — | — |
| The ice caves (Whidmore canisters) | — | — | Hielo | "energy supply canisters in the ice caves" | 18, −35 | guess | Grouped with the Roper's cave as one cave system in rough terrain. |
| The Roper's cave | — | — | Hielo | "the Roper's effects in the cave on Hielo" | 15, −40 | guess | Probably part of the ice caves. Ask the DM. |
| Hammer and Kiln Hiobium works | — | — | Hielo | "Dwarven corporation who was mixing Hiobium on Hielo" | 5, 10 | guess | Industrial site near the caves. It gives the night side its only lights. |
| Science station (where scientists died) | — | — | Hielo | "the death of scientists on Hielo" | −10, 60 | guess | Separate from the mine. Pure placement. |
| Bode Augur's exile camp | — | — | Hielo | "self-exile on the ice rock of Hielo" | 50, −90 | guess | Remote from the other sites. |

## 4. Feature-spec draft

| Feature | Type | Centre lat, lon | Size (deg) | Source / note |
|---|---|---|---|---|
| Ice crust | base | all | — | "Frozen"; grey-white to pale blue |
| Crater field | crater | global | many, 1–25° | "oversized asteroid" (inference) |
| Bright smooth ice plain | plain | 10, 175 | ~45 × 35° | Inference from "the Pluto of this world" and the reference image (heart-like plain). Optional. |
| Dark rough highlands | terrain | −20, −120 | ~60° | Contrast for the plain (inference) |
| Ice-cave field | cave mouths / chasm | 16, −38 | ~8° | Whidmore canisters and the Roper's cave |
| Hiobium works | city (tiny, emissive) | 5, 10 | 1° | Hammer and Kiln |
| Science station | city (tiny, emissive) | −10, 60 | 0.5° | Dead scientists |
| Polar frost | polar_cap | ±75 | soft | Guess |

Belt (for the instancer, not a texture):

| Item | Proposal | Conf. |
|---|---|---|
| Path | Arc between the suns, centred on the Yellow Sun side. The sketch's circle fit gives radius ≈ 0.74 × sun–sun distance, centre ≈ 0.35 × sun–sun distance beyond the Yellow Sun. | layout (sketch) |
| Nearest point to the Yellow Sun | ~0.4 × sun–sun distance; to the Red Sun ~0.54 | layout |
| Rocks | Thousands of grey/brown instanced rocks plus scattered icy ones. Denser near Hielo. | guess |
| Hielo | The largest body, near where the arc crosses the line between the suns, slightly toward the Yellow Sun | lore + layout |
| Gonhirrim | Sits just inside the belt (sketch) | layout |

## 5. Contradictions and open questions for the DM

1. **What does the belt orbit?** The DB parent is the Yellow Sun, but the notes say "rather than orbiting a sun", and the Bruno song says the belt isn't "a planet with an orbit". Should the belt (and Hielo) orbit the Yellow Sun, both suns, or stay fixed?
2. **People on Hielo?** "Some natural creatures, but no people" conflicts with Hammer and Kiln, the scientists, Keiko and the werewolves. Are these just outposts? Should the night side show any lights?
3. **The ice caves:** are they the same place as "the cave" with the Roper? Where are they relative to the Hiobium works?
4. **Shape:** round Pluto-like sphere, or a lumpy oversized asteroid?
5. **Hiobium:** what is it, and does mining scar the surface (pits, glow)?
6. **Hielo's Monster:** what is it, and does it have a lair worth pinning?
7. **The belt's look:** rocky, icy, or mixed? Is it a thin arc or a wide band? Does it surround a sun, or is it only an arc between the suns?
8. **DB links:** the DB lists Hielo in *Finding the Freelanders*, *Zombie Zip Tie*, *Echoes of the Iron Castle*, *Quarrel's Cargo*, *Mirages Unveiled* and *A Worthy Battle for the Dead*, but none of those logs mention Hielo. They're probably AI mis-links.

## 6. Sources read

- DB: places Hielo and The Yellow Sun. Associations Whidmore Corporation and Hammer and Kiln. Characters Bode Augur, Keiko and Hielo's Monster. Artifact The Locket. Reference image Hielo_0. The user's sketch and assets.md rulings.
- Logs:
  - *On the Planets* (2013-01-01)
  - log of 2018-10-02 (*The Codex and the Director's Office*)
  - *Shellback Ceremony* (2019-04-11)
  - *Space Battle* (2019-04-25)
  - *Exhuming Nora Omundsen* (2019-06-20)
  - *Off the Grid* (2019-08-01)
  - *The Urn and the Horse Riders* (2020-06-27)
  - *WINEPRESS* (2020-09-14)
  - *Into the Black* (2021-05-10)
  - *Searching Dhund Hal Ka's Backpack* (2022-08-01)
  - *Shadows of Betrayal* (2022-08-22)
  - *Monkey Lips at the Orange Star* (2022-11-21)
- All 152 logs were searched for Hielo, asteroid, belt, ice, frozen, cave, Roper and werewolf.

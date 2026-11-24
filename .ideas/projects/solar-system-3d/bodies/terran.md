# Terran — lore brief

Yellow Sun planet. DB `Place` **Terran** `UGxhY2U6Ng==` (PLANET, parent The Yellow Sun), description "Planet-Sized Metropolis".
The canon has almost no geography for Terran. Every position below is a `guess` except where it's tied to Champion City.

## 1. Canon summary

- "Centralized planet, probably most populated." "What you get when you mix Coruscant with Caprica. What you get when you mix metropolis on top of metropolis." (Terran notes = *On the Planets*, 2013-01-01)
- "They *have* a parks initiative, but it's like the city of Chicago spread across a whole planet." (same)
- "This is the Whidmore Corp. playground for developing terraforming" (same). Charles Whidmore is "a wealthy Terranite who got into terraforming" (association *Whidmore Corporation*; character *Charles Whidmore*: "Terran who began career as a pioneer in interplanetary Real Estate").
- "Champion City--expect like Demolition Man above world" / "The Senate is here." / "The seat is power." (same)
- "No unrest is allowed. Basically police state. Like the Novacore of Xandar from Guardians of the Galaxy." "Super high-tech. Really into that. Progress." "America in the fifties with technology." "Provide much of the police force of the world." (same)
- Each planet has 4–5 senators (*WINEPRESS*, 2020-09-14). Chromium has Senate seats "but no one ever comes"; its one delegate "turned into a Dragon and flew away" (Chromium notes).
- Champion City has **an arena**: Raltak (a dragon) "The orb you know as Terran. I'll find you there. Seek Champion City. I'll meet you at the arena… Champion City. The Arena." (*Raltak's Promise*, 2024-10-21); "(Raltach is waiting for us in an arena in Champion City on Terran)" (*Bargain in the Ash Pit*, 2025-03-27). He leaves Magmus by flying "straight up".
- Dhund Hal Ka: "The gladiatorial arena was on Terran for my branch. The same gladiatorial arena earned us the sarcophagus of Mazoe on Terran." Temples "move" per branch (*Searching Dhund Hal Ka's Backpack*, 2022-08-01). Possibly the same arena.
- Champion City is a big concert venue: Bruno's concert "on Terran" (*Summary going in*, 2018-08-06); "I thought he was playing Champion City" (*Espresso at the Bank*, 2022-09-05); "when he didn't show to Champion City" (*Monkey Lips at the Orange Star*, 2022-11-21).
- Other passing mentions: Daryo keeps one of three bank accounts "on Terran" (*The Naming of Kozmo*, 2021-06-21); card heraldry "from a kingdom that's nonexistent on Terran now and hasn't existed in about 200 years" (*The Blind Seer*, 2022-05-09), so Terran once had kingdoms; Wren: "I'm only here on Terran, holding you in this place" (*Echoes of the Iron Castle*, 2023-08-14).
- Races: "predominantly human"; many Yuan-ti and Hyang-wanese (races *Human*, *Yuan-ti*, *Hyang-wanese*).

## 2. Visual cues

Stated:
- A planet-wide city ("metropolis on top of metropolis"), with parks, on a Chicago-like plan, super high-tech.
- Champion City sits "above world", like Demolition Man's San Angeles.
- A terraforming testbed for Whidmore.
- Reference image (inspiration only, `dnd/a7yw9jdffzl2krf8yqic`): dark globe covered in warm-gold city-light grids and circular arcology rings, thin blue atmosphere rim, light cloud.

Inferred:
- **Surface:** grey/charcoal urban fabric on nearly all land. Chicago means an orthogonal street grid cut by diagonal avenues, plus a lakefront.
- **Night side:** dense warm-gold/white lights, the strongest of any planet. The fifties and Xandar references suggest clean, gleaming, retro-futurist.
- **Parks and seas:** the parks initiative gives regular green squares and a chain of green around the capital. Caprica (as opposed to Coruscant) suggests some seas survive. The asset plan already says "a few parks and seas".
- **Under-city:** "above world" implies a darker underworld. It isn't visible from orbit, so at most a dimmer ring around Champion City.
- **Terraforming:** Whidmore test zones as a patchwork of unlike biomes (green, desert, ice squares) breaking the grid.
- **Atmosphere and clouds:** Earth-like blue rim with sparse cloud (from the reference image).
- **Size, moons, orbit:**
  - Size is unstated. "Most populated" suggests at least Earth-class.
  - No moon in the text. The user's sketch draws #3 (Terran) teal with a tall edge-on ellipse (a ring or a moon's orbit) and one small moon. See the open questions.
  - Orbit: the Yellow Sun, third out (sketch legend order).

## 3. Places

| Name | Type | DB id | Parent | Geographic clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
|---|---|---|---|---|---|---|---|
| Champion City | (none) | `UGxhY2U6OTg=` | (none; should be Terran) | "Champion City--expect like Demolition Man above world"; "Seek Champion City. I'll meet you at the arena." | 42, 0 | guess | Capital hub gets the reference meridian. Lat 42° nods to Chicago. |
| The Senate | — | — | Terran | "The Senate is here. The seat is power." | 42.3, 0.6 | guess | Placed in Champion City's core. Lore only says "on Terran". |
| The Arena (Champion City) | — | — | Champion City | "Champion City. The Arena."; "an arena in Champion City on Terran" | 41.6, 1.4 | layout | Lore puts it in Champion City. The offset within the city is arbitrary. |
| Gladiatorial arena of Mazoë (previous branch) | — | — | Terran | "The gladiatorial arena was on Terran for my branch" | = The Arena | guess | Probably the same arena. Ask the DM. |
| Whidmore terraforming testbed | — | — | Terran | "Whidmore Corp. playground for developing terraforming" | −20, 120 | guess | Far from the capital so it reads as a separate region on the globe. |

## 4. Feature-spec draft

| Feature | Type | Centre lat, lon | Size (deg) | Source / note |
|---|---|---|---|---|
| Planet-wide urban fabric | base | all land | ~80% of surface | "metropolis on top of metropolis" |
| Street grid | city (pattern) | global | cell ~1–2°, diagonals every ~15° | "Chicago spread across a whole planet" (inference) |
| Night lights | emissive | global, weighted by density | — | "probably most populated"; reference image |
| Champion City megahub | city | 42, 0 | r ≈ 6°, radial avenues out to 15° | Champion City notes. Brightest node on the night side. |
| Senate plaza | city (landmark) | 42.3, 0.6 | 0.6° bright ring | "The Senate is here" |
| Arena | city (landmark) | 41.6, 1.4 | 0.4° ring | Raltak's Promise |
| Lakefront inland sea | lake | 40, 11 | 14 × 7° | Inference from "Chicago". The shore is a park strip. |
| Seas (2–3) | ocean | −15, −70; 10, 150; −48, 55 | 30×18°, 24×14°, 18×10° | Inference (Caprica, "seas" in assets.md). The coasts are built up to the waterline. |
| Capital park chain | park | ring around 42, 0 | 8 patches of 1–2° at r ≈ 9° | "parks initiative" |
| Grid parks | park | every ~15° grid node | ~1° squares | "parks initiative" |
| Whidmore terraforming testbed | biome patchwork | −20, 120 | 20 × 14° of mixed squares | "playground for developing terraforming" |
| Transit arteries | line (emissive) | great circles linking the hubs | 0.2° wide | Inference ("super high-tech") |
| Poles | polar_cap | ±80 | edge ±72 | Guess: built over, dimmer lights, thin ice. Ask the DM. |
| Clouds | clouds | global | sparse, ~20% cover | Reference image |

## 5. Contradictions and open questions for the DM

1. **Seas or none?** Is Terran an all-city Coruscant, or does it keep oceans and lakes (Caprica)? This changes the whole texture.
2. **Moon or ring?** The sketch gives #3 an edge-on ellipse and a small moon. Does Terran have a moon, a ring, or an orbital ring city?
3. **Where are the Senate and the Arena?** Are both inside Champion City, or is the Senate elsewhere?
4. **Is the Arena Mazoë's arena?** Is Champion City's arena the gladiatorial arena where the previous branch won Mazoë's sarcophagus?
5. **"Above world":** is Champion City literally elevated (a sky-city or towers over an under-city)? If so, should it be modelled as raised geometry or cloud-piercing lights?
6. **Whidmore:** is there a named Whidmore HQ or terraforming site on Terran? Charles Whidmore's "headquarters"/"home base" is mentioned while the party is on Genussa (*Espresso at the Bank*), so it's unclear which planet it's on.
7. **Poles:** urban, icy, or parkland?
8. **DB fixes:** Champion City has no `placeType` and no parent. Should it be TOWN under Terran?

## 6. Sources read

- DB places: Terran, Champion City, The Yellow Sun. Associations: Whidmore Corporation. Characters: Charles Whidmore. Races: Human, Yuan-ti, Hyang-wanese. Reference image Terran_0.
- Logs:
  - *On the Planets* (2013-01-01)
  - *Summary going in* (2018-08-06, 2018-08-14)
  - *WINEPRESS* (2020-09-14)
  - *The Naming of Kozmo* (2021-06-21)
  - *The Blind Seer* (2022-05-09)
  - *Searching Dhund Hal Ka's Backpack* (2022-08-01)
  - *Espresso at the Bank* (2022-09-05)
  - *Monkey Lips at the Orange Star* (2022-11-21)
  - *Echoes of the Iron Castle* (2023-08-14)
  - *Raltak's Promise* (2024-10-21)
  - *Bargain in the Ash Pit* (2025-03-27)
- All 152 logs were searched for Terran, Champion City, Senate and Whidmore. Only the logs above mention Terran.

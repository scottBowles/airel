# Genussa: lore brief for texture and pins

Sources: production DB (`places.json`, Nov 2026), "On the Planets" primer, and every session log that
mentions Genussa or its places (listed at the end). Quotes are verbatim; "log" means a session log,
cited as *Title (date)*.

## 1. Canon summary

- **"Vegas of Planets"** (DB description). Notes / primer: "Vegas." "Sleazy drug-ridden metropolis."
  "Nega-Terran." Name from "Genussa", "the embodiment of pleasure and grandiose feelings". Chaotic
  Neutral / Chaotic Evil; "the planet most likely to institute something like the purge".
- **Orbits the Red Sun** (DB parent). It has a normal day: "The Red Sun begins to set" (*Manticore
  Green*, 2019-05-16); "We do get to see the Red Sun set" from the lighthouse (*Monkey Lips at the Orange
  Star*, 2022-11-21). So it spins and is **not** tidally locked.
- **Holds the hub of the ansible network**: "They control the hub for it" (DB). The hub's location is not given.
- **The city covers everything, and it is tall**: Meagel University is "built of many vaunting skyscraper
  buildings, like everything on Genussa" (*Adventures at Meagel University*, 2019-05-09).
- **No trees**: "where are you going to find a tree on Genussa" (*Exhuming Nora Omundsen*, 2019-06-20),
  although a log-mill business existed there centuries ago.
- **Four quadrants**, given as a grid (*Adventures at Meagel University*):
  ```
  G1|G2
  G3|G4
  ```
  - G1: "commercial, residential".
  - G2: "entertainment, probably safest, university district, where you'll probably have people come if
    you want to have people come to Genussa". Has the **Casino Strip** and the **University District**.
  - G3 and G4: "anarchy, unless you have the cover of a gang. You don't go there unless you're involved in
    organized crime."
  - **Contradiction:** in 2022 the logs say "Q3, the business district, high money, cleanest of the
    quadrants" (*Espresso at the Bank*, 2022-09-05). See §5.
- **Water exists**: "There are docks by the main river where the river dumps into the bay. Dock A9 is the
  spot Daryo usually meets with him" (*A Deal with the Devil (Coney)*, 2022-11-07). "We drive west.
  There's a lengthy shoreline along this bay. A marina and some docks, and an abandoned lighthouse at the
  edge of the docks that's been turned into the Orange Star. Everything here is crummy. The road long since
  stopped being paved. Lights flicker if they're on at all … a junkyard of a shore … the Orange Star,
  which sits on a small island" (*Monkey Lips at the Orange Star*).
- **A chasm**: Yafel is on Genussa, "deep in a chasm of unknowing, under a wise star" (*Bargain in the Ash
  Pit*, 2025-03-27). Its location is unknown.
- **A gate** sits near the planet: "from this gate, we are now just outside the planet Genussa" (*Escape
  Through the Gate*, 2019-05-02). Ships need clearance to enter the atmosphere ("Our G9 clearance gets us
  into atmo").

## 2. Visual cues

Stated:
- A planet-wide skyscraper metropolis ("like everything on Genussa"). Vegas-style casinos. Neon and themed
  lights: the Blue Coconut has "bright blue lights with island paradise tiki theme". The Orange Star
  lighthouse has an orange "barbershop stripe" and "a five-point star logo … spinning and flicke[ring]".
- Bad districts are dim and patchy: "Lights flicker if they're on at all"; roads unpaved.
- No trees, no parks (in contrast to Terran's "parks initiative").
- A main river, a bay with a long shoreline, a marina, docks, small islands.
- Day and night under the Red Sun.
- No moons, size or orbit figures stated.

Inferred:
- From orbit: a dark grey/rust urban crust by day, and at night a dense web of city light over almost all
  the land. The reference image (inspiration only) shows exactly that: a rust-brown surface webbed with
  orange light.
- "Nega-Terran": like Terran (a planet-city) but negative: dirtier, darker, more neon, no green.
- Quadrant contrast at night: G2 the brightest and most colourful (casino strip neon). G1 a dense, even
  warm-white grid. G3/G4 dimmer, broken and flickering, with fire-orange spots. The bay and the river are
  dark gaps in the lights.
- Water is limited to a river system, the bay and probably one sea the bay opens into (the casino name
  "Eleven Oceans" is the only hint of oceans).

## 3. Places

**Convention.** lat +north, lon -180..180. The quadrants follow the grid as written, north up: the
equator and the 0°/180° meridian divide them. **G1 = NW (lat>0, lon<0), G2 = NE (lat>0, lon>0), G3 = SW,
G4 = SE.** Each quadrant is a quarter of the planet.

**The hub.** The logs cross quadrant lines in short drives (Q3 docks to the Orange Star "about 12 miles
away … in Q2"), so the places the party visited must lie where quadrants meet. The proposal puts the
**river mouth and bay at (0, 0)**, where all four quadrants meet. It does this for three reasons: it makes
the short cross-quadrant trips possible; it explains why a river and bay would mark the quadrant lines;
and it puts the action at the front of the texture.

**Scale.** The size is unknown. If Genussa is Earth-sized, 12 miles is about 0.17°. Distances in the hub
cluster are spread out by about 10× so the pins can be told apart; directions are kept.

| Name | Type | DB id | Parent | Geographic clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
|---|---|---|---|---|---|---|---|
| Genussa | PLANET | UGxhY2U6MTg= | The Red Sun | "Vegas of Planets"; "Nega-Terran" | n/a | | |
| G1 | REGION | UGxhY2U6Mzk= | Genussa | "commercial, residential"; top-left of the grid | label 40, -90 | layout | NW quarter |
| G2 | REGION | UGxhY2U6Mzc= | Genussa | "entertainment, probably safest, university district"; top-right | label 40, 90 | layout | NE quarter |
| G3 | REGION | UGxhY2U6NDA= | Genussa | "anarchy … organized crime" (2019); "Q3, the business district, high money, cleanest" (2022); bottom-left | label -40, -90 | layout | SW quarter |
| G4 | REGION | UGxhY2U6NDE= | Genussa | "anarchy … organized crime"; bottom-right | label -40, 90 | layout | SE quarter |
| (no DB) Main river and bay | water | none | Genussa | "docks by the main river where the river dumps into the bay"; "lengthy shoreline along this bay" | mouth at 0, 0; bay south of it | layout | The hub (see above) |
| Dock A9 (Genussa) | LOCATION | UGxhY2U6MzE= | none in DB | "docks by the main river where the river dumps into the bay. Dock A9 is the spot Daryo usually meets with him [Monkey Lips]" | 0.3, 0.3 | layout | At the river mouth. Which quadrant is unstated (Q4) |
| (no DB) Q3 port / ship dock | location | none | G3 | "We pull up to the ship in the dock area"; "the port we just left" (lockers, Cherry Beard); "we've been in Q3" | -0.6, -0.4 | layout | Head of the bay, SW side |
| Genussan Bank with Espresso | LOCATION | UGxhY2U6NjU= | G3 | "Dorinda tells us where the nearby bank is"; walked to from the port; "fancy, like we've been transported to a completely different world" | -0.9, -0.8 | layout | Walking distance from the port, in Q3 |
| Orange Star | LOCATION | UGxhY2U6MzA= | G3 (DB); "Q2" (log) | "about 12 miles away at the Orange Star just outside the University District, in Q2 (we've been in Q3)"; "We drive west … lengthy shoreline along this bay … abandoned lighthouse … sits on a small island"; watched the Red Sun set from it | -1.0, -2.0 | layout | West of the port along the bay shore, on an islet. Follows the DB's G3 and "drive west". The log's "Q2" can't fit a north-up grid (Q2) |
| Blue Coconut | LOCATION | UGxhY2U6MzI= | G2 | "The Blue Coconut is in Q2"; Daryo: "little place down the road"; parking lot; "bright blue lights with island paradise tiki theme"; Daryo's home is "the Blue Coconut's basement" | 1.2, 1.5 | layout | G2, near the hub (a short van ride from the bank) |
| Manticore Green (Genussa) | LOCATION | UGxhY2U6MzM= | G2 | "a really swanky casino"; a safe house "right next to the Manticore Green" | 1.8, 3.2 | layout | On the Casino Strip |
| (no DB) Casino Strip | district | none | G2 | "Welcome to G2. Geographically, we're a little closer to University District than the Casino Strip." | strip from 1.5, 2.5 to 2.5, 4.5 | layout | East of the landing spot, in G2 |
| Meagel University | LOCATION | UGxhY2U6Mzg= | G2 | "Campus isn't sprawling, but built of many vaunting skyscraper buildings"; in the University District; nearby "Alleys … where most things are available for purchase" | 2.5, 1.0 | layout | Closer to the landing spot than the Strip is |
| (no DB) Cemetery (Nora Omundsen's grave) | location | none | Genussa | "the graveyard where the exhumation with Bode occurred"; graves ~350 years old | 6, -6 | guess | No clue. Old ground in G1 |
| (no DB) Yafel's chasm | landmark | none | Genussa | "deep in a chasm of unknowing, under a wise star" | -25, 40 | guess | No clue. Make it a visible natural rift in the city (Q6) |
| (no DB) Ansible hub | landmark | none | Genussa | "They control the hub for it" | 0, 0 (hub) or orbit | guess | Unstated |

## 4. Feature-spec draft

| Feature | Type | Where | Size | Clue |
|---|---|---|---|---|
| Planet-wide city | `city` base layer (emissive night lights, grey/rust day albedo) | all land | global | "skyscraper … like everything on Genussa"; "metropolis" |
| Quadrant boundaries | lines: broad dark avenues or walls | equator, and lon 0 and ±180 | 0.5–1° wide | G1–G4 grid |
| Quadrant light character | emissive modulation | G2 bright multicolour neon; G1 dense warm-white grid; G3/G4 dim, sparse, flickering orange | quarters | Quadrant descriptions; "Lights flicker if they're on at all" |
| Main river | `river` | from 35, 0 south along lon 0 to 0, 0 (G1/G2 line) | 0.3° wide | "the main river where the river dumps into the bay" (the course is a guess) |
| The bay | `lake`/bay | centred -3, 0, from lat 0 to -6, lon -2.5 to 2.5 | ~6° × 5° | "lengthy shoreline along this bay" |
| Southern sea | ocean | lat -6 to -25, lon -20 to 20, opening from the bay | ~20° × 40° | Guess: a bay needs a larger water body |
| Orange Star islet | `island` with an orange beacon | -1.0, -2.0 | 0.2° | "sits on a small island" |
| Casino Strip | emissive line (brightest neon) | 1.5, 2.5 to 2.5, 4.5 | ~2° | "Casino Strip" |
| Blue Coconut | blue point light | 1.2, 1.5 | point | "bright blue lights" |
| Yafel's chasm | `valley`/rift, unlit | -25, 40 | ~8° × 1° | "deep in a chasm of unknowing" (position is a guess) |
| No vegetation | biome rule | everywhere | | "where are you going to find a tree on Genussa" |

## 5. Contradictions and open questions for the DM

1. **Which quadrant is the rough one?** In 2019 (and the DB), G3 and G4 are "anarchy". In 2022, "Q3"
   is "the business district, high money, cleanest". Which is current? Should G1 ("commercial") and G3
   swap?
2. **Is the Orange Star in G2 or G3?** The log says "in Q2, just outside the University District", but
   the place is "crummy", 12 miles **west** of the Q3 docks, and in G3 in the DB.
3. **Are G1–G4 quarters of the whole planet, or districts of one city on it?** The 12-mile trips between
   quadrants suggest one city, or a hub where all four meet. Is that hub the river mouth and bay?
4. **Which quadrant is Dock A9 in?** It has no parent in the DB. Is it at the Q3 port where the ship
   docks, or at the river-mouth docks?
5. **Any natural terrain beyond the river and bay?** A sea or oceans? Mountains? Desert outside the city?
   Does the city cover every bit of land?
6. **Where is Yafel's "chasm of unknowing, under a wise star"?** Is the "wise star" the Orange Star, or
   Meagel University?
7. Where is the **ansible hub**: on the surface, or in orbit? Does Genussa have a moon or a station?

## 6. Sources read

- DB places: Genussa, G1, G2, G3, G4, Meagel University, Manticore Green (Genussa), Blue Coconut, Orange
  Star, Genussan Bank with Espresso, Dock A9 (Genussa) (no parent). These are all places whose parent
  chain reaches Genussa, plus Dock A9 by name.
- Primer: On the Planets (2013-01-01).
- Logs: Escape Through the Gate (2019-05-02); Adventures at Meagel University (2019-05-09); Manticore
  Green (2019-05-16); Daryo Mr. Worlds (2019-05-23); Invisibility, Upgrades, & Dog Treats (2019-06-13);
  Exhuming Nora Omundsen (2019-06-20); Reconstructing Nora (2019-07-11); Off the Grid (2019-08-01); Ghost
  in the Sheev (2020-11-23); Intruders (2021-05-24); Daryo's Chair, Kozmo's Kontalaria (2021-06-07); The
  Naming of Kozmo (2021-06-21); Searching Dhund Hal Ka's Backpack (2022-08-01); Shadows of Betrayal
  (2022-08-22); Espresso at the Bank (2022-09-05); Back Alley Costumed Kerfuffle (2022-10-03); Drug Wars
  and Skeeball (2022-10-24); A Deal with the Devil (Coney) (2022-11-07); Monkey Lips at the Orange Star
  (2022-11-21); Brawnheim Steamroller (2022-12-05); Betrayal at Sea (2023-12-04); Bargain in the Ash Pit
  (2025-03-27).
- Reference images (`img/Genussa_0..1`): inspiration only. A rust-brown planet webbed with orange city
  lights.

## 7. Ideas kept for later (Nov 2026)

Shipped: the Berlin model (one grid, quadrants differ by lamp era and money, wide blends between
them). Ideas the user wants kept, not done yet:

- **G1 vs G2 still read alike** at whole-planet scale (G2 is a little brighter, with hot spots). Options:
  bigger and more numerous G2 hot spots; or a calmer, more uniform G1 carpet (steady residential light
  against G2's clustered blaze).
- **The river** north of the hub reads as a thin black wiggly line, close to the "crack" look. Make it
  wider and softer, or light its banks.
- **G4's dark tract** and **Yafel's chasm** barely show at whole-planet scale.
- **Confetti at close zoom**: the app's `cityDetail` points glitter more than they should.
- Annotated quadrant map script: `<scratchpad>/annot/genussa_map.py` (not committed).

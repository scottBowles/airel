# Janus: lore brief for texture and pins

Sources: production DB (`places.json`, Nov 2026), "On the Planets" primer, and every session log that
mentions Janus or its places (listed at the end). Quotes are verbatim; "log" means a session log,
cited as *Title (date)*.

## 1. Canon summary

- **Half light, half dark.** DB description: "Half Light, Half Dark, a Little Mezzolux". Notes / primer:
  "One half's light, one half's dark, with a very little bit of overlap in the center."
- **Made that way by Dhund Hal Ka.** Exiled to one planet by Gliten, "Dhund Halka in her attempt at
  balance drew this one planet into an even split of light and dark. And thus Janus was born. So Dhund
  Halka is landlocked there" (*Stories in Gliten's Chapel*, 2021-01-04).
- **Orbits the Red Sun** (DB parent). The tidal lock is the brief's reading of "half light, half dark";
  no log says "tidally locked" in so many words.
- **The dark side is temperate, kept warm by geysers, and clouded.** "the whole thing seems to
  constantly have geysers of heated thermal vents exploding into the air. This is where the clouds come
  that cause the dark side to be dark, though pretty temperate." Geysers "of varying sizes, but average
  about 10-12 ft. We can see the craters where they occur" (*Visparo*, 2021-06-28). Underground, the
  "thermal spurts of steam … keep the dark side of the planet from being an ice-half-planet"
  (*Underground Exploration*, 2021-07-16).
- **People.** "Netherese, Human, Drow" (DB). "Even the Light and the Dark don't tend to interact much."
  All "pay homage to the Netherese princes/leaders" (DB). Dark side: "Most of the cities on the dark side
  are floating above the planet, but there are a few settlements on the surface, including the house of
  knowledge. The floating cities are more like the Princes' houses … the Drow beneath are matriarchal"
  (*Visparo*). Izar (a Shadovar from the dark side): "on his world their cities are floating in a shadow
  dimension" (*The Floating Cube*, 2020-12-21). Underground: "the Drow in the Deep and the communities that
  try to break in from the light side" (*Underground Exploration*). Drow houses named: Ligeia, Maillard,
  Tamarlain, Luchesi (*Parlay with the Drow*, 2021-11-15; *Jetpacks and Salamanders*, 2021-12-06).
- **The Mezzolux / Penumbra** ("Mezzanox" in one log): "the grey area between the areas of light and
  dark". The ground near it is "desolate, desert-like. There are occasional ashy grey cacti-looking
  things", "rock land", with "a shepherd, Bedouin-style community with 300 or so goat-like creatures"
  (*Visparo*). It has buttes ("One of the lasers hits a butte"), seasonal storms ("This time of year those
  storms are generally flash-floody with big downpours and tons of lightning"), and Visparo's hut "is in a
  channel" next to "high ground … a ledge and a cave" (*Netting the Dagger*, 2022-07-11).
- **Width of the Mezzolux.** From the butte, "right in the middle of the mezzolux": "It would go pitch
  black maybe 20 miles to the west" (*Netting the Dagger*). So the band is about 40 miles across.
- **Underground**: limestone caves with geyser columns, constant mist, bioluminescent mites, translucent
  salamanders, camouflaged giant bats, water bears, cold sweet pools, underground rivers, a "room of 100
  geysers" (*Underground Exploration* to *Battle at the Geysers*, 2021-07 to 2022-01).
- **The light side itself is never described.** Nobody in the logs goes there.

## 2. Visual cues

Stated:
- Two halves, light and dark, with a thin twilight band between ("very little bit of overlap").
- Dark side: steam clouds from geysers ("where the clouds come that cause the dark side to be dark"),
  geyser craters, temperate, not frozen. Floating Princes' cities above it (they may sit in "a shadow
  dimension", so may not be visible). A few surface settlements.
- A castle of House Roderick "floating in the distance over a large mountain", from Janus (a door
  etching, *Thestal Halls of Heorot*, 2022-12-19). Its side is not stated.
- The Mezzolux: grey, desolate desert rock, ashy grey cacti, buttes and spires ("a high plateau on a rock
  that seems to be atop an epic spire of a mountain"), flash-flood channels, lightning storms in season.
- South along the Mezzolux: "The Wastelands"; underground to the south "dries out, wasteland, nothing
  really lives that way".
- No moons, rings, size or orbit figures appear anywhere.

Inferred (not stated):
- Light side: permanent red daylight under the Red Sun ("Red wild fire"). Arid and scorched is the
  user's recommendation in `assets.md`, not lore.
- Dark side surface: dark rock under a cloud deck lit from below by faint settlement glow and from above by
  floating-city lights (if visible). **Not ice-covered**: the lore says the steam prevents that.
  `assets.md` recommends "dark rock and ice"; ice at most as patchy frost far from vent fields, or none.
- Desert-like ground extends a little way into the dark side (they drove with night vision through it,
  switching it off only near the Mezzolux).
- Geography beyond the visited spot (oceans, ranges) is unknown: noise can decide it.

## 3. Places

**Convention.** lat +north, lon -180..180. **Sub-solar point at (0, 0)**: the light side is lon -90..90,
the anti-solar point is lon ±180, and the Mezzolux is the ring at lon ±90.

**East/west.** The logs disagree on which way is dark (see §5, Q1). Two of three statements put the dark
to the **west** of the visited site, so all visited sites sit on the **lon -90** arc of the ring (west of
it is dark, east is light). If the DM picks the butte note instead (dark east), **negate every lon** below:
the sites move to the +90 arc.

**Scale.** Janus's size is unknown. The 40-mile Mezzolux is about 0.6° wide on an Earth-sized planet.
Positions below keep the stated directions, but distances in the Mezzolux cluster are spread out by about
10× so the pins can be told apart.

| Name | Type | DB id | Parent | Geographic clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
|---|---|---|---|---|---|---|---|
| Janus | PLANET | UGxhY2U6MTk= | The Red Sun | "Half Light, Half Dark, a Little Mezzolux" | n/a | | |
| Mezzolux | REGION | UGxhY2U6NTc= | Janus | "a very little bit of overlap in the center"; "pitch black maybe 20 miles to the west" | label at 0, -90 (ring at lon ±90) | lore | The terminator is fixed by the light/dark split |
| The Penumbra | REGION | UGxhY2U6NTk= | Janus | "We go to the penumbra looking for Visparo. The Mezzanox." | 14, -90 | layout | Same band as the Mezzolux (probably a duplicate, Q3). Label it on the visited arc |
| The House of Knowledge | LOCATION | UGxhY2U6NTY= | Janus | Dark-side surface settlement ("a few settlements on the surface, including the house of knowledge"). Reached by 4-wheeler, then "desolate, desert-like" ground "toward the Mezzanox"; night vision off only "as we get closer" | 12, -96 | layout | Dark side, a drive from the hut (distance unstated) |
| Visparo's Hut | LOCATION | UGxhY2U6NTg= | Mezzolux | Thatched hut, engines cut "about a half-mile walk away"; "the hut he was in is in a channel"; near "high ground … a ledge and a cave"; the ship landed there; Izar flies "to the northwest" from the butte to reach it | 12, -90.4 | layout | In the band, just dark-ward. NW of the butte |
| Janus Underground | REGION | UGxhY2U6NjE= | Janus | Entered near the Penumbra; junction: "North … Drow … scouts"; "due West (into the dark side) … Black Lake"; "South, dries out, wasteland" | 11.5, -90.6 | layout | Under and around the hut. Cave entrance near it |
| Black Lake | LOCATION | UGxhY2U6NjA= | Janus Underground | "Heading due West (into the dark side of the planet) we'll eventually come upon the Black Lake, which is a giant underground pool" | 11.5, -93 | layout | Due west of the junction. Distance is a guess |
| (no DB) Nearest Drow city | location | none | Janus Underground | "the Drow presence from the nearest city"; north of the junction | 14.5, -91 | guess | "If we go North … Drow" |
| (no DB) Room of 100 geysers / Dhund Hal Ka's cave | location | none | Janus Underground | Reached by taking the South branch ("spaghetti bowl South"); "round and approximately 150 ft across … rows of geyser towers"; griffins ride a geyser burst "to the surface" | 10.5, -90.5 | layout | South of the junction, still near the band |
| The Wastelands | REGION | UGxhY2U6NjI= | Janus | "We travel along the mezzolux to the south. …to the wastelands!"; underground "South, dries out, wasteland, nothing really lives that way" | centre -10, -90; spans lat 8 to -30, lon -93 to -87 | layout | South of the cave along the band |
| Butte on Janus | LOCATION | UGxhY2U6NjM= | Mezzolux | "high plateau on a rock that seems to be atop an epic spire of a mountain. It is in the mezzolux … right in the middle of the mezzolux … a 120' diameter rock – a large butte"; "pitch black maybe 20 miles to the west"; Izar flies "to the northwest" back to Visparo/ship | 8, -90.0 | layout | Mid-band (lon exactly on the terminator), SE of the hut, south along the band toward the Wastelands |
| Sarcophagus of Gliten (Lizard Teresias' Cube) | LOCATION | UGxhY2U6NjQ= | Butte on Janus | The cube "slowly descending" onto the butte | 8, -90.0 | lore | Same spot as the butte |
| (no DB) Bedouin shepherd camp | location | none | Mezzolux | "300 or so goat-like creatures … herding through the rock land as we make our way toward the Mezzanox" | 12, -91.5 | guess | On the drive between the House and the hut |
| (no DB) Princes' floating cities | location | none | Janus | "Most of the cities on the dark side are floating above the planet"; "floating in a shadow dimension" | scatter, lon -100 to -170 and 100 to 170 | guess | Dark side. Izar knows "only … a couple" |
| (no DB) House Roderick castle | location | none | Janus | "a castle floating in the distance over a large mountain"; a druid house, sigil "a door with eight eyes" | 30, -125 | guess | Floating castle means the dark side. Position free |

## 4. Feature-spec draft

| Feature | Type | Where | Size | Clue |
|---|---|---|---|---|
| Day/night split | `terminator_band` | ring at lon ±90 | true width ~0.6° (40 mi); draw a visible twilight blend of 3–5° | DB, *Netting the Dagger* |
| Dark-side cloud deck | cloud mask | lon \|lon\|>95, thickest near vents | whole night hemisphere, patchy | "This is where the clouds come that cause the dark side to be dark" |
| Geyser fields | crater scatter, emissive steam glow | dark side and the Mezzolux; dense near -90 arc | craters tiny (10–12 ft geysers): render as speckle fields only | *Visparo* |
| Grey desert rock band | biome | lon -96 to -88 near the visited arc, extend along the whole ring | ~6° | "desolate, desert-like … ashy grey cacti … rock land" |
| Butte country | `mountain_range` (mesas/spires) | lat 15 to -5, lon -91.5 to -88.5 | ~20° × 3° | Butte "atop an epic spire"; "One of the lasers hits a butte" |
| The Butte | `mountain` (spire) | 8, -90.0 | <0.1° (pin only) | Butte note |
| Visparo's channel | `valley` (flash-flood channel) | from 13, -90.6 to 11, -90.2 | ~2° long | "the hut he was in is in a channel" |
| The Wastelands | biome (barren, paler) | lat 8 to -30, lon -93 to -87 | ~38° × 6° | Branch and the Griffins; Underground Exploration |
| Large mountain under the Roderick castle | `mountain` | 30, -125 | ~4° | Thestal Halls door |
| Dark-side settlement lights | `city` (faint, emissive) | House of Knowledge 12, -96; a few scattered dark-side towns | points | "a few settlements on the surface" |
| Floating Princes' cities | emissive points above the surface (or skip if in shadow dimension) | ~5 points lon 100–170 / -100 to -170 | points | *Visparo* |
| Day side | biome | lon -88 to 88 | hemisphere | No lore. Use the user's recommendation: scorched, arid, rust-red under the Red Sun |

## 5. Contradictions and open questions for the DM

1. **Which side is dark, looking from the butte?** The butte note says "the darkness of the east and the
   light of the west" (*Gryphons to the Mezzolux*, 2022-01-31). *Netting the Dagger* (2022-07-11) says
   "pitch black maybe 20 miles to the west", and *Underground Exploration* (2021-07-16) says "due West (into
   the dark side)". Which is right? (This only picks which arc of the ring the sites are on.)
2. **Is the dark side dark because it faces away from the sun, or partly because of the geyser clouds?**
   ("This is where the clouds come that cause the dark side to be dark".) Is Janus tidally locked to the Red
   Sun? "At dawn on the third day" and "this time of year" (storm season) hint at days and seasons.
3. Are **The Penumbra** and **Mezzolux** the same region? If so, merge one into the other as an alias.
4. **What is the light side like** (temperature, terrain, who lives there)? Is "scorched, arid" right?
   Any ice anywhere, or does the steam keep the whole dark side ice-free?
5. **How big is Janus**, and does the Mezzolux run all the way round, or only where the party went?
6. Is the butte in or next to **The Wastelands**?
7. Which side is **House Roderick's** floating castle on, and can floating cities be seen from orbit?

## 6. Sources read

- DB places: Janus, Mezzolux, The Penumbra, The House of Knowledge, Visparo's Hut, Janus Underground,
  Black Lake, The Wastelands, Butte on Janus, Sarcophagus of Gliten (all of Janus's children; there are
  no others among the 98 places).
- Primer: On the Planets (2013-01-01).
- Logs: Shellback Ceremony (2019-04-11); The Floating Cube (2020-12-21); Stories in Gliten's Chapel
  (2021-01-04); Iconic Conflicts (2021-01-18); Daryo's Bodily Death (2021-04-12); Into the Black
  (2021-05-10); Daryo's Chair, Kozmo's Kontalaria (2021-06-07); The Naming of Kozmo (2021-06-21); Visparo
  (2021-06-28); Underground Exploration (2021-07-16); Not a Clew (2021-09-06); A Bad Day for Dmitri and
  Freedieedi (2021-09-20); The Fungal Room (2021-10-04); Subterranean Squeeze (2021-10-18); Parlay with the
  Drow (2021-11-15); Jetpacks and Salamanders (2021-12-06); Guerrillas in the Myst (2021-12-20); Battle at
  the Geysers (2022-01-03); The Branch and the Griffins (2022-01-17); Gryphons to the Mezzolux (2022-01-31);
  The Rise and Fall of Giga-Gargoyle (2022-03-14); Greg's 40th (2022-03-28); Cubism (2022-04-11); The
  Blind Seer (2022-05-09); The Scales and the Disc (2022-06-06); Netting the Dagger (2022-07-11);
  Searching Dhund Hal Ka's Backpack (2022-08-01); Shadows of Betrayal (2022-08-22); Thestal Halls of
  Heorot (2022-12-19).
- Reference images (`img/Janus_0..2`): inspiration only. One shows a lit rust-orange half and a black half.

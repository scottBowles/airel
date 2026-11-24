# The seven moons of Gonhirrim

All seven are DB `Place`s of type MOON with parent **Gonhirrim**. Each DB description reads "Gonhirrim moon
close to <god> (<domains>)", and the primer pairs each moon with one god. "There is a representative
temple to each of the gods other than death&time and fire&chaos … One god per moon." (*WINEPRESS*,
2020-09-14). Only three moons were visited: Durinfol, Broadbeam and Ironfist. The other four have nothing
beyond the god pairing.

| Moon | DB id | God (domains) | Visited? | User's plan (assets.md) |
| --- | --- | --- | --- | --- |
| Broadbeam | `UGxhY2U6OQ==` | Gliten, goddess of air and balance | yes | hazy thin atmosphere |
| Firebeard | `UGxhY2U6MTA=` | Tyronóë, goddess of dreams and psyche | no | violet tint |
| Blacklock | `UGxhY2U6MTE=` | Moronóë, god of wisdom and hearth | no | warm-lit settlements |
| Durinfol | `UGxhY2U6MTI=` | Thiton, god of water and life; capital Erebôr | yes | ice and water, some green |
| Ironfist | `UGxhY2U6MTM=` | Mazoë, god of justice and courage | yes | iron-red rock |
| Stiffbeard | `UGxhY2U6MTQ=` | Yafel, knowledge and temperance | no | pale stone |
| Stonefoot | `UGxhY2U6MTU=` | Glitonea, goddess of earth and law | no | heavily cratered |

(The primer spells the gods "Tyrono'e" and "Moronnoe". *The Scales and the Disc* (2022-06-06) uses
"Tyronóë", "Moronóë", and "Yafel (Knowledge/Cunning)".)

## Shared canon (all moons)

- "Predominantly Dwarven. Craftspeople. Gems." "When tech helps the mining of the moons, they'll take
  advantage." "They have completely rejected terraforming." (Gonhirrim DB notes)
- "These are largely mining colonies." The moons are "embroiled" in labor-union struggles (*WINEPRESS*).
- "Due to some atmospheric difficulties in some moons, some are uninhabited except like Hielo … But all of
  the moons of Gonhirrim are inhabited." (DB notes; contradictory, see questions)
- **They have breathable air and weather** (stated per moon below). People walk outside on Broadbeam,
  Durinfol and Ironfist with no suits. There are lakes, fog, clouds, wind, a "windy day", sunlight and a
  day/night cycle.
- Orbit to surface: Tres's shuttle trip from the ship in orbit to Ironfist "is about two hours"
  (*Daryo's Bodily Death*, 2021-04-12).
- Reference: `img/Gonhirrim_0.jpg` shows a brown, cratered moon and a small pale one beside the giant
  (mood only). `img/Gonhirrim_1.jpg` is most likely the flag (see `gonhirrim.md`).

**Inference for the shared base.** The text describes worlds with air, weather and water, which an airless
cratered rock doesn't have. Keep the user's "mined rock" base, but give every moon at least a thin
atmosphere rim and some cloud. Make mining scars and settlement lights the shared motif. No size, order,
orbit or tidal lock is stated. **Convention used below:** lon 0 is the meridian facing Gonhirrim (assuming
tidal lock), and lat 0 is the orbital plane.

---

## Durinfol (Thiton, water/life)

### 1. Canon summary
- "Durinfol - Erebôr Capital" (*On the Planets*). DB: "<Erebôr> is its capital".
- **The lake:** "On Durinfol is a lake. At the north end of the lake is the capital city of Erebôr. At its
  south end is the temple." / "We will land on the Crystal Coral Lake" (*WINEPRESS*, 2020-09-14).
- **The temple:** "The temple is more of a dock than anything else. A building that seems to be docked,
  floating in water." It looks like "a slightly smaller version of the squid cathedral" on Hyang Wan. It has
  water channels, a single-pane "glass steel" floor over water "thriving with aquatic life", coral
  furniture, a waterfall curtain, "a flying buttress", a library with a "sunlight glass ceiling", and pump
  systems. (*Pilgrimage on Durinfol*, 2020-11-09)
- **Water:** "It is crystal clear fresh water, though we're on a saltwater lake." (same)
- **Weather:** "It's a windy day" (Darnit on the high scaffolding, same).
- Heraldry: "the gilded circle of Durinfol" (same).

### 2. Visual cues
- Stated: a large **saltwater lake** called the Crystal Coral Lake, big enough to land a ship on and with
  a city at one end; coral; abundant aquatic life; wind; sunlight; open sky.
- Inference: "Coral" and life "thriving" suggest **warm or temperate** water, which pulls against the
  "ice and water" plan. Recommendation: a temperate moon with blue-green water and green shores around the
  lake, and ice only at the poles. Erebôr is a capital, so it should show the brightest lights on this moon.
  The "gilded circle" suggests gold accents if a tint is wanted.

### 3. Places

| Name | Type | DB id | Parent | Clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Crystal Coral Lake | lake (no DB entry) | none | Durinfol | "On Durinfol is a lake"; "Crystal Coral Lake"; "saltwater lake" | centre 12, 30; elongated N–S, ~12° × 5° | guess | No size or location stated. Elongated N–S because it has a north end and a south end. Placed on the Gonhirrim-facing side |
| Erebôr | TOWN (capital) | `UGxhY2U6MjE=` | Durinfol | "Capital of Durinfol"; "At the north end of the lake is the capital city of Erebôr" | 18.5, 30 | layout | Fixed relative to the lake (north shore). The lake itself is a guess |
| Temple of Thiton (Durinfol) | temple (no DB entry) | none | Durinfol | "At its south end is the temple"; "a building … docked, floating in water" | 5.8, 30 | layout | On the water at the south shore |

Do **not** pin the DB place "Thiton's Temple" (`UGxhY2U6MzQ=`) here. Its description says "On Hyang Wan",
and it is the vandalised shrine from 2019.

### 4. Feature spec
| Feature | Type | Lat, lon | Size | From |
| --- | --- | --- | --- | --- |
| Crystal Coral Lake | lake (salt, turquoise shallows) | 12, 30 | 12° × 5°, N–S | *WINEPRESS* |
| Erebôr | city lights (brightest on the moon) | 18.5, 30 | ~1.5° | capital, north end |
| Temple | point light on water | 5.8, 30 | tiny | south end |
| Other seas and lakes | water bodies | noise | — | Thiton, water/life (inference) |
| Green lowlands around water | biome | near water | — | "some green" (user), life (inference) |
| Polar ice | polar caps | ±70 | small | user plan "ice and water" |
| Mining scars and small town lights | mining / lights | scattered | — | shared base |

---

## Broadbeam (Gliten, air/balance)

### 1. Canon summary
- "On the moon of Broadbeam we easily locate a chapel of Gliten. In a mountainous region, floating between
  mountains over a great fog is a (non-gelatinous) cube. It appears to be of a blue glassy material."
  (*The Floating Cube*, 2020-12-21)
- "The fog does not move the slightest bit, even as the ship's engines move through it." "There are eight
  mountains surrounding the cube. Every other is one the same height, and the others are the same height as
  each other too, but a bit shorter … We land on the Southwest mountain -- one of the shorter ones." The
  bridges are glass, under 2 ft wide, and run to the cube's corners. The crossing is "~200 / 250 m" of rope
  and then more. Hrothulf picks up "handfuls of sand … sand and gravel" on the mountain. (same)
- The cube is 45 ft with "a four-foot ledge"; inside it is 42 ft, with a dome and colours of "white and
  blue". "The stratus clouds in the sky are definitely moving, despite the fact that there is no wind
  blowing." (*Stories in Gliten's Chapel*, 2021-01-04)

### 2. Visual cues
- Stated: mountains, a sea of fog in the valleys, stratus cloud overhead, open sky, sand and gravel on the
  peaks, blue-white glassy architecture.
- Inference: the user's "hazy thin atmosphere" fits. Give it **fog banks filling the lowlands** and a layer of
  stratus cloud, so the haze reads from orbit. The mountains should be rugged. The temple is too small to
  see from orbit.

### 3. Places

| Name | Type | DB id | Parent | Clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gliten's Floating Cube Chapel (alias "Gliten's Chapel") | LOCATION | `UGxhY2U6NTI=` | **none in DB** (description: "On Broadbeam, a moon of Gonhirrim") | "In a mountainous region, floating between mountains over a great fog"; "eight mountains surrounding the cube"; landed on "the Southwest mountain" | 35, −40 | guess | Needs a mountainous region and nothing more. The ring of peaks is a few km across, far below a texel |

### 4. Feature spec
| Feature | Type | Lat, lon | Size | From |
| --- | --- | --- | --- | --- |
| Gliten's Highlands (region holding the chapel) | mountain range / highland | 35, −40 | ~18° × 12° | "mountainous region" |
| Ring of eight peaks (4 tall, 4 shorter, alternating) | mountain ring, regional map only | 35, −40 | <0.2° | *The Floating Cube* |
| Valley fog sea | fog / low cloud mask in valleys | in highlands and elsewhere | — | "great fog" |
| Stratus decks | cloud layer | global, patchy | — | "stratus clouds in the sky" |
| Mining scars, settlement lights | shared base | scattered | — | shared |

---

## Ironfist (Mazoë, justice/courage)

### 1. Canon summary
- Darnit's home moon: "Though he is from the moon of Ironfist, Gonhirrim remains home." (*Pilgrimage on
  Durinfol*). "This is where Darnit is from." (*The Lady's Ladle…ing Stew*, 2021-02-01). He is "Darnit, son
  of Gosh, house Golly." (*Zedd's Cause*, 2023-03-20)
- **Lady's Ladle:** Uncle Drat's dwarf restaurant and bar. The party arrives in "late afternoon"; it has a
  "patio" and windows. "They travel here by means of a lab-grown burro/elephant hybrid called Priuses."
  It's "open-carry country". (*Lady's Ladle*; *Rules Are Rules*, 2021-03-01)
- **Golly mines:** Gosh "is retired from mining of metallics in the Golly mines. The region has strife
  between those who vie for specified separate labor unions or one unified labor union." (*Lady's Ladle*)
- **Colosseum of Mazoë:** visited the same evening, after the brawl. "Center stage is the thunderbowl, a
  concave, circular arena with drains"; bleachers, screens, six gates; the floor's topography is changed by
  machinery underneath. (*Thunderbowl Fights*, 2021-03-15). Outside it's night: "Izar finds himself
  outside, in the cool dark." (*Ego Defeats Izar (DQ)*, 2021-03-29). Darnit: "anything religious would be
  in the bowl itself", so the colosseum is Mazoë's temple on this moon.
- Orbit link: "The trip is about two hours" by shuttle from the ship in orbit (*Daryo's Bodily Death*).

### 2. Visual cues
- Stated: a day/night cycle; the night is "cool"; metal mining; dwarven towns with bars, patios and an
  arena.
- Inference: "iron-red rock" (user) fits the name and the metallic mining. Give it rust-red highlands,
  large open-pit and strip-mine scars, and dense warm town lights around the mining region.

### 3. Places

| Name | Type | DB id | Parent | Clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Darnit's home town (unnamed) | town (no DB entry) | none | Ironfist | holds both the Lady's Ladle and the Colosseum (walked between them the same evening) | −20, 60 | guess | No location stated |
| Lady's Ladle | LOCATION (bar) | `UGxhY2U6NTM=` | **none in DB** (description: "A Dwarf bar on Ironfist, owned by Darnit's Uncle Drat") | "late afternoon"; patio; windows | −20.1, 59.9 | layout | In the same town as the Colosseum |
| Colosseum of Mazoë | LOCATION (arena / temple) | `UGxhY2U6NTQ=` | **none in DB** | "the thunderbowl, a concave, circular arena"; reached the same night | −19.9, 60.2 | layout | Same town |
| Golly mines | mining region (no DB entry) | none | Ironfist | "mining of metallics in the Golly mines. The region has strife…" | −17, 63 (region ~8°) | layout | "the region" is Darnit's family's, so it's near the home town |

### 4. Feature spec
| Feature | Type | Lat, lon | Size | From |
| --- | --- | --- | --- | --- |
| Golly mining district | mining scars (open pits, terraces) | −17, 63 | ~8° | Golly mines |
| Darnit's town | city lights | −20, 60 | ~1° | Lady's Ladle + Colosseum |
| Iron-red highlands | albedo / biome | global, with darker basins | — | user plan, the name |
| Other mining towns | small lights | scattered | — | "mining colonies" |

---

## Firebeard, Blacklock, Stiffbeard, Stonefoot

No session visited them and none has a DB child place. Canon is only the god pairing above. Use the shared
base plus the user's variation: Firebeard violet (dreams), Blacklock warm-lit settlements (hearth),
Stiffbeard pale stone (knowledge), Stonefoot heavily cratered (earth/law). The names hint at colours
(Fire-, Black-, Stone-) that could add to these; that's inference only.

---

## 5. Contradictions and open questions for the DM

1. **Durinfol: ice or warm?** The log has a saltwater "Crystal Coral Lake" with coral and thriving life.
   The plan in assets.md says "ice and water". Should Durinfol be temperate (blue-green lake, green shores,
   small polar ice) instead?
2. **Atmospheres.** Durinfol, Broadbeam and Ironfist all have breathable air, wind, cloud or fog. Does every
   moon have air and weather? Which moons does "atmospheric difficulties in some moons" mean, given that
   "all of the moons of Gonhirrim are inhabited"?
3. **Sizes and order.** Are the moons roughly equal in size, as the flag draws them? Is there an order
   outward from Gonhirrim, and is any moon notably bigger (e.g. Durinfol as the capital moon)?
4. **Tidal lock.** Do the moons always show Gonhirrim the same face (so Gonhirrim hangs fixed in their
   sky)? The positions here assume yes, with lon 0 facing the planet.
5. **DB parents.** Should "Gliten's Floating Cube Chapel" get parent Broadbeam, and "Lady's Ladle" and
   "Colosseum of Mazoë" get parent Ironfist? Their descriptions say so but `parent` is empty, so they'd have
   no pins. Should the Durinfol temple, Crystal Coral Lake, Darnit's town and the Golly mines become places?
6. **Dwampton** (towns Tolland, Erskineville, Dwamton: "carved out the largest mountain", the Dwamish River)
   comes from a ReDream replay of *The Legacy of Dhund Halka* (2020-12-07). Is it on a Gonhirrim moon, or
   elsewhere / only historical? I've left it unplaced.

## 6. Sources read

DB places: the 7 moons, Erebôr, Gliten's Floating Cube Chapel, Lady's Ladle, Colosseum of Mazoë, Thiton's
Temple, Tolland/Erskineville/Dwamton. *On the Planets* (2013-01-01). Logs: *Convincing Daryo*
(2020-08-31), *WINEPRESS* (2020-09-14), *Pilgrimage on Durinfol* (2020-11-09), *Ghost in the Sheev*
(2020-11-23), *In the city…city of Dwampton* (2020-12-07), *The Floating Cube* (2020-12-21), *Stories in
Gliten's Chapel* (2021-01-04), *Iconic Conflicts* (2021-01-18), *The Lady's Ladle…ing Stew* (2021-02-01),
*Rules Are Rules* (2021-03-01), *Thunderbowl Fights* (2021-03-15), *Ego Defeats Izar (DQ)* (2021-03-29),
*Daryo's Bodily Death* (2021-04-12), *Into the Black* (2021-05-10), *Zedd's Cause* (2023-03-20), *The
Scales and the Disc* (2022-06-06), *Visparo* (2021-06-28). I also grepped every downloaded log for the moon
and god names, Erebôr and Golly.

# Felucia: lore brief for the texture and pins

Jungle planet of the Yellow Sun. DB: `Felucia` (Place:5, `UGxhY2U6NQ==`, PLANET, parent The Yellow Sun). Description
"Forest Planet of Fey". **It has no child places in the DB** and the party never played a session there, so there is
**no geography in the canon**: every position below is a `guess`. The model in `solars` is spelled `Falucia`, and so are
several logs.

## 1. Canon summary

- **Jungle, humid, colourful, hopeful.** "Forest planet … Humid, colorful, jungle. Full of vibrance. A very hopeful kind
  of atmosphere." (DB notes; On the Planets, 2013-01-01). "(Basically stolen from the Star Wars universe)" — i.e. Star
  Wars' Felucia.
- **Fey and elves.** "Large elvish population … Lots of elf, but mixed. All of your woodland. Dryads, faeries, batfey,
  etc." (DB notes). "high elven forest in falucia" (A Deal with the Devil (Coney), 2022-11-07). In legend, "the
  miserably underpowered elven population in Felucia who's struggling against the Orc horde" (Ghost in the Sheev,
  2020-11-23).
- **Wildlands.** "It's got the wildlands, so there's a large chunk intentionally left undeveloped, free to do what it
  does. Probably the biggest voice against the Whidmore Corporation's terraforming enterprise" (DB notes).
- **Tradition plus technology; libraries.** "Traditionalists, but not afraid of technology, so you'll see that blend";
  "The libraries there would be full of people like Bruno's mom--sage … while communing with nature"; "Trade in
  knowledge, wisdom of years gone by. A lot of scionic influence" (DB notes).
- **Dinosaurs.** "We met the dinosaurs there" (DB notes; from play before the logs).
- **Rivers.** A Freelander: "I've spent most of my time … on Falucia in smaller ecological events … there was another
  corporate type illegally diverting rivers" (Zedd's Cause, 2023-03-20).
- **Hot springs in the jungle.** "There's a lot of overlap between the hot springs of Felucia and those in Canaz, only
  swapping jungle for stone" (Quarrel's Cargo, 2023-10-02).
- **A volcano.** Dhund Hal Ka: "Thrown away we found the sarcophagus [of Mazoë] on Felucia in a volcano. That doesn't
  mean it's still there." (Searching Dhund Hal Ka's Backpack, 2022-08-01). Her branch's era, long ago.
- **Other mentions:** Bruno "was born on Felucia" (Into the Black, 2021-05-10); a rumour that Bruno went "for a
  walk-about in Falucia" (Monkey Lips at the Orange Star, 2022-11-21); Teresias "spent forever looking for [the Lady
  Saharel] on Fallucia" — she was on Mystra (The Blind Seer, 2022-05-09); the gryphon-cavalry hatchery might be on
  "Gonhirrim or Felucia" (party speculation, Convincing Daryo, 2020-08-31).
- "Often referred to as the third planet. (After Terran, Genussa, based on voice in the planet …)" (DB notes): a rank in
  political weight, **not** orbital order.

## 2. Visual cues

**Stated**
- Surface: "Forest planet", "jungle", "humid", "colorful", "Full of vibrance". Wildlands: "a large chunk intentionally left
  undeveloped". Rivers. Hot springs in jungle. At least one volcano.
- Population: large, elvish, with "that blend" of tradition and tech: settlements and libraries in nature, so some
  night lights, but no metropolis is ever described.
- Orbit: Yellow Sun (DB parent). 2nd in the primer's list (after Magmus) and #2 on the user's sketch.
- Not stated: oceans or seas, ice caps, moons, size, day length, clouds.

**Inferred (mine)**
- Mostly land under unbroken jungle canopy; water as rivers, lakes and small seas. The reference image (bright lush green,
  white clouds, little ocean) agrees, but is inspiration only; assets.md already plans "mostly jungle, vivid, cloudy,
  small seas".
- "Colorful": not a flat green. Vary the canopy from emerald to lime and yellow-green, with patches of flowering colour
  (magenta, orange, violet); Star Wars' Felucia, which the DM says it is "stolen from", is known for giant
  brightly-coloured fungi. Keep these as accents, not a rainbow.
- "Humid": many white cumulus clouds and low haze, more than Earth, far less than Hyang Wan's grey deck. Small or no
  polar ice.
- Wildlands: the densest, darkest canopy with no lights, a single large region.
- Night side: soft, scattered warm lights (towns in forest, libraries); none in the wildlands. Much dimmer than Terran
  or Genussa.

## 3. Places

No DB places have Felucia as parent. These are the features the logs name, with positions chosen only to spread them
across the globe readably. All `guess`; longitudes are arbitrary.

| Name | Type | DB id | Parent | Clues (verbatim) | Proposed lat, lon | Conf. | Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Wildlands | region | none | Felucia | "a large chunk intentionally left undeveloped, free to do what it does" (DB notes) | −10, 120 (~45° × 70°) | guess | One big region, a "large chunk", on the hemisphere away from the developed lands |
| High elven forest | region | none | Felucia | "high elven forest in falucia" (Coney, 2022-11-07) | +35, −60 | guess | In the developed hemisphere, old-growth on higher ground |
| Libraries / elven heartland | region (settled) | none | Felucia | "The libraries there…"; "Bruno's Dad was ambassador" (DB notes) | +15, −20 | guess | Main settled band, mild latitudes |
| Volcano of Mazoë's sarcophagus | mountain (volcano) | none | Felucia | "we found the sarcophagus on Felucia in a volcano" (Backpack, 2022-08-01) | +5, 40 | guess | Near the edge of the wildlands; volcanic highland that also explains hot springs |
| Hot springs of Felucia | location | none | Felucia | "the hot springs of Felucia … only swapping jungle for stone" (Quarrel's Cargo, 2023-10-02) | 0, 44 | guess | On the volcano's flank |
| Diverted rivers | rivers | none | Felucia | "illegally diverting rivers" (Zedd's Cause, 2023-03-20) | from the volcanic highland (+5, 40) W to a sea at (+5, −5) | guess | Large river systems need highlands and a sea; this one drains the settled lands |

Not places (no position possible): the dinosaurs ("We met the dinosaurs there"), the orc-horde wars (legend), the gryphon
hatchery (speculation).

## 4. Feature-spec draft

| Feature | Kind | Centre (lat, lon) | Size | Source / note |
| --- | --- | --- | --- | --- |
| Jungle land | land cover | — | ~75–85 % of surface | "Forest planet", "jungle" |
| Canopy colour variation | biome noise | — | patches 3–10° | "colorful … Full of vibrance" |
| Wildlands | dense dark jungle, no lights | −10, 120 | ~45° × 70° | "a large chunk … left undeveloped" |
| High elven forest | old-growth, darker emerald | +35, −60 | ~15° | Coney, 2022-11-07 |
| Settled heartland | soft town lights | +15, −20 | ~40° × 60° | libraries, elves, tech blend |
| Volcanic highland | mountain + volcano cone | +5, 40 | highland ~12°, cone ~2° | sarcophagus "in a volcano"; hot springs |
| Hot springs | small steaming pools (haze) | 0, 44 | < 1° | Quarrel's Cargo |
| Great river | river | (+5, 40) → (+5, −5) | ~45° long | "diverting rivers" |
| Small seas / lakes | seas | e.g. +5, −5; +45, 70; −40, −40; −55, 160 | 5–15° each | inferred (humid world needs water; image) |
| Clouds | clouds | global | ~40–55 % cover, white, puffy; haze | "Humid" |
| Polar caps | — | — | none or very small | inferred from "humid … jungle" |

## 5. Contradictions and open questions for the DM

1. **Water.** How much ocean? Is it "small seas" (the image) or a jungle with Earth-like oceans? (This sets the whole map.)
2. **Wildlands.** One continent-sized region, or several reserves? Roughly what share of the planet?
3. **Places to pin.** Any named cities, the libraries, Bruno's family home, the elven high forest, the dinosaurs' region?
   Without names the globe has no pins.
4. **Volcanoes.** Is the sarcophagus volcano a single landmark (and still there), or is Felucia volcanic generally?
5. **Moons, size, day length?** Nothing in the canon.
6. **"Third planet"** in the notes means political weight, not orbital order (it is 2nd from the Yellow Sun in the
   primer and the sketch). Right?

## 6. Sources read

- DB place Felucia (places.json + production API; no children). Reference image Felucia_0 (inspiration only).
- On the Planets (2013-01-01).
- Logs tagged with Felucia: Into the Black (2021-05-10); Searching Dhund Hal Ka's Backpack (2022-08-01); Quarrel's Cargo
  (2023-10-02).
- Logs found by grep of all 152 logs for Felucia/Falucia/Fallucia/Felucian and related terms (dinosaur, wildlands, elven,
  volcano, faerie, batfey, Mmbaugh, Bruno's parents): Convincing Daryo (2020-08-31); Ghost in the Sheev (2020-11-23);
  In the city...city of Dwampton (2020-12-07; a ReDream memory of a port, Port Bail, "taxing ships that come in to make
  trade from Felucia": planet unstated, probably not Felucia); Stories in
  Gliten's Chapel (2021-01-04); The Blind Seer (2022-05-09); A Deal with the Devil (Coney) (2022-11-07); Monkey Lips at
  the Orange Star (2022-11-21); Zedd's Cause (2023-03-20).

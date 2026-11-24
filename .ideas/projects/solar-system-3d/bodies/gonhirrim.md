# Gonhirrim (gas giant)

DB: `Place` **Gonhirrim**, id `UGxhY2U6OA==`, type PLANET, parent **The Yellow Sun**. Description:
"Blue-Collar Planetary System". Seven MOON children (see [`gonhirrim-moons.md`](gonhirrim-moons.md)).
Alignment LN. No DB place sits on the planet itself.

## 1. Canon summary

- **Gas giant with seven inhabited moons.** "Gas planet with seven moons" / "No one lives on the planet
  as such, but the moons are inhabited." (DB notes; *On the Planets*)
- **Permanent storm.** "There's some controversy in delving into the gas giant itself. So far attempts
  haven't gotten far. Too much of a storm all the time. Cloud." (DB notes; *On the Planets*)
- **The eighth moon is its core.** "'The eighth moon' is how they refer to the center of the gas giant.
  … That's where their creator/crafter god lived or lives. That's where their fallen go to rest."
  (DB notes). "None have gotten there and returned. Some say it is a myth, and the planet is a gas giant,
  but Darnit will hear nothing of that." (*Convincing Daryo*, 2020-08-31). Later called "the center
  moon of the gas giant" (*Into the Black*, 2021-05-10).
- **Strong magnetic field.** Comms from orbit to Ironfist failed: "It's being interrupted by a magnetic
  field created by the gas giant here." (*Daryo's Bodily Death*, 2021-04-12)
- **Weather is a navigation hazard.** Ego hopes an AI could anticipate and counteract "weather patterns"
  to reach the core (*Convincing Daryo*, 2020-08-31).
- **Orbiting stations.** "Typically one would need to stop by the orbiting station before entering"
  (*WINEPRESS*, 2020-09-14); Izar shops "in one of the orbiting stations where there's higher quality"
  (same); Mystra pilgrimages "have largely stalled at the Confederate orbiting station" (*Pilgrimage on
  Durinfol*, 2020-11-09).
- **People and culture** (for lights, not geography): "Predominantly Dwarven. Craftspeople. Gems."
  "Blue collar planetary system. Pittsburgh." Lean to the old ways "but when tech helps the mining of the
  moons, they'll take advantage." "They have completely rejected terraforming. Whidmore can't get it."
  (DB notes). "Largely mining colonies"; labor-union politics; "the moons tend to have 2 trad, 2 prog,
  1 swing" senators (*WINEPRESS*). Strong gem trade with Magmus (*On the Planets*).
- **Heraldry.** "The blue seal of Gonhirrim"; a book's splash page "holds the Gonhirrim print and the
  gilded circle of Durinfol" (*Pilgrimage on Durinfol*). The same log shows "The flag of Gonhirrim:" with
  an embedded image (211×178 px).

## 2. Visual cues

**Stated**
- Gas giant; stormy and cloudy "all the time"; nobody has reached the interior.
- A magnetic field strong enough to block short-range radio.
- One or more orbiting stations (one is Confederate), used as a customs stop.
- Orbits the Yellow Sun (DB parent). The user's sketch numbers it 5, after Hyang Wan and before Hielo.
- *Space Battle* (2019-04-25), leaving Hyang Wan: the asteroid belt is "a couple hours" away, and via the
  gates "We could get to Gonhirrim before then." This loosely puts Gonhirrim near Hyang Wan and the belt.
- No rings, colours or band count appear anywhere in the text.

**Inference**
- **`img/Gonhirrim_1.jpg` (seven circles around a central one, crossed by a dark-red ring) is almost
  certainly the flag of Gonhirrim, not an orbit diagram.** Its aspect ratio (1.179) matches the flag image
  in *Pilgrimage on Durinfol* (211.56 × 178.5 px = 1.185). Read it as heraldry: seven moons around the
  eighth (the core), maybe in a ring. It doesn't say the moons share one orbit.
- `img/Gonhirrim_0.jpg` (a pink/orange/yellow banded giant) gives the mood. Use its palette, because the
  text names no colours.
- "Too much of a storm all the time" suggests turbulent, high-contrast bands with many eddies and one
  dominant great storm (where the core is "hidden"). The planet should look hostile, not calm.
- A strong magnetic field plus a nearby sun suggests faint polar aurorae (optional).
- As a gas giant it should be the **largest planet** in the system. Nothing in the text sizes it.
- Night side: no lights, because nobody lives on the planet. A faint aurora or lightning in the great storm
  is the most that is justified.
- No rings: none are mentioned, and the user ruled the same way for Hyang Wan.

## 3. Places

No DB place has Gonhirrim as parent except its seven moons. Objects that belong near it but aren't on its
surface:

| Name | Type | DB id | Parent | Clues (verbatim) | Proposed position | Conf. | Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| "The eighth moon" (the core) | myth / core | none | Gonhirrim | "how they refer to the center of the gas giant"; "None have gotten there and returned" | not on surface; hidden under the great storm (see feature spec) | guess | The core is unseen. A storm "eye" is a natural visual stand-in |
| Confederate orbiting station | station | none | Gonhirrim (or a moon) | "Typically one would need to stop by the orbiting station before entering"; "the Confederate orbiting station"; "one of the orbiting stations" | small object in low orbit around Gonhirrim | guess | It's a customs stop for the whole system. Which body it circles isn't stated |

## 4. Feature-spec draft

The coordinates are for a banded shader. Lat +N; lon −180..180.

| Feature | Type | Lat, lon | Size | From |
| --- | --- | --- | --- | --- |
| Zonal bands, alternating pale zones and dark belts, ~12–16 bands, strong turbulent edges | band set | whole globe | widths 5–15° lat | "Too much of a storm all the time. Cloud." Palette from reference image |
| Great storm (stand-in for the unreachable core, "the eighth moon") | storm (oval vortex) | −22, 40 | ~28° × 16° | perpetual storm + core myth (inference) |
| Secondary storms / white ovals, a dozen or so, drifting along band edges | storm (small) | scattered, mostly ±10–45° | 2–6° | "storm all the time" |
| Chaotic polar regions (no clean bands above ~65°) | polar turbulence | ±65–90 | caps | inference (common for giants; adds "always stormy") |
| Aurora ovals (optional, emissive, night side) | aurora | ±70 | ring ~8° wide | "magnetic field created by the gas giant" |
| Lightning flicker in the great storm (optional, emissive) | storm lights | −22, 40 | within storm | inference; same idea as Chromium's lightning |

No city lights and no rings.

## 5. Contradictions and open questions for the DM

1. **Is the ring diagram (reference image 2) the flag of Gonhirrim?** If it is (the aspect ratio matches the
   flag in *Pilgrimage on Durinfol*), should the moons still orbit separately, or share one orbit evenly
   spaced the way the flag shows them?
2. **The eighth moon:** should the model hint at it, e.g. a great storm whose eye glows faintly, or leave
   the planet with no hint of a core?
3. **Colour:** the text gives none. Is the reference image's pink/orange/yellow palette right, or should it
   lean toward the "blue seal of Gonhirrim"?
4. **Orbiting station:** should the Confederate station appear in the model? Does it circle Gonhirrim
   itself or one of the moons?

## 6. Sources read

- DB places: Gonhirrim, its 7 moons, Erebôr, Gliten's Floating Cube Chapel, Lady's Ladle, Colosseum of
  Mazoë, Thiton's Temple (Hyang Wan), Space.
- *On the Planets* (primer, 2013-01-01).
- Logs: *Space Battle* (2019-04-25), *Escape Through the Gate* (2019-05-02), *Convincing Daryo*
  (2020-08-31), *WINEPRESS* (2020-09-14), *ReDream Immortality* (2020-09-28), *Artificial Intransigence*
  (2020-10-26), *Pilgrimage on Durinfol* (2020-11-09; HTML checked for the flag image), *Ghost in the Sheev*
  (2020-11-23), *In the city…city of Dwampton* (2020-12-07), *The Floating Cube* (2020-12-21), *Stories in
  Gliten's Chapel* (2021-01-04), *Iconic Conflicts* (2021-01-18), *The Lady's Ladle…ing Stew* (2021-02-01),
  *Rules Are Rules* (2021-03-01), *Thunderbowl Fights* (2021-03-15), *Ego Defeats Izar (DQ)* (2021-03-29),
  *Daryo's Bodily Death* (2021-04-12), *Into the Black* (2021-05-10), *Visparo* (2021-06-28).
- I grepped all 150+ downloaded logs for the body, moon and god names, Erebôr, Golly and "eighth moon".
- Reference images `img/Gonhirrim_0.jpg` and `img/Gonhirrim_1.jpg`.

# Places to add to the database

Places the lore briefs (`bodies/*.md`) found in the logs that have no DB `Place` row. Each brief's
places table has the verbatim clue, a proposed lat/lon and the reasoning. Once a place is in the DB,
its planet can get a pin for it.

## Bodies

- **Didymus (the twin)**: the smaller, rounder twin. The DB has only `Didymus` (the system) and
  `Didymus Prime`.
- **Hyang Wan's moon**: seen setting over Mulgogi in two logs.
- **The gates**: Vostok, Galileo, Tiberius, Lizhi, Aryabhata. They're named only in the system sketch's legend.
- **Confederate orbiting stations**: at Mystra ("pilgrimages have largely stalled at the
  Confederate orbiting station"), at Didymus ("fairly undermanned"), and probably one at Gonhirrim.
  They might be one place type with several instances.

## By planet

**Hielo**: the only Hielo place in the DB is the planet itself.
- The ice caves (Whidmore's energy canisters)
- The Roper's cave (maybe part of the ice caves)
- Hammer and Kiln's Hiobium works
- The science station (where the scientists died)
- Bode Augur's exile camp

**Genussa**
- The main river and the bay ("docks by the main river where the river dumps into the bay")
- The Q3 port / ship dock
- The Casino Strip (G2)
- The cemetery (Nora Omundsen's grave)
- Yafel's chasm ("a chasm of unknowing, under a wise star")
- The ansible hub

**Janus**
- The nearest Drow city (Janus Underground)
- The room of 100 geysers / Dhund Hal Ka's cave (Janus Underground)
- The Bedouin shepherd camp (Mezzolux)
- The Princes' floating cities
- House Roderick's castle (it has a pin from the DB; check it's a Place with Janus as parent)

**Mystra**
- Lady Saharel's (the Blue Lady's) shrine. Lady Saharel is a Character.
- Thorin's temple: the tower that became a rocket
- The polvimithe source
- The nuns' convent and lavender distillery
- House Lukesea's (the Loukasins') seat

**Didymus Prime**
- The One Horn Riders' compound
- The drop-off point, about 8 mi SE of Ashtown
- Whidmore's land / terraforming ("owns more than half of Prime")
- Klutch's home town ("a backwater town on Didymus")

**Felucia**: no DB place has Felucia as parent.
- The Wildlands
- The high elven forest
- The libraries / elven heartland
- The volcano of Mazoë's sarcophagus
- The hot springs
- The diverted rivers

**Hyang Wan**
- Railman's tunnels and camp
- The port town where the Desconnegut landed
- The East Isles
- The major city on Hatatori Island (near Jing Long)
- The small uninhabited islets
- The squid migration route (maybe not a place)

**Terran**
- The Senate
- The Arena in Champion City
- The gladiatorial arena of Mazoë (an earlier branch)
- Whidmore's terraforming testbed

**Gonhirrim and moons**
- Crystal Coral Lake (Durinfol)
- Temple of Thiton (Durinfol)
- Darnit's home town (Ironfist; unnamed)
- The Golly mines (Ironfist)
- "The eighth moon" (Gonhirrim's core; a myth)

**Chromium**
- The Halls of the Pantheon (seen in a vision)

## DB fixes noticed

- **Dock A9 (Genussa)** has no parent. It's probably G4 or the river-mouth docks.
- **Tomb of Teresias** has no parent. It should be Mystra.
- Hielo is linked to six logs that never mention it (*Finding the Freelanders*, *Zombie Zip Tie*,
  *Echoes of the Iron Castle*, *Quarrel's Cargo*, *Mirages Unveiled*, *A Worthy Battle for the Dead*).
  These are probably AI mis-links.

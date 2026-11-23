"""Mystra ("the pink Dagobah"): generate texture maps and pins from the spec below.

    python3 tools/planets/mystra.py [--width 4096] [--out web/static/system/mystra] [--clouds-only]

Lore (see .ideas/projects/solar-system-3d/bodies/mystra.md and QUESTIONS.md):
- "The pink Dagobah. Very swampy." A mystic world, a pilgrimage site, orbiting the Red Sun.
- The surface is mostly, not entirely, hidden by pink mist (DM, Nov 2026). The Mystrans didn't
  know other planets existed until the party's rocket: a sky that is nearly always hidden.
- Mostly swamp with some uplands; the pink is the vegetation and the water (QUESTIONS.md
  defaults, not answered by the DM).
- "Nuns and lavender whiskey": lavender fields on a drier upland (inference in the brief).
- The ancient Netherese and "Thorin's rocket that once was a tower", the complex powered by
  polvimithe: an ancient-technology site on an upland (brief's guess).
- The Tomb of Teresias, the Blue Lady's shrine and House Lukesea's seat: places on firm ground
  near the swamps (all positions are the brief's guesses; nothing in the logs fixes them).
- A pre-spaceflight society: very few lights at night.

Real analogue, and how it's translated:
- Structure: the great lowland wetlands seen from orbit (the West Siberian Plain's Vasyugan
  mire, the Sudd, the Pantanal). From orbit they're a dark, mottled, fairly even tone, crowded
  with small dark lakes and pools in clusters, with lighter floodplain belts along the big
  rivers. Not channels: at ~10 km a texel the rivers themselves are too thin to draw, so they
  show as belts of fresher vegetation strung with oxbow pools.
- Colour: a red-sphagnum raised bog (the Flow Country, Estonian bogs), whose moss lawns are
  deep red, wine and rose with ochre-mauve hummocks and black peat pools. Vegetation is dark
  from orbit, so the pinks here are deep and muted (plum, wine, rose, mauve), never candy;
  the world reads pink because its main palette is pink, from plum to dusty mauve, with no
  spots of accent colour. Water is peat-stained blackwater (the Rio Negro from orbit is nearly
  black), tinted violet-brown, with rose algal shallows (the pink of Lake Hillier and Lake
  Retba, from Dunaliella algae, kept faint: a bright pink lake from orbit reads as a spot).
- The mist: marine stratocumulus decks (off California, Namibia, Peru) are the closest
  thing to a world-covering low cloud from orbit: a vast lumpy sheet, thick and thin in patches,
  breaking at its edges into fragments and then clear air; and valley fog (the Po Valley,
  California's tule fog), which fills the lowlands and leaves the high ground standing clear.
  Here one field does both: the deck is thickest over the swamps and breaks over the uplands,
  and where it opens over the swamp a thin, streaky ground fog still lies in the basins. Its
  colour is set in the app (one colour for the layer); clouds.webp is how much of it there is.

Interpretations (all guesses unless marked):
- Swamp ~80% of the land, uplands ~20%: low plateaus rising out of the swamp, the named ones
  where the brief puts its sites, the rest from the noise.
- Open water ~6% (a few large shallow lakes from the brief, invented smaller ones, and pools
  gathered into lake districts); no seas (none is named).
- The launch site isn't scarred: the launch was years ago, and a scorched patch would read as
  damage from orbit.
- Polar caps: none; a swamp world under a warm, wet deck.
- Night: a handful of dim, warm towns at the sites and a few dozen villages on firm ground
  (the user found two lights a hemisphere too few, Nov 2026); a faint magenta tint at the Netherese
  complex (Mystran robots glow "a sort of magenta", 2018-10-16). No faint magenta swamp
  glow (the brief's option): not built, as a broad glow risked reading as a rash.
- Only the Tomb of Teresias gets a pin: it's the only DB place on Mystra.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from clouds import rank
from felucia import meander
from planetgen import (
    Noise3,
    angular_distance,
    fbm,
    make_grid,
    normal_map,
    ramp,
    ridged,
    save_gray,
    save_rgb,
    smoothstep,
    unit,
    write_pins,
)

SEED = 717
UPLAND = 0.2  # share of the surface that's firm upland, not swamp
MIST_COVER = 0.72  # share under the thick deck

# Named uplands: (lat, lon, radius°). Positions from the brief (all guesses).
NETHERESE = (30, 60, 10)  # Thorin's tower-rocket and the complex; the polvimithe source
TOMB = (18, -40, 7)  # Tomb of Teresias, at a swamp's edge
LAVENDER = (-22, 95, 8)  # the nuns' convent and lavender fields
CENTRAL = (8, 8, 9)  # invented: the low rise holding the Blue Lady's shrine and House Lukesea's seat
SHRINE = (5, 20)
LUKESEA = (10, -5)

# Large shallow lakes: (lat, lon, radius°). The first three are the brief's; the rest invented.
LAKES = [
    (-5, -120, 9),
    (35, -150, 7),
    (-40, 10, 11),
    (4, -70, 5),
    (50, 96, 6),
    (-12, 145, 7),
    (-55, -60, 6),
]

# Big rivers (source on an upland → mouth in a lake). Drawn as floodplain belts, not channels.
RIVERS = [
    ((14, -45), (5, -66)),  # from the Tomb's upland to the small western lake
    ((2, 10), (-32, 9)),  # south off the central rise into the great southern lake
    ((26, 54), (47, 91)),  # from the Netherese upland north-east
    ((-20, 103), (-13, 139)),  # from the lavender upland east
    ((22, -100), (1, -114)),
    ((-32, -160), (-8, -127)),
    ((55, -118), (38, -145)),
    ((-25, 42), (-37, 21)),
    ((-40, -95), (-53, -65)),
]

# Towns: (lat, lon, radius°, brightness). Very few: a pre-spaceflight people, lamps and fires.
TOWNS = [
    (LUKESEA[0], LUKESEA[1], 0.7, 0.9),  # House Lukesea's seat, the main settlement
    (SHRINE[0], SHRINE[1], 0.55, 0.7),  # the pilgrim town at the Blue Lady's shrine
    (18.6, -39.2, 0.35, 0.45),  # pilgrims' village by the Tomb
    (-22, 95, 0.4, 0.5),  # the convent and distillery
    (27, 52, 0.35, 0.4),  # village below the Netherese complex
    (14, 4, 0.35, 0.45),
    (-3, 2, 0.3, 0.4),
    (22, -48, 0.3, 0.35),
    (-26, 88, 0.3, 0.35),
    (35, 66, 0.25, 0.3),
]
VILLAGES = 45  # more villages, placed on firm ground (see generate)
VILLAGE_GAP = 6.0  # degrees between any two settlements
COMPLEX = (31, 61)  # the Netherese complex: a small cool-magenta glow

PINS = [
    dict(name="Tomb of Teresias", lat=TOMB[0], lon=TOMB[1], confidence="guess"),
]

LAMP = np.array([1.0, 0.7, 0.42], np.float32)
NETHER = np.array([0.8, 0.45, 0.85], np.float32)


def river_field(g, rng, warp):
    """Distance (degrees) to the nearest river course, and how big that river is there (1 at a
    main stem's mouth, less up its tributaries). As felucia.py, with Mystra's rivers."""
    dist = np.full(g.lat.shape, 99.0, np.float32)
    size = np.zeros(g.lat.shape, np.float32)
    q = g.xyz + 0.006 * warp
    q /= np.linalg.norm(q, axis=-1, keepdims=True)
    lat = np.degrees(g.lat)
    lon = np.degrees(g.lon)
    systems = []
    for src, mouth in RIVERS:
        main = meander(rng, src, mouth, rough=0.3)
        systems.append((main, 1.0))
        for _ in range(int(rng.integers(3, 6))):
            k = int(rng.integers(len(main) // 5, len(main) * 4 // 5))
            join = main[k]
            ang = rng.uniform(0, 2 * np.pi)
            ln = rng.uniform(4, 10)
            start = join + ln * np.array([np.sin(ang), np.cos(ang) / np.cos(np.radians(join[0]))])
            systems.append((meander(rng, start, join, depth=5), 0.55 * (k / len(main)) + 0.25))
    pad = 2.0
    for pts, big in systems:
        for i, (p, r) in enumerate(zip(pts[:-1], pts[1:])):
            la0, la1 = min(p[0], r[0]) - pad, max(p[0], r[0]) + pad
            rows = np.where((lat[:, 0] >= la0) & (lat[:, 0] <= la1))[0]
            if not len(rows):
                continue
            c = np.cos(np.radians(np.clip(abs(p[0]) + pad, 0, 85)))
            lo0, lo1 = min(p[1], r[1]) - pad / c, max(p[1], r[1]) + pad / c
            cols = np.where((lon[0] >= lo0) & (lon[0] <= lo1))[0]
            if not len(cols):
                continue
            view = (slice(rows[0], rows[-1] + 1), slice(cols[0], cols[-1] + 1))
            sub = q[view]
            pa, pb = unit(*p), unit(*r)
            ab = pb - pa
            t = np.clip(((sub - pa) @ ab) / max(float(ab @ ab), 1e-12), 0, 1)
            d = np.degrees(np.linalg.norm(sub - (pa + t[..., None] * ab), axis=-1))
            s = big * (0.35 + 0.65 * (i + t) / (len(pts) - 1))  # wider downstream
            better = d < dist[view]
            dist[view] = np.where(better, d, dist[view])
            size[view] = np.where(better, s, size[view])
    return dist, size


def terrain(g):
    """The one field everything follows: low-frequency height (what the fog sees), full height,
    the upland mask, and the warp."""
    n = [Noise3(SEED * 10 + i) for i in range(6)]
    p = g.xyz
    warp = np.stack([fbm(n[0], p * 1.6 + 11, 5), fbm(n[1], p * 1.6 + 23, 5), fbm(n[2], p * 1.6 + 37, 5)], -1)
    broad = fbm(n[3], p * 2.4 + warp * 1.3, octaves=4)
    for la, lo, r in (NETHERESE, TOMB, LAVENDER, CENTRAL):
        broad = broad + 0.45 * np.exp(-((angular_distance(g, la, lo) / r) ** 2))
    for la, lo, r in LAKES:
        broad = broad - 0.5 * smoothstep(1.6, 0.3, angular_distance(g, la, lo) / r)
    low = rank(broad)
    detail = fbm(n[4], p * 9 + warp * 2, 5)
    ridges = ridged(n[5], p * 7 + warp * 1.5, 5)
    # Uplands: the top of the broad field, edged by the detail so their margins are lobed.
    up = smoothstep(1 - UPLAND - 0.08, 1 - UPLAND + 0.1, low + 0.1 * detail)
    # The swamp is nearly flat; relief is on the uplands.
    # Height rises gently through a wide margin, so the uplands' edges have no scarp to cast a line.
    rise = smoothstep(1 - UPLAND - 0.3, 1 - UPLAND + 0.25, low)
    h = 0.6 * low + 0.04 * detail + 0.12 * rise + 0.1 * ridges * up**2
    return low, h, up, warp, ridges


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n = [Noise3(SEED * 10 + 20 + i) for i in range(10)]
    p = g.xyz
    lat = np.degrees(g.lat)

    low, h, up, warp, ridges = terrain(g)
    print(f"terrain {time.time() - t0:.1f}s")
    rdist, rsize = river_field(g, rng, warp)
    belt_w = 0.5 + 1.0 * rsize  # floodplain half-width, degrees: a broad corridor, not a line
    belt = smoothstep(belt_w, 0.0, rdist + 0.25 * belt_w * fbm(n[0], p * 25 + warp, 3)) ** 1.5 * (1 - up)
    print(f"rivers {time.time() - t0:.1f}s")

    # Lakes: the deepest basins of the broad field. Measured in a warped frame and edged by noise
    # at three scales, so the shores are crisp but lobed, with arms, bays and a few islands.
    lake_d = np.full(g.lat.shape, 9.0, np.float32)
    qw = p + 0.18 * warp + 0.06 * np.stack([fbm(n[3], p * 6 + 1, 3), fbm(n[4], p * 6 + 2, 3), fbm(n[5], p * 6 + 3, 3)], -1)
    qw /= np.linalg.norm(qw, axis=-1, keepdims=True)
    for la, lo, r in LAKES:
        lake_d = np.minimum(lake_d, np.degrees(np.arccos(np.clip(qw @ unit(la, lo), -1, 1))) / r)
    coast = lake_d + 0.35 * fbm(n[1], p * 5 + warp * 2, 5) + 0.13 * fbm(n[2], p * 22 + warp * 3, 4) + 0.04 * fbm(n[6], p * 70, 2)
    lake = smoothstep(0.95, 0.93, coast)
    shoal = smoothstep(0.86, 0.94, coast) * lake  # a narrow band of shallows inside the shore
    reeds = smoothstep(1.0, 0.95, coast) * (1 - lake)  # and a reed fringe just outside it

    # Wetness across the swamp: one field, wetter in the low ground and along the belts.
    wet = rank(fbm(n[3], p * 5 + warp * 1.4, 5) - 1.2 * low)
    wet = np.clip(0.8 * wet + 0.4 * belt + 0.15 * reeds, 0, 1) * (1 - up)
    # Pools gather in lake districts and are rare elsewhere; a few oxbows along the floodplains.
    district = smoothstep(0.45, 0.85, rank(fbm(n[2], p * 7 + warp * 2 + 5, 4))) * smoothstep(0.2, 0.5, wet)
    district = np.maximum(district, 0.35 * belt)
    # Three sizes, fewer of the larger; drawn out a little (a stretched frame, turned by the warp)
    # as pools follow the contours. Each has a soft wet rim a texel or two wide.
    aniso = np.array([1.0, 1.0, 1.7], np.float32)
    pools = np.zeros(g.lat.shape, np.float32)
    rim = np.zeros(g.lat.shape, np.float32)
    for k, (freq, share, w) in enumerate(((40, 0.07, 0.006), (85, 0.09, 0.008), (160, 0.1, 0.01))):
        f = rank(fbm(n[4 + k], p * aniso * freq + warp * (3 + k), 2))
        t = 1 - share * district
        pools = np.maximum(pools, smoothstep(t - 0.2 * w, t + 0.8 * w, f))
        rim = np.maximum(rim, smoothstep(t - 2.5 * w, t, f))
    pools *= smoothstep(0.05, 0.2, district)
    rim = (rim * smoothstep(0.05, 0.2, district) - pools).clip(0, 1)
    water = np.clip(np.maximum(lake, pools), 0, 1)  # (river channels are too thin to draw)
    print(f"water {time.time() - t0:.1f}s")

    # --- Colour ---------------------------------------------------------------------------
    # Vegetation: one ramp from wet to dry, desaturated toward dark plum-brown with rose only in the
    # fresher growth (rendered under the Red Sun, saturated crimson read as blood). Dryness is one
    # field across swamp and upland, organised by the terrain and the drainage, low in contrast.
    hd = fbm(n[8], p * 12 + warp * 2, 4)
    dry = rank(0.25 * fbm(n[6], p * 4 + warp * 1.6, 5) + 0.4 * (1 - wet) + 0.9 * smoothstep(0.45, 0.95, low + 0.06 * hd))
    veg = ramp(
        dry,
        [
            (0.0, (0.15, 0.075, 0.1)),  # dark plum-brown swamp forest
            (0.35, (0.22, 0.1, 0.14)),  # wine-brown
            (0.65, (0.28, 0.13, 0.18)),  # rose mire
            (0.85, (0.29, 0.18, 0.21)),  # mauve-brown heath
            (1.0, (0.31, 0.23, 0.24)),  # dusty mauve-brown upland
        ],
    )
    # Floodplain belts: fresher rose growth on the silt, as várzea is lighter than terra firme.
    veg = veg * (1 - 0.35 * belt[..., None]) + np.array([0.33, 0.15, 0.19], np.float32) * 0.35 * belt[..., None]
    # Uplands: the same palette's dry end, with gentle relief shading; weathered stone on the
    # Netherese plateau.
    heath = veg * (0.9 + 0.2 * ridges[..., None])
    stone = smoothstep(1.3, 0.4, angular_distance(g, NETHERESE[0], NETHERESE[1]) / NETHERESE[2] + 0.4 * hd)
    heath = heath * (1 - 0.25 * stone[..., None]) + np.array([0.38, 0.31, 0.3], np.float32) * 0.25 * stone[..., None]
    land = veg * (1 - up[..., None]) + heath * up[..., None]
    # Toward the convent, the faintest purple shift, with no edge (the lavender fields themselves
    # are far too small to see).
    lav = np.exp(-((angular_distance(g, LAVENDER[0], LAVENDER[1]) / (2.0 * LAVENDER[2])) ** 2))[..., None]
    land = land * (1 + 0.08 * lav * np.array([-0.4, -0.2, 1.0], np.float32))
    # Fine mottling from a few texels to ~20: stands of trees, mire and open water too small to
    # draw one by one. Large-scale variation stays low.
    mott = fbm(n[9], p * 90 + warp * 3, 2)
    mid = fbm(n[0], p * 30 + warp * 2, 3)
    land = land * (0.9 + 0.16 * mott[..., None] + 0.1 * mid[..., None])
    land = land * (1 - 0.3 * reeds[..., None]) + np.array([0.27, 0.12, 0.16], np.float32) * 0.3 * reeds[..., None]

    # Water: blackwater, violet-brown; a narrow rose-brown shoal inside each shore; faint algal
    # swirls in the big lakes. Pools vary from black water to brown, half-overgrown.
    swirl = fbm(n[1], p * 18 + warp * 3, 4)
    lake_rgb = np.array([0.13, 0.07, 0.1], np.float32) * (0.9 + 0.25 * swirl[..., None])
    bloom = smoothstep(0.05, 0.4, swirl) * (1 - shoal) * 0.3
    lake_rgb = lake_rgb * (1 - bloom[..., None]) + np.array([0.26, 0.11, 0.16], np.float32) * bloom[..., None]
    lake_rgb = lake_rgb * (1 - 0.7 * shoal[..., None]) + np.array([0.24, 0.12, 0.15], np.float32) * 0.7 * shoal[..., None]
    tone = smoothstep(-0.35, 0.35, fbm(n[7], p * 25 + 4.4, 3))[..., None]
    pool_rgb = np.array([0.11, 0.06, 0.085], np.float32) * (1 - tone) + np.array([0.2, 0.11, 0.12], np.float32) * tone
    water_rgb = np.where((lake > 0.5)[..., None], lake_rgb, pool_rgb)
    land = land * (1 - 0.45 * rim[..., None]) + np.array([0.3, 0.13, 0.17], np.float32) * 0.45 * rim[..., None]
    rgb = land * (1 - water[..., None]) + water_rgb * water[..., None]
    print(f"colour {time.time() - t0:.1f}s")

    # --- Lights ---------------------------------------------------------------------------
    lights = np.zeros(g.lat.shape, np.float32)
    nether = np.zeros(g.lat.shape, np.float32)
    glint = np.random.default_rng(SEED + 1).random(g.lat.shape).astype(np.float32)

    def town(la, lo, r, b):
        """A small town at night: a lit centre, lamps thinning outward, a track or two as a
        broken line. Dim: lamps and fires, not electric light."""
        rows = np.where(np.abs(lat[:, 0] - la) < 3.6 * r)[0]
        sub = (slice(rows[0], rows[-1] + 1), slice(None))
        d = angular_distance(g, la, lo)[sub]
        t = d / r
        c = unit(la, lo)
        east = np.cross([0, 0, 1], c)
        east /= np.linalg.norm(east)
        north = np.cross(c, east)
        a = np.arctan2(p[sub] @ north, p[sub] @ east)
        core = smoothstep(0.5, 0.1, t)
        lamps = (glint[sub] > 0.35 + 0.5 * t) * smoothstep(1.4, 0.3, t)
        tracks = np.zeros_like(d)
        for bearing in rng.uniform(0, 2 * np.pi, int(rng.integers(1, 3))):
            perp = np.abs(d * np.sin(a - bearing))
            along = d * np.cos(a - bearing)
            tracks = np.maximum(tracks, smoothstep(0.05, 0.015, perp) * (along > 0) * smoothstep(3.0 * r, 1.0 * r, d) * (glint[sub] > 0.6))
        lights[sub] += b * (0.6 * core + 0.45 * lamps + 0.2 * tracks)

    for la, lo, r, b in TOWNS:
        town(la, lo, r, b)
    # Villages: a few dozen more across the planet, on firm ground (the uplands, and the levees
    # of the floodplain belts), never closer than VILLAGE_GAP. Sizes and brightness vary, most
    # small. The named towns alone left a whole hemisphere with two lights.
    firm = np.maximum(up, 0.5 * belt)
    weight = (firm * (1 - water) * np.cos(g.lat)).ravel().astype(np.float64)
    weight /= weight.sum()
    placed = [unit(t[0], t[1]) for t in TOWNS]
    lonv = np.degrees(g.lon)
    villages = 0
    for idx in rng.choice(weight.size, size=4000, p=weight):
        if villages >= VILLAGES:
            break
        la, lo = float(lat.flat[idx]), float(lonv.flat[idx])
        c = unit(la, lo)
        if any(np.degrees(np.arccos(np.clip(c @ q, -1, 1))) < VILLAGE_GAP for q in placed):
            continue
        placed.append(c)
        size = float(rng.lognormal(0, 0.35))
        town(la, lo, 0.22 * size, float(np.clip(0.32 * size, 0.2, 0.6)))
        villages += 1
    print(f"  {villages} villages")
    # Hamlets: a sparse scatter on the uplands and the levees of the belts only.
    lights += 0.15 * firm * smoothstep(0.99, 0.998, rank(fbm(n[2], p * 380 + 7.7, 2)))
    lights *= 1 - water
    d = angular_distance(g, *COMPLEX)
    nether += 0.4 * smoothstep(0.3, 0.0, d)  # dim, a few texels, no brighter than the main town
    emissive = LAMP * np.clip(lights, 0, 1.1)[..., None] + NETHER * np.clip(nether, 0, 1)[..., None]
    print(f"lights {time.time() - t0:.1f}s")

    # Lakes a soft, dull sheen (wind-ruffled, weedy water); pools no glint at all.
    rough = np.clip(0.9 - 0.3 * lake, 0, 1)
    height = np.clip(h - 0.02 * water - 0.01 * belt, 0, 1)
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.02, strength=1.0))
    print(f"maps {time.time() - t0:.1f}s, water {float((water > 0.5).mean()):.3f}, upland {float((up > 0.5).mean()):.3f}")
    save_clouds(out, *mystra_mist(g, low, up))
    save_mist_glow(out, emissive)
    write_pins(out / "pins.json", "Mystra", PINS)
    print(f"done {time.time() - t0:.1f}s -> {out}")


def blur(x: np.ndarray, sigma: float) -> np.ndarray:
    """Separable Gaussian blur (σ in texels), wrapping east–west."""
    k = np.arange(-int(3 * sigma + 1), int(3 * sigma + 1) + 1)
    wts = np.exp(-0.5 * (k / sigma) ** 2).astype(np.float32)
    wts /= wts.sum()
    out = np.zeros_like(x)
    for sh, wt in zip(k, wts):
        out += wt * np.roll(x, int(sh), axis=1)
    pad = np.pad(out, ((len(k) // 2, len(k) // 2), (0, 0)), mode="edge")
    res = np.zeros_like(x)
    for i, wt in enumerate(wts):
        res += wt * pad[i : i + x.shape[0]]
    return res


def mystra_mist(g, low=None, up=None):
    """The pink mist: a near-continuous deck, broken by rifts and pockets of holes, over a thin
    ground fog that lies in every gap over the swamp.

    Openness is one field: a few large rifts drawn out along the winds, clusters of smaller
    pockets at two sizes, and clearings over the uplands, which poke through as the fog fills
    the low ground. The deck thins through a wide belt around each opening, broken by soft cells
    (about 10 and 30 texels at 4096), so its edges grade into separate lumps rather than crumbs.
    Inside, the same cells give a pebbled tone and the tops ±20% thickness at a large scale.
    No billow and no streaks: both drew contour lines and thread webs before."""
    if low is None:
        low, _, up, _, _ = terrain(g)
    n = [Noise3(SEED * 7 + i) for i in range(10)]
    p = g.xyz
    warp = np.stack([fbm(n[0], p * 2.0 + 3, 4), fbm(n[1], p * 2.0 + 9, 4), fbm(n[2], p * 2.0 + 17, 4)], -1)
    fogbed = smoothstep(0.85, 0.45, low)  # 1 deep in the swamp lowlands
    # High ground from the smooth broad field, so clearings over the uplands grade out, not cut.
    upsoft = smoothstep(0.62, 0.95, low + 0.08 * fbm(n[2], p * 8 + warp, 3))

    # Soft cells at two sizes, and large thick/thin regions.
    c1 = fbm(n[4], p * 22 + warp * 2, 3)
    c2 = fbm(n[5], p * 60 + warp * 3, 2)
    cells = np.clip(0.5 + 1.1 * (0.6 * c1 + 0.4 * c2), 0, 1)
    body = np.clip(0.5 + 1.6 * fbm(n[3], p * 3 + warp, 4), 0, 1)
    print("  mist: texture")

    # Where it opens.
    rifts = smoothstep(0.78, 0.97, rank(fbm(n[6], p * np.array([1.0, 1.0, 3.2], np.float32) * 2.2 + warp * 1.2, 5) - 0.2 * fogbed))
    cluster = smoothstep(0.5, 0.85, rank(fbm(n[7], p * 5 + warp + 3.3, 4) - 0.2 * fogbed))
    pockets = cluster * np.maximum(
        smoothstep(0.1, 0.5, fbm(n[8], p * 14 + warp * 2, 3)),
        0.8 * smoothstep(0.15, 0.55, fbm(n[9], p * 34 + warp * 2, 2)),
    )
    clearing = 0.85 * upsoft * smoothstep(0.4, 0.85, rank(fbm(n[6], p * 6 + warp + 9.1, 4)))
    # Blurred so every opening is ringed by a thinning belt (the rank()ed fields above are steep
    # wherever the noise is flat and would otherwise cut crisp holes): ~1.2° for the rifts and
    # clearings, ~0.4° for the pockets, so their clusters stay clusters.
    openness = np.maximum(blur(np.maximum(rifts, clearing), 1.2 * g.width / 360), blur(pockets, 0.4 * g.width / 360))
    # The thinning belt: wide, and broken by the cells so the edge grades into separate lumps.
    e = openness + 0.4 * (cells - 0.5)
    deck = 1 - smoothstep(0.15, 0.7, e)
    deck = deck * (0.66 + 0.34 * body) * (0.84 + 0.16 * cells)
    # Ground fog in every gap over the swamp, mottled; thin over the uplands.
    gfog = (0.45 - 0.28 * upsoft) * (0.75 + 0.6 * c1 + 0.3 * (cells - 0.5))
    alpha = gfog + (1 - gfog) * deck
    thickness = deck * (0.6 + 0.25 * cells + 0.15 * body) + 0.15 * gfog
    print("  mist: done")
    return np.clip(alpha, 0, 1).astype(np.float32), thickness.astype(np.float32)


def save_clouds(out: Path, clouds, thickness) -> None:
    out.mkdir(parents=True, exist_ok=True)
    save_gray(out / "clouds.webp", clouds)
    save_rgb(out / "clouds-normal.webp", normal_map(thickness * 0.006, strength=1.0))
    print(f"  mist: alpha>0.5 {float((clouds > 0.5).mean()):.3f}, alpha>0.8 {float((clouds > 0.8).mean()):.3f}, alpha<0.2 {float((clouds < 0.2).mean()):.3f}")


def save_mist_glow(out: Path, emissive: np.ndarray) -> None:
    """clouds-glow.webp: the lights as the mist above them shows them, scattered into soft halos
    (~0.3° and ~1°) many times wider than the lights. The app adds it to the mist on the night
    side, so towns under the deck show as smudges of light rather than vanishing. Saved at a
    quarter of the width: it's blurry by nature."""
    h, w = emissive.shape[:2]
    small = emissive[: h - h % 4, : w - w % 4].reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3))
    px = (w // 4) / 360
    glow = np.stack([0.6 * blur(small[..., c], 0.3 * px) + 0.4 * blur(small[..., c], 1.0 * px) for c in range(3)], -1)
    # Scaled so the brightest town's halo fills the 8-bit range, and lifted (power < 1) so the
    # halo's skirt stays visible rather than only its centre.
    peak = float(np.percentile(glow.max(-1), 99.98))
    save_rgb(out / "clouds-glow.webp", np.clip(glow / max(peak, 1e-6), 0, 1) ** 0.7)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/mystra")
    ap.add_argument("--clouds-only", action="store_true", help="regenerate just the mist layer")
    args = ap.parse_args()
    if args.clouds_only:
        save_clouds(args.out, *mystra_mist(make_grid(args.width)))
    else:
        generate(args.width, args.out)

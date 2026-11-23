"""Genussa ("the Vegas of planets", "Nega-Terran"): generate texture maps and pins.

    python3 tools/planets/genussa.py [--width 4096] [--out web/static/system/genussa]

Lore (see .ideas/projects/solar-system-3d/bodies/genussa.md and QUESTIONS.md):
- "Vegas of Planets." "Sleazy drug-ridden metropolis." "Nega-Terran." A planet-wide city of
  skyscrapers ("vaunting skyscraper buildings, like everything on Genussa"); no trees ("where
  are you going to find a tree on Genussa").
- Four quadrants, G1|G2 over G3|G4. G1 commercial and residential; G2 entertainment, the
  Casino Strip and the University District, the safest; G4 anarchy, organised crime. G3 is
  the clean, high-money business district (the 2022 logs; DM, Nov 2026).
- A main river runs into a bay with a long shoreline, docks, a marina, and the Orange Star on
  a small island; the bad shore is crummy, its lights flickering if on at all.
- Yafel lies "deep in a chasm of unknowing, under a wise star" (position unknown).
- It turns under the Red Sun (sunsets in the logs), so it has a day and night like Terran.

Interpretation (mine, from the brief's defaults):
- The quadrants are quarters of the planet, split by the equator and the 0°/180° meridian, and
  meet at the river-mouth bay at (0, 0), where the party's trips cross between them. Places in
  that hub are spread ~10× from their true distances so the pins can be told apart. The bay's
  western arm is what the party drove along to the Orange Star ("we drive west … a lengthy
  shoreline along this bay"), so the pins are moved a little from the brief to sit on land.
- Nega-Terran: Terran is planned (district street grids, parks, silver by day, gold at
  night). Genussa is grimy and unplanned: rust-brown and soot by day, no green anywhere, smog,
  polluted grey-green water, junkyard and slag toward the poles. At night each quadrant has its
  own light: G1 an even warm-white grid; G2 the brightest, a mix of neon colours by district
  with the Strip blazing; G3 crisp cool white, orderly, the brightest cores; G4 dim, broken,
  sodium-orange with blacked-out tracts and scattered fires.
- A few seas ("Eleven Oceans" is the only hint of oceans): a southern sea that the bay opens
  into, and three more. Yafel's chasm: a dark unlit rift in G4, placed by guess.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from clouds import make_clouds, rank
from planetgen import (
    Noise3,
    angular_distance,
    fbm,
    make_grid,
    normal_map,
    ramp,
    save_gray,
    save_rgb,
    segment_distance,
    smoothstep,
    unit,
    write_pins,
)
from terran import ellipse, grid_lines, near_arcs

SEED = 505

# The hub: the river mouth at (0, 0), where the four quadrants meet. (lat, lon) in degrees.
RIVER = [(38, -4), (31, 1.5), (24, -1.5), (17, 2.5), (10, 0.2), (4, 1.4), (0.2, 0.1)]  # source → mouth
BAY = dict(lat=-2.2, lon=0.3, ax=2.2, ay=2.2)
BAY_ARM = dict(lat=-2.6, lon=-2.5, ax=2.0, ay=0.9)  # the shore the party drove west along
ISLET = (-2.0, -3.4)  # the Orange Star's island
SEAS = [  # (lat, lon, half-width lon°, half-height lat°)
    (-16, 1, 20, 9),  # the southern sea the bay opens into
    (28, -118, 13, 8),
    (-38, 128, 11, 7),
    (50, 96, 9, 5),
]
STRIP = ((1.5, 2.5), (2.6, 4.6))  # the Casino Strip
CHASM = dict(lat=-25, lon=40, length=8.0, width=0.8, bearing=60)  # Yafel's "chasm of unknowing"

PINS = [
    dict(name="G1", lat=40, lon=-90, confidence="layout"),
    dict(name="G2", lat=40, lon=90, confidence="layout"),
    dict(name="G3", lat=-40, lon=-90, confidence="layout"),
    dict(name="G4", lat=-40, lon=90, confidence="layout"),
    dict(name="Dock A9 (Genussa)", lat=0.3, lon=0.3, confidence="layout"),
    dict(name="Genussan Bank with Espresso", lat=-0.8, lon=-2.0, confidence="layout"),
    dict(name="Orange Star", lat=ISLET[0], lon=ISLET[1], confidence="layout"),
    dict(name="Blue Coconut", lat=1.2, lon=1.5, confidence="layout"),
    dict(name="Manticore Green (Genussa)", lat=1.9, lon=3.4, confidence="layout"),
    dict(name="Meagel University", lat=2.6, lon=1.0, confidence="layout"),
]

# Night light colours.
WARM_WHITE = np.array([1.0, 0.84, 0.6], np.float32)  # G1
SODIUM = np.array([1.0, 0.55, 0.22], np.float32)  # G4
COOL_WHITE = np.array([0.82, 0.9, 1.0], np.float32)  # G3
NEON = [  # G2, by district
    np.array([1.0, 0.72, 0.35], np.float32),  # amber
    np.array([1.0, 0.42, 0.72], np.float32),  # magenta-pink
    np.array([0.45, 0.82, 1.0], np.float32),  # cyan-blue
    np.array([0.95, 0.9, 0.8], np.float32),  # white marquee
]


def districts(p, warp, rng, count):
    """Voronoi districts of jittered Fibonacci seeds, each with its own street-grid frame (as in
    terran.py: per-district tangent frames, never planet-wide axes)."""
    k = np.arange(count) + 0.5
    zs = 1 - 2 * k / count
    az = np.pi * (1 + 5**0.5) * k + rng.uniform(-0.4, 0.4, count)
    seeds = np.stack([np.sqrt(1 - zs**2) * np.cos(az), np.sqrt(1 - zs**2) * np.sin(az), zs], -1)
    seeds += rng.normal(0, 0.03, seeds.shape)
    seeds /= np.linalg.norm(seeds, axis=-1, keepdims=True)
    seeds32 = seeds.astype(np.float32)
    q = p + warp * 0.06
    q = (q / np.linalg.norm(q, axis=-1, keepdims=True)).reshape(-1, 3).astype(np.float32)
    inv = np.empty(len(q), np.int64)
    for s in range(0, len(q), 1 << 16):
        inv[s : s + (1 << 16)] = np.argmax(q[s : s + (1 << 16)] @ seeds32.T, axis=1)
    inv = inv.reshape(p.shape[:-1])
    any_dir = np.where(np.abs(seeds[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    e1 = np.cross(any_dir, seeds)
    e1 /= np.linalg.norm(e1, axis=-1, keepdims=True)
    e2 = np.cross(seeds, e1)
    turn = rng.uniform(0, np.pi, count)[:, None]
    a1 = (e1 * np.cos(turn) + e2 * np.sin(turn)).astype(np.float32)
    a2 = (-e1 * np.sin(turn) + e2 * np.cos(turn)).astype(np.float32)
    return inv, a1[inv], a2[inv]


def hashf(*v):
    x = np.zeros_like(v[0], dtype=np.int64)
    for i, a in enumerate(v):
        x = x ^ (a.astype(np.int64) * (73856093 + 19349663 * i))
    x = (x ^ (x >> 13)) * 1274126177
    return ((x ^ (x >> 16)) & 0xFFFF).astype(np.float32) / 0xFFFF


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n = [Noise3(SEED * 10 + i) for i in range(8)]
    p = g.xyz
    lat = np.degrees(g.lat)
    lon = np.degrees(g.lon)
    alat = np.abs(lat)
    warp = np.stack([fbm(n[0], p * 1.6 + 11, 5), fbm(n[1], p * 1.6 + 23, 5), fbm(n[2], p * 1.6 + 37, 5)], -1)

    # --- Water: a few seas, the bay and its arm, one river. ----------------------------------
    h = 0.35 * rank(fbm(n[3], p * 2.5 + warp * 1.3, 7))
    # Each sea is a few overlapping lobes with a warped shore, so none is an oval hole.
    for k, (la, lo, ax, ay) in enumerate(SEAS):
        # A smaller core and lobes reaching out past it as arms and inlets.
        lobes = [(la, lo, ax * 0.6, ay * 0.6)] + [
            (la + rng.uniform(-1, 1) * ay * 0.8, lo + rng.uniform(-1, 1) * ax * 0.9, ax * rng.uniform(0.2, 0.45), ay * rng.uniform(0.2, 0.5))
            for _ in range(5)
        ]
        d = np.min([ellipse(g, *lb) for lb in lobes], axis=0)
        h = h - 0.9 * smoothstep(1.5, 0.5, d + 2.2 * fbm(n[4], p * 3 + warp * 2.5 + k, 5))
    coast = 0.25 * fbm(n[5], p * 60 + warp, 4)  # small bays and points along the hub's shores
    for b in (BAY, BAY_ARM):
        h = h - 0.9 * smoothstep(1.15, 0.85, ellipse(g, b["lat"], b["lon"], b["ax"], b["ay"]) + coast)
    h = h + 0.9 * smoothstep(0.35, 0.15, angular_distance(g, *ISLET))  # the Orange Star's islet
    sea_level = np.quantile(h, 0.07)
    # The river: an open line from its source to the mouth, wandering a little (never a loop).
    meander = p + 0.004 * np.stack([fbm(n[6], p * 40, 3), fbm(n[7], p * 40, 3), fbm(n[5], p * 40 + 5, 3)], -1)
    meander /= np.linalg.norm(meander, axis=-1, keepdims=True)
    gm = type(g)(width=g.width, lat=np.arcsin(np.clip(meander[..., 2], -1, 1)), lon=np.arctan2(meander[..., 1], meander[..., 0]), xyz=meander)
    rd = np.full(lat.shape, 99.0, np.float32)
    for a, b in zip(RIVER[:-1], RIVER[1:]):
        rd = np.minimum(rd, segment_distance(gm, a, b))
    river_w = 0.09 + 0.12 * smoothstep(38, 0, lat)  # wider toward the mouth
    river = smoothstep(river_w, river_w * 0.6, rd)
    water = np.maximum(smoothstep(sea_level + 0.004, sea_level - 0.004, h), river)
    below = np.clip(sea_level - h, 0, None)
    print(f"water {time.time() - t0:.1f}s, {float((water > 0.5).mean()):.3f} of the surface")

    # --- Quadrants: hemispheres split by the equator and the 0°/180° meridian, blended over a
    # degree or two with a ragged edge (an old city's boundary isn't ruled straight). ---------
    # (fbm's spread is about ±0.17, so these swing the borders by ~6° with ~1° raggedness.)
    edge_n = 35.0 * fbm(n[1], p * 2.0 + warp, 4) + 5.0 * fbm(n[1], p * 40, 3)
    edge_e = 35.0 * fbm(n[2], p * 2.0 + warp, 4) + 5.0 * fbm(n[2], p * 40, 3)
    north = smoothstep(-3.0, 3.0, lat + edge_n)
    east = smoothstep(-0.05, 0.05, np.sin(np.radians(lon)) + np.radians(edge_e))
    G1 = north * (1 - east)
    G2 = north * east
    G3 = (1 - north) * (1 - east)
    G4 = (1 - north) * east

    # --- Chasm: a dark rift in G4, tapering at its ends. --------------------------------------
    c = unit(CHASM["lat"], CHASM["lon"])
    ce = np.cross([0, 0, 1.0], c)
    ce /= np.linalg.norm(ce)
    cn = np.cross(c, ce)
    br = np.radians(CHASM["bearing"])
    along_dir = np.cos(br) * cn + np.sin(br) * ce
    across_dir = np.cross(c, along_dir)
    along = np.degrees(p @ along_dir)
    across = np.degrees(p @ across_dir) + 0.25 * fbm(n[3], p * 50, 4)
    taper = np.clip(1 - (along / (CHASM["length"] / 2)) ** 2, 0, 1) * (p @ c > 0.9)
    half = CHASM["width"] / 2 * np.sqrt(taper) * (0.8 + 0.4 * fbm(n[4], p * 25, 3))
    chasm = smoothstep(0.05, -0.05, np.abs(across) - half) * (taper > 0)
    rim = smoothstep(0.5, 0.0, np.abs(across) - half) * (taper > 0) * (1 - chasm)

    # --- Density: hubs everywhere, thinning toward the poles into scrap and slag. ------------
    hubs = []
    while len(hubs) < 520:
        la = float(np.degrees(np.arcsin(rng.uniform(-0.93, 0.93))))
        lo = float(rng.uniform(-180, 180))
        iy = min(int((90 - la) / 180 * g.lat.shape[0]), g.lat.shape[0] - 1)
        ix = min(int((lo + 180) / 360 * width), width - 1)
        if water[iy, ix] > 0.5:
            continue
        size = min(float(rng.pareto(2.0) + 1) * 0.8, 5.0)
        hubs.append((la, lo, size, min(0.35 + 0.15 * size, 1.1)))
    hubs.append((1.0, 1.5, 3.0, 1.1))  # the hub around the river mouth: docks, Strip, University
    hubs.append((-1.0, -1.6, 2.2, 1.0))  # the Q3 port and bank
    density = np.zeros_like(h)
    ragged = fbm(n[4], p * 14 + warp * 2, 4)
    for la, lo, r, b in hubs:
        d = angular_distance(g, la, lo) * (1 + 0.9 * ragged)
        density = np.maximum(density, b * np.exp(-((d / r) ** 2)))
    sprawl = 0.25 + 0.35 * smoothstep(0.2, 0.85, rank(fbm(n[5], p * 7 + warp * 1.5, 5)))
    polar = smoothstep(84, 70, alat + 5 * fbm(n[6], p * 4, 3))  # 1 where the city is
    hubd = density * polar
    density = np.maximum(density, sprawl) * polar
    print(f"hubs {time.time() - t0:.1f}s")

    # --- Streets: district grids in the planned quadrants (G1, G3; G3's larger and more regular);
    # G2 half-planned; G4's are lost under the sprawl. -----------------------------------------
    inv, f1, f2 = districts(p, warp, rng, 900)
    big = np.maximum(grid_lines(p, f1, 0.024, 0.05)[0], grid_lines(p, f2, 0.024, 0.05)[0])
    sa, sx = grid_lines(p, f1, 0.006, 0.15)
    sb, sy = grid_lines(p, f2, 0.006, 0.15)
    streets = np.maximum(sa, sb)
    block = hashf(sx, sy, inv)
    gridness = 0.9 * G1 + 1.0 * G3 + 0.5 * G2 + 0.1 * G4
    street_mark = gridness * np.maximum(streets, 0.8 * big)
    print(f"streets {time.time() - t0:.1f}s")

    # Highways between neighbouring hubs; in G4 they're broken.
    xyz = np.array([unit(la, lo) for la, lo, _, _ in hubs])
    segs = []
    for i in range(len(hubs)):
        for j in np.argsort(-(xyz @ xyz[i]))[1:3]:
            if i < j:
                segs.append(((hubs[i][0], hubs[i][1]), (hubs[j][0], hubs[j][1]), 1.0))
    arteries = near_arcs(g, segs, 0.2) * polar
    strip = segment_distance(g, *STRIP)
    strip = smoothstep(0.35, 0.05, strip)
    print(f"arteries {time.time() - t0:.1f}s")

    # --- Day: grime and rust, no green anywhere. Rooftop speckle like any city; each quadrant
    # its own cast: G3 clean pale concrete and glass, G4 dark rust and soot with burnt blocks. --
    grain = rank(fbm(n[3], p * 380, 2))
    tone = 0.85 + 0.3 * block * (0.6 + 0.4 * gridness)
    tone = tone * (0.9 + 0.2 * grain) * (1 - 0.25 * street_mark * smoothstep(0.2, 0.7, density))
    tone = tone * (1 + 0.15 * smoothstep(0.3, 0.9, hubd))  # highways don't show by day at this scale
    cast = (
        G1[..., None] * np.array([0.36, 0.32, 0.28], np.float32)
        + G2[..., None] * np.array([0.39, 0.33, 0.29], np.float32)
        + G3[..., None] * np.array([0.44, 0.43, 0.42], np.float32)
        + G4[..., None] * np.array([0.27, 0.21, 0.17], np.float32)
    )
    burnt = G4 * smoothstep(0.55, 0.95, rank(fbm(n[7], p * 8 + warp, 5))) * (0.7 + 0.3 * block)
    city = cast * tone[..., None]
    city = city * (1 - 0.45 * burnt[..., None])
    # Toward the poles: scrapyards, slag heaps and landfill.
    scrap = ramp(rank(fbm(n[2], p * 10 + warp, 5)), [(0, (0.2, 0.16, 0.13)), (0.6, (0.36, 0.27, 0.2)), (1, (0.46, 0.38, 0.3))])
    scrap = scrap * (0.85 + 0.3 * grain[..., None])
    land = scrap * (1 - polar[..., None]) + city * polar[..., None]
    land = land * (1 - 0.9 * chasm[..., None]) + np.array([0.05, 0.04, 0.04], np.float32) * 0.9 * chasm[..., None]
    land = land * (1 - 0.3 * rim[..., None])
    deep = np.array([0.05, 0.08, 0.08], np.float32)
    shelf = np.array([0.14, 0.17, 0.13], np.float32)  # silted, polluted
    s = smoothstep(0.05, 0.0, below)[..., None] ** 2
    sea = deep * (0.9 + 0.2 * fbm(n[5], p * 9, 3)[..., None]) * (1 - s) + shelf * s
    sea = sea * (1 - river[..., None]) + np.array([0.13, 0.14, 0.1], np.float32) * river[..., None]
    rgb = land * (1 - water[..., None]) + sea * water[..., None]
    print(f"colour {time.time() - t0:.1f}s")

    # --- Night. -----------------------------------------------------------------------------
    sparkle = block**2.5 + 0.12
    lit = 1.5 * density * sparkle + 0.9 * hubd**1.3 * (0.6 + 0.4 * block)
    lit = lit * (0.75 + 0.25 * np.maximum(streets * gridness, big * smoothstep(0.1, 0.6, hubd)))
    lit = lit + 0.4 * arteries * (0.5 + 0.5 * smoothstep(0.4, 0.8, rank(fbm(n[7], p * 120, 2))))
    # Quadrant character.
    blackout = smoothstep(0.42, 0.3, rank(fbm(n[6], p * 9 + warp, 4)))  # G4's dark tracts
    flicker = smoothstep(0.5, 0.75, block)  # G4: only some blocks lit at all
    fires = smoothstep(0.985, 1.0, rank(fbm(n[1], p * 300, 2))) * smoothstep(0.1, 0.4, density)
    g4 = lit * 0.45 * flicker * (1 - 0.9 * blackout) + 0.9 * fires
    g2 = lit * 1.6 + 0.5 * hubd**1.2 + 1.8 * strip
    g3 = lit * (0.55 + 1.1 * smoothstep(0.3, 0.9, hubd))
    lit = G1 * lit * 0.95 + G2 * g2 + G3 * g3 + G4 * g4
    lit = lit * (1 - water) * (1 - chasm) * polar
    lit = lit + 0.35 * smoothstep(0.004, 0.0, np.abs(h - sea_level)) * smoothstep(0.2, 0.5, density) * (1 - G4)
    # G2's neon: a colour block by block among the white-gold, so from afar it mixes into a warm,
    # slightly rosy blaze (as Las Vegas does from orbit) and only close up shows its colours.
    # District-sized colour patches read as a quilt.
    pick = np.minimum((hashf(sx + 5, sy, inv) * len(NEON)).astype(int), len(NEON) - 1)
    coloured = (hashf(sy, sx + 9, inv) > 0.6)[..., None]
    neon = np.where(coloured, np.stack(NEON)[pick], WARM_WHITE)
    colour = (
        G1[..., None] * WARM_WHITE
        + G2[..., None] * neon
        + G3[..., None] * COOL_WHITE
        + G4[..., None] * SODIUM
    )
    colour = colour * (1 - fires[..., None] * G4[..., None]) + np.array([1.0, 0.45, 0.15], np.float32) * (fires * G4)[..., None]
    emissive = colour * np.clip(lit, 0, 1.4)[..., None] * 0.72
    print(f"lights {time.time() - t0:.1f}s")

    rough = np.where(water > 0.5, 0.4, 0.8 - 0.4 * G3 * smoothstep(0.3, 0.9, hubd))
    height = (0.6 * density + 0.15 * block * polar - 0.05 * streets * gridness) * (1 - water) * (1 - chasm)
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.004, strength=1.0))
    save_clouds(out, *genussa_clouds(g))
    write_pins(out / "pins.json", "Genussa", PINS)
    print(f"done {time.time() - t0:.1f}s -> {out}")


def genussa_clouds(g):
    """Little weather, but smog: a thin brown overcast everywhere, thicker over the cities'
    cores, and a few scattered clouds."""
    storms = [dict(lat=-46, lon=-60, ax=14, ay=9, swirl=1.0, inflow=0.5, strength=0.6, face=0.5, front=(-30, -85))]
    return make_clouds(g, SEED, cover=0.06, storms=storms, veil=(0.0, 0.08), zoning=0.2)


def save_clouds(out: Path, clouds, thickness) -> None:
    out.mkdir(parents=True, exist_ok=True)
    save_gray(out / "clouds.webp", clouds)
    save_rgb(out / "clouds-normal.webp", normal_map(thickness * 0.006, strength=1.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/genussa")
    args = ap.parse_args()
    generate(args.width, args.out)

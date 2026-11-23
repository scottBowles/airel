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
  with the Strip blazing; G3 crisp clean white, orderly, as bright as G1 with the brightest cores; G4 dim, broken,
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
COOL_WHITE = np.array([1.0, 0.96, 0.9], np.float32)  # G3: clean white (bluer read as snow, grey as frost)
ROSE = np.array([1.0, 0.62, 0.68], np.float32)  # G2's neon, as a drift of the whole blaze


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

    # --- Water: a few real seas, the bay and its arm, one river; nothing else. -------------
    # (Water from a global noise threshold scattered dozens of small lakes over every land,
    # which read as a lake-pocked desert.)
    seas = np.zeros(lat.shape, np.float32)
    for k, (la, lo, ax, ay) in enumerate(SEAS):
        # A core and lobes reaching out past it as arms and inlets, under a strongly warped shore.
        lobes = [(la, lo, ax * 0.85, ay * 0.85)] + [
            (la + rng.uniform(-1, 1) * ay * 0.8, lo + rng.uniform(-1, 1) * ax * 0.9, ax * rng.uniform(0.25, 0.5), ay * rng.uniform(0.25, 0.55))
            for _ in range(5)
        ]
        d = np.min([ellipse(g, *lb) for lb in lobes], axis=0)
        seas = np.maximum(seas, smoothstep(1.6, 0.8, d + 1.2 * fbm(n[4], p * 3 + warp * 2.5 + k, 5)))
    coast = 1.6 * fbm(n[5], p * 30 + warp * 2, 5)  # coves and points along the hub's shores
    for b in (BAY, BAY_ARM):
        seas = np.maximum(seas, smoothstep(1.3, 0.8, ellipse(g, b["lat"], b["lon"], b["ax"], b["ay"]) + coast))
    islet = smoothstep(0.45, 0.25, angular_distance(g, *ISLET) + 0.1 * fbm(n[6], p * 200, 3))  # the Orange Star's
    h = 0.5 + 0.08 * rank(fbm(n[3], p * 2.5 + warp * 1.3, 6)) - 0.6 * seas * (1 - islet)
    sea_level = 0.3
    # The river: one smooth, sinuous line from its source down to the mouth at (0, 0), wider
    # toward the mouth; drawn as short arcs along a curve, so no kinks.
    path = []
    for la in np.arange(38.0, 0.0, -0.4):
        lo = smoothstep(0, 4, la) * (1.4 * np.sin(la * 0.3) + 0.6 * np.sin(la * 0.83 + 1.3))
        path.append((float(la), float(lo)))
    path.append((0.15, 0.05))
    upper = [(a, b, 1.0) for a, b in zip(path[:-1], path[1:]) if a[0] > 12]
    lower = [(a, b, 1.0) for a, b in zip(path[:-1], path[1:]) if a[0] <= 12.4]
    river = np.maximum(smoothstep(0.35, 0.6, near_arcs(g, upper, 0.2)), smoothstep(0.35, 0.6, near_arcs(g, lower, 0.32)))
    water = np.maximum(smoothstep(sea_level + 0.02, sea_level - 0.02, h), river)
    below = np.clip(sea_level - h, 0, None)
    print(f"water {time.time() - t0:.1f}s, {float((water > 0.5).mean()):.3f} of the surface")

    # --- Quadrants: hemispheres split by the equator and the 0°/180° meridian. Their character is
    # a tendency, not a paint: it changes over ~8° on either side of a border that swings by
    # several degrees, and only at the hub do the four meet sharply. -----------------------
    # (fbm's spread is about ±0.17, so these swing the borders by ~6° with ~1° raggedness.)
    edge_n = 35.0 * fbm(n[1], p * 2.0 + warp, 4) + 5.0 * fbm(n[1], p * 40, 3)
    edge_e = 35.0 * fbm(n[2], p * 2.0 + warp, 4) + 5.0 * fbm(n[2], p * 40, 3)
    # At the hub the four meet exactly, so its places sit in the right quadrants.
    settle = smoothstep(1.5, 10.0, angular_distance(g, 0, 0))
    edge_n *= settle
    edge_e *= settle
    blend = 1.0 + 7.0 * settle  # degrees either side
    north = smoothstep(-blend, blend, lat + edge_n)
    east = smoothstep(-np.radians(blend), np.radians(blend), np.sin(np.radians(lon)) + np.radians(edge_e))
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
        size = min(float(rng.pareto(2.0) + 1) * 0.6, 4.0)
        b = min(0.35 + 0.15 * size, 1.1)
        if G4[iy, ix] > 0.5:  # the anarchy quadrant: fewer, weaker centres
            if rng.random() < 0.5:
                continue
            b *= 0.6
        hubs.append((la, lo, size, b))
    hubs.append((1.0, 1.5, 3.0, 0.8))  # the hub around the river mouth: docks, Strip, University
    hubs.append((-1.0, -1.6, 2.2, 0.75))  # the Q3 port and bank
    density = np.zeros_like(h)
    ragged = fbm(n[4], p * 14 + warp * 2, 4)
    for la, lo, r, b in hubs:
        d = angular_distance(g, la, lo) * (1 + 0.9 * ragged)
        density = np.maximum(density, b * np.exp(-((d / r) ** 2)))
    sprawl = 0.25 + 0.35 * smoothstep(0.2, 0.85, rank(fbm(n[5], p * 7 + warp * 1.5, 5)))
    polar = smoothstep(84, 70, alat + 30 * fbm(n[6], p * 4 + warp, 4))  # 1 where the city is
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
        for j in np.argsort(-(xyz @ xyz[i]))[1:4]:
            if i < j:
                segs.append(((hubs[i][0], hubs[i][1]), (hubs[j][0], hubs[j][1]), 1.0))
    # Corridors: broad, broken bands of sprawl along the roads between centres (the "web").
    gaps = smoothstep(0.15, 0.6, rank(fbm(n[7], p * 30 + warp, 3)))  # soft ends, not snapped sticks
    arteries = near_arcs(g, segs, 0.45) * polar * gaps
    strip = segment_distance(g, *STRIP)
    strip = smoothstep(0.35, 0.05, strip)
    print(f"arteries {time.time() - t0:.1f}s")

    # --- Day: grimy concrete, soot and asphalt, near-neutral grey (under the Red Sun a tan base
    # turned the whole planet into Mars). No street grid in the colour: blocks are ~100 m and a
    # texel is ~10 km, so a drawn grid reads as floor tiles. Texture comes from roof-tone speckle
    # at several scales; dense cores are darker (tall towers and their shadows); the quadrants
    # differ only a little: G3 cleaner and paler, G4 sootier. ---------------------------------
    grain = rank(fbm(n[3], p * 380, 2))
    mid = rank(fbm(n[2], p * 90 + warp, 3))
    core = smoothstep(0.3, 0.9, hubd)
    tone = (0.9 + 0.12 * grain) * (0.88 + 0.24 * mid) * (1 + 0.04 * (block - 0.5) * gridness)
    tone = tone * (1 - 0.22 * core) * (1 + 0.1 * arteries)
    base = np.array([0.3, 0.29, 0.28], np.float32)
    lift = 1 + 0.12 * G3 + 0.03 * G2 - 0.14 * G4
    cool = G3[..., None] * np.array([-0.01, 0.0, 0.015], np.float32) + G4[..., None] * np.array([0.015, 0.0, -0.015], np.float32)
    city = (base + cool) * (tone * lift)[..., None]
    soot = G4 * smoothstep(0.5, 0.9, rank(fbm(n[7], p * 4 + warp, 5)))  # derelict, burnt-out tracts
    city = city * (1 - 0.3 * soot[..., None])
    # Docks and fill along the shores: a thin paler band.
    shore = smoothstep(0.03, 0.0, np.abs(h - sea_level) - 0.01) * (1 - water)
    city = city * (1 - 0.3 * shore[..., None]) + np.array([0.42, 0.41, 0.39], np.float32) * 0.3 * shore[..., None]
    # Toward the poles: scrapyards, slag heaps and landfill, thinning out of the city.
    scrap = ramp(rank(fbm(n[2], p * 10 + warp, 5)), [(0, (0.18, 0.16, 0.15)), (0.6, (0.32, 0.29, 0.26)), (1, (0.42, 0.38, 0.34))])
    scrap = scrap * (0.85 + 0.3 * grain[..., None])
    land = scrap * (1 - polar[..., None]) + city * polar[..., None]
    land = land * (1 - 0.9 * chasm[..., None]) + np.array([0.05, 0.04, 0.04], np.float32) * 0.9 * chasm[..., None]
    land = land * (1 - 0.3 * rim[..., None])
    # One water colour, dark polluted grey-green, a little lighter in the shallows.
    deep = np.array([0.06, 0.08, 0.075], np.float32)
    shallow = np.array([0.11, 0.13, 0.11], np.float32)
    s = smoothstep(0.12, 0.0, below)[..., None]
    sea = deep * (1 - s) + shallow * s
    sea = sea * (1 - river[..., None]) + shallow * river[..., None]
    rgb = land * (1 - water[..., None]) + sea * water[..., None]
    print(f"colour {time.time() - t0:.1f}s")

    # --- Night. A web: glitter densest in the centres, broad broken corridors of light between
    # them, orange sodium along the corridors everywhere (the reference image's orange web).
    # Each quadrant by tendency: G1 even warm white; G2 the brightest, a rosy Vegas blaze with the
    # Strip; G3 crisp neutral white, orderly; G4 dim, broken, sodium orange, with blacked-out
    # tracts and scattered fires. -----------------------------------------------------------
    sparkle = 0.6 * block**2.5 + 0.4 * grain**3 + 0.1
    lit = 1.5 * density * sparkle + 0.6 * hubd**1.3 * (0.5 + 0.5 * sparkle)
    lit = lit * (0.8 + 0.2 * np.maximum(streets * gridness, big * smoothstep(0.1, 0.6, hubd)))
    web = 0.55 * arteries * (0.55 + 0.45 * grain)
    blackout = smoothstep(0.42, 0.3, rank(fbm(n[6], p * 9 + warp, 4)))  # G4's dark tracts
    flicker = smoothstep(0.5, 0.75, block)  # G4: only some blocks lit at all
    fires = smoothstep(0.985, 1.0, rank(fbm(n[1], p * 300, 2))) * smoothstep(0.1, 0.4, density)
    g4 = (lit * 0.5 * flicker + 0.6 * web) * (1 - 0.9 * blackout) + 0.9 * fires
    g2 = lit * 1.5 + 0.3 * hubd + web + 1.8 * strip
    # The money district: bright, even and clean. Its light follows the density smoothly, with
    # little of the block-by-block sparkle (which, white and grainy, read as frost).
    # Even: the gaps between dense districts are lit too (they read as camouflage when dark).
    calm = (0.35 + 0.65 * density) * (0.8 + 0.2 * block) + 0.5 * hubd**1.3
    g3 = (0.25 * lit + 0.6 * calm) * (1.0 + 0.6 * core) + 0.5 * web
    g1 = lit + web
    lit = G1 * g1 + G2 * g2 + G3 * g3 + G4 * g4
    # The crummy shore the party drove along: lights flicker, if they're on at all.
    crummy = smoothstep(1.9, 1.1, ellipse(g, BAY_ARM["lat"], BAY_ARM["lon"], BAY_ARM["ax"], BAY_ARM["ay"]))
    lit = lit * (1 - 0.6 * crummy * (1 - flicker))
    lit = lit * (1 - water) * (1 - chasm) * polar
    lit = lit + 0.3 * shore * smoothstep(0.2, 0.5, density) * (1 - G4)
    # Colour: the corridors orange; G2 drifts rosy in broad areas and on the Strip.
    rosy = np.clip(0.4 * smoothstep(0.4, 0.8, rank(fbm(n[5], p * 5 + warp, 4))) + strip, 0, 1)[..., None]
    g2c = WARM_WHITE * (1 - 0.5 * rosy) + ROSE * 0.5 * rosy
    colour = G1[..., None] * WARM_WHITE + G2[..., None] * g2c + G3[..., None] * COOL_WHITE + G4[..., None] * SODIUM
    corridor = np.clip(web / (lit + 1e-4), 0, 1)[..., None] * (1 - 0.6 * G3[..., None])
    colour = colour * (1 - corridor) + SODIUM * corridor
    colour = colour * (1 - fires[..., None] * G4[..., None]) + np.array([1.0, 0.45, 0.15], np.float32) * (fires * G4)[..., None]
    emissive = warm_dim(colour * np.clip(lit, 0, 1.3)[..., None] * 0.72, keep=G3)
    # The Orange Star's beacon: one small orange point on its islet.
    beacon = smoothstep(0.12, 0.0, angular_distance(g, *ISLET))
    emissive = emissive * (1 - beacon[..., None]) + np.array([1.0, 0.5, 0.15], np.float32) * beacon[..., None]
    print(f"lights {time.time() - t0:.1f}s")

    rough = np.where(water > 0.5, 0.4, 0.8 - 0.4 * G3 * core)
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


AMBER = np.array([1.0, 0.6, 0.28], np.float32)


def warm_dim(emissive: np.ndarray, keep: np.ndarray | None = None) -> np.ndarray:
    """Dim light drifts to amber. Warm white at low brightness is a dark yellow, which reads as
    olive-green (the follow-up review saw a mossy camouflage over G1 and G2 at night); real city
    light seen dimly from orbit is orange, as the dimmer lamps are sodium. Only the bright cores
    stay white. `keep` (0..1) exempts an area: G3's LED white stays white when dim, as neutral
    white dims to grey, not olive."""
    lum = emissive.mean(-1, keepdims=True)
    k = smoothstep(0.08, 0.4, lum)
    if keep is not None:
        k = np.maximum(k, keep[..., None])
    return emissive * k + AMBER * lum / float(AMBER.mean()) * (1 - k)


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

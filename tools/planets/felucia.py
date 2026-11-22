"""Felucia (the jungle world of the fey): generate texture maps and pins from the spec below.

    python3 tools/planets/felucia.py [--width 4096] [--out web/static/system/felucia]

Lore (see .ideas/projects/solar-system-3d/bodies/felucia.md and QUESTIONS.md):
- "Forest planet … Humid, colorful, jungle. Full of vibrance. A very hopeful kind of atmosphere."
- Mostly jungle with small seas, more water than Terran, enough to feed the jungle (DM, Nov 2026).
- "It's got the wildlands": a large chunk left undeveloped. One big region of the densest,
  darkest canopy, with no lights.
- Elves and fey, tradition blended with technology; libraries in nature. Soft, scattered town
  lights, far dimmer than Terran's.
- Rivers (a corporation "illegally diverting rivers"), hot springs in the jungle, and the
  volcano where Mazoë's sarcophagus was found.
- "Colorful" comes from the range of greens, emerald to lime and yellow-green. Accents of
  violet, crimson and autumn colour were tried; from orbit they read as burn scars or
  disease, not blooms, so the canopy stays green (user's call, Nov 2026).

No DB places have Felucia as parent, so every position is a guess, chosen to spread the
features readably. Longitude zero is arbitrary.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from clouds import billow, make_clouds, rank
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
    veins,
    write_pins,
)

SEED = 202
WATER = 0.24  # share of the surface under water

# Small seas: (lat, lon, radius°). Coasts come from the noise.
SEAS = [
    (5, -12, 11),  # the heartland's sea, where the great river ends
    (45, 72, 9),
    (-40, -40, 13),
    (-55, 160, 11),
    (-30, 80, 7),
    (28, -118, 12),
    (62, -25, 8),
    (-12, -125, 9),
    (20, 160, 6),
]
WILDLANDS = dict(lat=-10, lon=120, ax=35, ay=22)
ELVEN_FOREST = (35, -60)
HEARTLAND = dict(lat=15, lon=-20, ax=30, ay=20)
VOLCANO = (5, 40)
SPRINGS = (0, 44)

# Major rivers: (source, mouth), each with tributaries joining part-way down.
RIVERS = [
    ((6, 36), (5, -1)),  # the great river, from the volcanic highland west to the heartland's sea
    ((8, 118), (-25, 84)),  # through the wildlands
    ((-8, 150), (-46, 158)),
    ((40, -58), (30, -104)),  # down from the high elven forest
    ((22, 42), (42, 64)),
    ((-14, -18), (-31, -33)),
    ((50, -70), (60, -32)),
    ((-25, -80), (-16, -117)),
]

TOWNS = [  # (lat, lon, radius°, brightness): the larger settlements; villages are scattered
    (14, -16, 1.0, 1.0),  # library city on the sea
    (19, -27, 0.7, 0.8),
    (9, -2, 0.6, 0.7),  # at the great river's mouth
    (24, -8, 0.5, 0.6),
    (33, -55, 0.5, 0.6),  # in the high elven forest
    (29, -100, 0.5, 0.6),
    (-30, -34, 0.5, 0.5),
    (44, 60, 0.4, 0.5),
]

PINS = [
    dict(name="The Wildlands", lat=WILDLANDS["lat"], lon=WILDLANDS["lon"], confidence="guess"),
    dict(name="High elven forest", lat=ELVEN_FOREST[0], lon=ELVEN_FOREST[1], confidence="guess"),
    dict(name="Libraries of Felucia", lat=14, lon=-16, confidence="guess"),
    dict(name="Volcano of Mazoë's sarcophagus", lat=VOLCANO[0], lon=VOLCANO[1], confidence="guess"),
    dict(name="Hot springs", lat=SPRINGS[0], lon=SPRINGS[1], confidence="guess"),
]

LIGHT = np.array([1.0, 0.82, 0.55], np.float32)


def ellipse(g, lat, lon, ax, ay):
    dlat = (np.degrees(g.lat) - lat) / ay
    dlon = ((np.degrees(g.lon) - lon + 180) % 360 - 180) * np.cos(np.radians(lat)) / ax
    return np.sqrt(dlat**2 + dlon**2)


def meander(rng, a, b, depth=6, rough=0.28):
    """A river's course from a to b (lat, lon): midpoint displacement, so it wanders at every
    scale but always arrives."""
    pts = [np.array(a, float), np.array(b, float)]
    for level in range(depth):
        out = [pts[0]]
        for p, q in zip(pts[:-1], pts[1:]):
            d = q - p
            side = np.array([-d[1], d[0]])
            m = (p + q) / 2 + side * rng.normal(0, rough) * (0.85**level)
            out += [m, q]
        pts = out
    return pts


def river_field(g, rng, warp):
    """Distance (degrees) to the nearest river, and how big that river is there (1 at the mouth
    of a main stem, less up its tributaries)."""
    dist = np.full(g.lat.shape, 99.0, np.float32)
    size = np.zeros(g.lat.shape, np.float32)
    # Bend the map a little so courses curl, not only zig-zag.
    q = g.xyz + 0.006 * warp
    q /= np.linalg.norm(q, axis=-1, keepdims=True)
    lat = np.degrees(g.lat)
    lon = np.degrees(g.lon)
    systems = []
    for src, mouth in RIVERS:
        main = meander(rng, src, mouth)
        systems.append((main, 1.0))
        for _ in range(int(rng.integers(3, 6))):
            k = int(rng.integers(len(main) // 5, len(main) * 4 // 5))
            join = main[k]
            ang = rng.uniform(0, 2 * np.pi)
            ln = rng.uniform(4, 10)
            start = join + ln * np.array([np.sin(ang), np.cos(ang) / np.cos(np.radians(join[0]))])
            systems.append((meander(rng, start, join, depth=5), 0.55 * (k / len(main)) + 0.25))
    for pts, big in systems:
        for i, (p, r) in enumerate(zip(pts[:-1], pts[1:])):
            # Only the texels near this short segment.
            la0, la1 = min(p[0], r[0]) - 1, max(p[0], r[0]) + 1
            rows = np.where((lat[:, 0] >= la0) & (lat[:, 0] <= la1))[0]
            if not len(rows):
                continue
            c = np.cos(np.radians(np.clip(abs(p[0]) + 1, 0, 85)))
            lo0, lo1 = min(p[1], r[1]) - 1 / c, max(p[1], r[1]) + 1 / c
            cols = np.where((lon[0] >= lo0) & (lon[0] <= lo1))[0]
            if not len(cols):
                continue
            sub = q[rows[0] : rows[-1] + 1, cols[0] : cols[-1] + 1]
            pa, pb = unit(*p), unit(*r)
            ab = pb - pa
            t = np.clip(((sub - pa) @ ab) / max(float(ab @ ab), 1e-12), 0, 1)
            near = pa + t[..., None] * ab
            d = np.degrees(np.linalg.norm(sub - near, axis=-1))
            s = big * (0.35 + 0.65 * (i + t) / (len(pts) - 1))  # wider downstream
            view = (slice(rows[0], rows[-1] + 1), slice(cols[0], cols[-1] + 1))
            better = d < dist[view]
            dist[view] = np.where(better, d, dist[view])
            size[view] = np.where(better, s, size[view])
    return dist, size


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n = [Noise3(SEED * 10 + i) for i in range(8)]
    p = g.xyz
    lat = np.degrees(g.lat)

    # One warped field shapes the land, its highlands, the seas' coasts and the canopy.
    warp = np.stack([fbm(n[0], p * 1.6 + 11, 5), fbm(n[1], p * 1.6 + 23, 5), fbm(n[2], p * 1.6 + 37, 5)], -1)
    base = rank(fbm(n[3], p * 3.0 + warp * 1.3, octaves=8))
    ridges = ridged(n[4], p * 5.0 + warp * 1.0, octaves=6)
    h = base + 0.25 * (ridges - 0.5)
    # The seas: basins pressed into the field, their coasts left to the noise.
    for la, lo, r in SEAS:
        d = angular_distance(g, la, lo) / r
        h = h - 0.75 * smoothstep(1.6, 0.2, d)
    # The wildlands and the settled heartland are unbroken land; highlands around the volcano
    # and under the high elven forest.
    for spec, lift in ((WILDLANDS, 0.35), (HEARTLAND, 0.15)):
        h = h + lift * smoothstep(1.2, 0.6, ellipse(g, spec["lat"], spec["lon"], spec["ax"], spec["ay"]))
    highland = smoothstep(14, 3, angular_distance(g, *VOLCANO) + 6 * fbm(n[5], p * 6 + warp, 4))
    highland = np.maximum(highland, 0.7 * smoothstep(16, 5, angular_distance(g, *ELVEN_FOREST) + 7 * fbm(n[6], p * 6 + warp, 4)))
    h = h + 0.35 * highland * (0.6 + 0.6 * ridges)
    cone_d = angular_distance(g, *VOLCANO)
    cone = np.exp(-((cone_d / 1.8) ** 2)) - 0.5 * np.exp(-((cone_d / 0.3) ** 2))  # with a crater
    h = h + 0.5 * cone
    sea_level = np.quantile(h, WATER)
    print(f"field {time.time() - t0:.1f}s")

    rdist, rsize = river_field(g, rng, warp)
    width_deg = 0.04 + 0.08 * rsize  # a main stem is ~2 texels wide at its mouth
    river = smoothstep(width_deg, width_deg * 0.4, rdist) * smoothstep(0.03, 0.08, h - sea_level)
    flood = smoothstep(0.9 * rsize + 0.3, 0.0, rdist)  # the floodplain each side
    h = h - 0.05 * flood - 0.03 * river
    print(f"rivers {time.time() - t0:.1f}s")

    water = np.maximum(smoothstep(sea_level + 0.004, sea_level - 0.004, h), river)
    below = np.clip(sea_level - h, 0, None)
    e = np.clip((h - sea_level) / (np.quantile(h, 0.995) - sea_level), 0, 1)
    # Dissected land: stream valleys at three scales (the zero-crossings of noise make
    # connected, winding lines), deeper in the hills. From orbit, drainage etched into the
    # canopy is most of what gives a forest its texture.
    w2 = np.stack([fbm(n[3], p * 8 + 5, 3), fbm(n[6], p * 8 + 9, 3), fbm(n[2], p * 8 + 3, 3)], -1)
    valleys = np.maximum.reduce(
        [
            veins(n[4], p * 9 + warp * 2 + w2 * 0.6, 0.08),
            0.7 * veins(n[5], p * 22 + warp * 3 + w2 * 0.8, 0.09),
            0.45 * veins(n[7], p * 55 + warp * 4 + w2, 0.1),
        ]
    ) * (0.45 + 0.55 * smoothstep(0.0, 0.5, e))
    print(f"relief {time.time() - t0:.1f}s")

    # Seas: clear tropical water, turquoise on the shelves, deep blue-green in the basins.
    deep = np.array([0.03, 0.15, 0.24], np.float32)
    mid = np.array([0.04, 0.26, 0.33], np.float32)
    shelf = np.array([0.12, 0.42, 0.42], np.float32)
    swell = fbm(n[5], p * 9 + warp * 1.5, 4)[..., None]
    water_rgb = deep * (0.9 + 0.25 * swell)
    water_rgb = water_rgb * (1 - smoothstep(0.08, 0.0, below)[..., None]) + mid * smoothstep(0.08, 0.0, below)[..., None]
    s2 = smoothstep(0.06, 0.0, below)[..., None] ** 2
    water_rgb = water_rgb * (1 - 0.7 * s2) + shelf * 0.7 * s2
    # Jungle rivers run brown-green with silt.
    silt = np.array([0.16, 0.2, 0.12], np.float32)
    water_rgb = np.where((river > 0.01)[..., None] & (below[..., None] <= 0), silt, water_rgb)

    # Canopy: mostly deep rainforest green, as jungle is from orbit, varied in patches by a
    # biome field built from the same warp; the lighter yellow-greens only in its top tenth
    # (younger growth and clearings) and along the rivers.
    biome = rank(fbm(n[6], p * 4.5 + warp * 1.6, 6))
    patch = fbm(n[7], p * 14 + warp * 2.5, 5)
    green = ramp(
        biome,
        [
            (0.0, (0.02, 0.15, 0.06)),
            (0.4, (0.04, 0.23, 0.08)),
            (0.72, (0.07, 0.3, 0.08)),
            (0.88, (0.18, 0.4, 0.07)),
            (1.0, (0.34, 0.5, 0.08)),
        ],
    )
    green = green * (0.85 + 0.3 * patch[..., None])
    # Higher ground is darker old growth; the floodplains are bright and fresh.
    old = smoothstep(0.35, 0.8, e)[..., None]
    green = green * (1 - 0.5 * old) + np.array([0.05, 0.17, 0.08], np.float32) * 0.5 * old
    green = green * (1 - 0.5 * flood[..., None]) + np.array([0.26, 0.45, 0.1], np.float32) * 0.5 * flood[..., None]
    # The wildlands: the densest, darkest canopy.
    wild = smoothstep(1.15, 0.75, ellipse(g, WILDLANDS["lat"], WILDLANDS["lon"], WILDLANDS["ax"], WILDLANDS["ay"]) + 0.25 * fbm(n[1], p * 5 + warp, 4))
    green = green * (1 - 0.55 * wild[..., None]) + np.array([0.04, 0.15, 0.07], np.float32) * 0.55 * wild[..., None]
    crowns = billow(n[1], p * 90 + warp * 3, 3)  # tree crowns, used for the canopy's texture below
    # Volcanic rock on the cone, pale steaming ground at the springs, and a little tundra and
    # ice only at the poles.
    # Old lava flows run down the flanks as dark tongues; the cone's top is bare.
    ang = np.arctan2(*(np.stack([lat - VOLCANO[0], (np.degrees(g.lon) - VOLCANO[1]) * np.cos(np.radians(VOLCANO[0]))])))
    tongues = smoothstep(0.3, 0.8, fbm(n[6], np.stack([np.cos(ang) * 3, np.sin(ang) * 3, cone_d * 0.4], -1), 3) + 0.5)
    rock = np.maximum(smoothstep(1.6, 0.7, cone_d), 0.7 * tongues * smoothstep(4.5, 1.2, cone_d))[..., None]
    green = green * (1 - 0.8 * rock) + np.array([0.2, 0.17, 0.15], np.float32) * 0.8 * rock
    springs = smoothstep(1.2, 0.0, angular_distance(g, *SPRINGS) + 0.8 * fbm(n[5], p * 60, 3))[..., None]
    green = green * (1 - 0.5 * springs) + np.array([0.55, 0.6, 0.5], np.float32) * 0.5 * springs
    polar = smoothstep(80, 87, np.abs(lat) + 5 * fbm(n[0], p * 6, 4))[..., None]
    green = green * (1 - polar) + np.array([0.75, 0.78, 0.76], np.float32) * polar
    # The canopy seen from above: tree crowns bunched into clumps, with shaded gaps.
    grain = fbm(n[2], p * 400, 2)
    # Valleys sit in shade under taller, denser trees; ridges catch light.
    land = green * (0.8 + 0.3 * crowns[..., None] + 0.08 * grain[..., None]) * (1 - 0.22 * valleys[..., None])
    rgb = land * (1 - water[..., None]) + water_rgb * water[..., None]
    print(f"colour {time.time() - t0:.1f}s")

    # Lights: warm, soft and scattered, mostly in the heartland and along the rivers and
    # coasts; none in the wildlands.
    lights = np.zeros_like(h)
    sprawl = fbm(n[3], p * 300, 3)
    for la, lo, r, b in TOWNS:
        t = angular_distance(g, la, lo) / r
        near = t < 1.6
        core = smoothstep(1.6, 0.0, t[near])
        lights[near] += b * core * smoothstep(0.1 - 0.3 * core, 0.4, sprawl[near])
    heart = smoothstep(1.3, 0.3, ellipse(g, HEARTLAND["lat"], HEARTLAND["lon"], HEARTLAND["ax"], HEARTLAND["ay"]))
    settled = np.maximum(0.8 * heart, 0.45 * smoothstep(0.5, 0.85, rank(fbm(n[5], p * 5 + warp + 1.1, 4))))
    waterside = np.maximum(smoothstep(1.2, 0.0, rdist), smoothstep(0.04, 0.0, h - sea_level))
    villages = smoothstep(0.84, 0.95, rank(fbm(n[6], p * 420 + 2.9, 2)))
    lights += 0.9 * settled * (0.3 + 0.7 * waterside) * villages
    lights = np.clip(lights, 0, 1.2) * (1 - water) * (1 - wild) * (1 - polar[..., 0])
    emissive = LIGHT * lights[..., None]
    print(f"lights {time.time() - t0:.1f}s")

    rough = np.where(water > 0.5, 0.45, 0.88)
    height = (e - 0.06 * valleys) * (1 - water)
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.025, strength=1.0))
    save_clouds(out, *felucia_clouds(g))
    write_pins(out / "pins.json", "Felucia", PINS)
    print(f"done {time.time() - t0:.1f}s -> {out}, water {float((water > 0.5).mean()):.3f}")


def felucia_clouds(g):
    """Humid: white cumulus over the jungle, gathered into clusters near the equator and a few
    weak systems, more cloud than Earth but far less than Hyang Wan, with low haze."""
    storms = [
        dict(lat=42, lon=-150, ax=18, ay=12, swirl=1.3, inflow=0.6, face=0.6, front=(24, -175)),
        dict(lat=-46, lon=60, ax=16, ay=11, swirl=-1.2, inflow=0.5, strength=0.8, face=-0.6, front=(-28, 40)),
        dict(lat=12, lon=95, ax=5, ay=5, swirl=2.2, inflow=1.2, eye=1.0, strength=3.0, round=True),
        dict(lat=55, lon=20, ax=12, ay=9, swirl=1.0, inflow=0.4, strength=0.6, eye=0),
    ]
    return make_clouds(g, SEED, cover=0.3, storms=storms, veil=(0.04, 0.14), zoning=0.3)


def save_clouds(out: Path, clouds, thickness) -> None:
    out.mkdir(parents=True, exist_ok=True)
    save_gray(out / "clouds.webp", clouds)
    save_rgb(out / "clouds-normal.webp", normal_map(thickness * 0.006, strength=1.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/felucia")
    ap.add_argument("--clouds-only", action="store_true", help="regenerate just the cloud layer")
    args = ap.parse_args()
    if args.clouds_only:
        save_clouds(args.out, *felucia_clouds(make_grid(args.width)))
    else:
        generate(args.width, args.out)

"""Terran (the planet-wide metropolis): generate texture maps and pins from the spec below.

    python3 tools/planets/terran.py [--width 4096] [--out web/static/system/terran]

Lore (see .ideas/projects/solar-system-3d/bodies/terran.md and QUESTIONS.md):
- "Planet-Sized Metropolis." "Coruscant with Caprica … metropolis on top of metropolis."
  "Centralized planet, probably most populated." Super high-tech; "America in the fifties
  with technology"; a police state where no unrest is allowed.
- "They have a parks initiative, but it's like the city of Chicago spread across a whole
  planet": street grids, with parks as green squares.
- Some seas, but not many; the city covers most of the planet (DM, Nov 2026).
- Champion City, "like Demolition Man above world": the Senate ("the seat is power") and the
  Arena where Raltak waits. The brightest hub on the night side.
- "The Whidmore Corp. playground for developing terraforming": a patchwork of unlike biomes.

From orbit a city is grey-tan by day, a mosaic of districts whose street grids run different
ways; at night it is a web of gold lights, densest in the hubs and along the arteries between
them. Positions are guesses except where tied to Champion City. Longitude zero is the capital.
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
    smoothstep,
    unit,
    worley,
    write_pins,
)

SEED = 303
WATER = 0.075  # "some seas, but not many"

CHAMPION = (42, 0)
SENATE = (42.3, 0.6)
ARENA = (41.6, 1.4)
LAKE = dict(lat=40, lon=11, ax=7, ay=3.5)  # Champion City's lakefront, as Chicago's
SEAS = [  # (lat, lon, half-width lon°, half-height lat°)
    (-15, -70, 18, 11),
    (10, 150, 14, 8),
    (-48, 55, 10, 6),
]
TESTBED = dict(lat=-20, lon=120, ax=10, ay=7)  # Whidmore's terraforming patchwork

PINS = [
    dict(name="Champion City", lat=CHAMPION[0], lon=CHAMPION[1], confidence="guess"),
    dict(name="The Senate", lat=SENATE[0], lon=SENATE[1], confidence="guess"),
    dict(name="The Arena", lat=ARENA[0], lon=ARENA[1], confidence="layout"),
    dict(name="Whidmore terraforming testbed", lat=TESTBED["lat"], lon=TESTBED["lon"], confidence="guess"),
]

WARM = np.array([1.0, 0.78, 0.45], np.float32)  # sodium-gold
COOL = np.array([0.9, 0.93, 1.0], np.float32)  # the newest districts' white light


def ellipse(g, lat, lon, ax, ay):
    dlat = (np.degrees(g.lat) - lat) / ay
    dlon = ((np.degrees(g.lon) - lon + 180) % 360 - 180) * np.cos(np.radians(lat)) / ax
    return np.sqrt(dlat**2 + dlon**2)


def grid_lines(p, a, spacing, width):
    """Lines every `spacing` radians across direction a (per texel), 0..1, width as a fraction."""
    t = (p * a).sum(-1) / spacing
    d = np.abs(t - np.round(t))
    return smoothstep(width, width * 0.3, d), np.floor(t)


def near_arcs(g, segs, width):
    """Distance-based glow (0..1) along great-circle segments, computed only near each one."""
    out = np.zeros(g.lat.shape, np.float32)
    lat = np.degrees(g.lat[:, 0])
    lon = np.degrees(g.lon[0])
    for a, b, w in segs:
        pa, pb = unit(*a), unit(*b)
        # A short arc: sample its bounding box (wrapping in longitude when it crosses ±180).
        n = max(2, int(np.degrees(np.arccos(np.clip(pa @ pb, -1, 1))) / 3) + 1)
        for i in range(n - 1):
            q0 = pa + (pb - pa) * (i / (n - 1))
            q1 = pa + (pb - pa) * ((i + 1) / (n - 1))
            q0, q1 = q0 / np.linalg.norm(q0), q1 / np.linalg.norm(q1)
            la = np.degrees(np.arcsin([q0[2], q1[2]]))
            lo = np.degrees(np.arctan2([q0[1], q1[1]], [q0[0], q1[0]]))
            pad = 0.6
            rows = np.where((lat >= la.min() - pad) & (lat <= la.max() + pad))[0]
            if abs(lo[0] - lo[1]) > 180:
                lo = np.where(lo < 0, lo + 360, lo)
            c = 1 / max(np.cos(np.radians(min(abs(la).max() + pad, 85))), 0.1)
            span = (lon - (lo.min() - pad * c)) % 360
            cols = np.where(span <= (lo.max() - lo.min()) + 2 * pad * c)[0]
            if not len(rows) or not len(cols):
                continue
            sub = g.xyz[rows[0] : rows[-1] + 1][:, cols]
            ab = q1 - q0
            t = np.clip(((sub - q0) @ ab) / max(float(ab @ ab), 1e-12), 0, 1)
            d = np.degrees(np.linalg.norm(sub - (q0 + t[..., None] * ab), axis=-1))
            v = w * smoothstep(width, 0, d)
            view = out[rows[0] : rows[-1] + 1][:, cols]
            out[rows[0] : rows[-1] + 1, cols] = np.maximum(view, v)
    return out


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n = [Noise3(SEED * 10 + i) for i in range(8)]
    p = g.xyz
    lat = np.degrees(g.lat)
    alat = np.abs(lat)

    # Land and the few seas, from one warped field; the seas are basins pressed into it.
    warp = np.stack([fbm(n[0], p * 1.6 + 11, 5), fbm(n[1], p * 1.6 + 23, 5), fbm(n[2], p * 1.6 + 37, 5)], -1)
    # The noise only shapes coasts and a few lakes; the seas come from the basins.
    h = 0.35 * rank(fbm(n[3], p * 2.5 + warp * 1.3, 7))
    for la, lo, ax, ay in SEAS:
        h = h - 0.9 * smoothstep(1.5, 0.3, ellipse(g, la, lo, ax, ay) + 0.3 * fbm(n[4], p * 6 + warp, 4))
    h = h - 0.9 * smoothstep(1.2, 0.5, ellipse(g, LAKE["lat"], LAKE["lon"], LAKE["ax"], LAKE["ay"]) + 0.2 * fbm(n[4], p * 12 + warp, 4))
    # Keep the capital and the testbed on land.
    h = h + 0.6 * smoothstep(8, 3, angular_distance(g, *CHAMPION))
    h = h + 0.5 * smoothstep(1.4, 0.8, ellipse(g, TESTBED["lat"], TESTBED["lon"], TESTBED["ax"], TESTBED["ay"]))
    sea_level = np.quantile(h, WATER)
    water = smoothstep(sea_level + 0.004, sea_level - 0.004, h)
    below = np.clip(sea_level - h, 0, None)
    print(f"land {time.time() - t0:.1f}s")

    # Cities: Champion City, then a few hundred lesser hubs, big and small, never in the sea.
    hubs = [(CHAMPION[0], CHAMPION[1], 7.0, 1.6)]
    while len(hubs) < 420:
        la = float(np.degrees(np.arcsin(rng.uniform(-0.93, 0.93))))
        lo = float(rng.uniform(-180, 180))
        r, c = np.radians(90 - la), np.radians(lo)
        iy = min(int((90 - la) / 180 * g.lat.shape[0]), g.lat.shape[0] - 1)
        ix = min(int((lo + 180) / 360 * width), width - 1)
        if water[iy, ix] > 0.5:
            continue
        size = float(rng.pareto(2.2) + 1) * 0.9
        hubs.append((la, lo, min(size, 5.0), min(0.35 + 0.15 * size, 1.1)))
    density = np.zeros_like(h)
    # Hubs sprawl unevenly along their coasts and corridors, not in circles.
    ragged = fbm(n[4], p * 14 + warp * 2, 4)
    # Big hubs get wheels: ring roads (beltways) and radial highways, like DC's or Moscow's,
    # at city-planet scale and a little out of round.
    wheels = np.zeros_like(h)
    for i, (la, lo, r, b) in enumerate(hubs):
        d0 = angular_distance(g, la, lo)
        d = d0 * (1 + 0.9 * ragged)
        density = np.maximum(density, b * np.exp(-((d / r) ** 2)))
        if i == 0 or r < 1.8:
            continue
        c = unit(la, lo)
        e = np.cross([0, 0, 1.0], c)
        e /= np.linalg.norm(e)
        nn = np.cross(c, e)
        near = d0 < r * 1.6
        dw = d0[near] * (1 + 0.06 * ragged[near])
        ang = np.arctan2(p[near] @ nn, p[near] @ e)
        w = 0.16
        ring = np.maximum(smoothstep(w, 0, np.abs(dw - 0.4 * r)), smoothstep(w, 0, np.abs(dw - 0.85 * r)) * (r > 2.6))
        k = int(rng.integers(5, 9))
        phase = rng.uniform(0, np.pi)
        spoke = smoothstep(w, 0, dw * np.abs(np.sin((ang - phase) * k / 2))) * smoothstep(0.1 * r, 0.25 * r, dw) * smoothstep(1.5 * r, 1.0 * r, dw)
        wheels[near] = np.maximum(wheels[near], b * np.maximum(ring, spoke))
    # The urban sprawl between hubs is everywhere, thinning toward the poles.
    # It is patchy: dense suburbs, industry, and darker tracts between.
    base = 0.2 + 0.35 * smoothstep(0.2, 0.85, rank(fbm(n[5], p * 7 + warp * 1.5, 5)))
    polar_thin = smoothstep(82, 66, alat + 4 * fbm(n[6], p * 4, 3))
    hubd = density * polar_thin
    density = np.maximum(density, base) * polar_thin
    print(f"hubs {time.time() - t0:.1f}s")

    # Districts: each one's street grid runs its own way (Chicago's grid, turned district by
    # district), so the city is a mosaic, not a planet-wide graticule.
    _, _, cid = worley(p * 9 + warp * 0.6, SEED)
    # Each district's grid is laid out in its own tangent plane: axes perpendicular to the
    # district's centre, turned by a random angle. Laid out on random 3D axes instead, a grid
    # stretches into long strips wherever an axis points nearly straight up.
    labels, inv = np.unique(cid, return_inverse=True)
    inv = inv.reshape(cid.shape)
    centre = np.stack([np.bincount(inv.ravel(), p[..., k].ravel(), len(labels)) for k in range(3)], -1)
    centre /= np.linalg.norm(centre, axis=-1, keepdims=True) + 1e-9
    any_dir = np.where(np.abs(centre[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    e1 = np.cross(any_dir, centre)
    e1 /= np.linalg.norm(e1, axis=-1, keepdims=True)
    e2 = np.cross(centre, e1)
    turn = rng.uniform(0, np.pi, len(labels))[:, None]
    a1 = (e1 * np.cos(turn) + e2 * np.sin(turn)).astype(np.float32)
    a2 = (-e1 * np.sin(turn) + e2 * np.cos(turn)).astype(np.float32)
    fr = np.stack([a1[inv], a2[inv]], -2)
    print(f"districts {time.time() - t0:.1f}s")
    big_a, bx = grid_lines(p, fr[..., 0, :], 0.024, 0.05)
    big_b, by = grid_lines(p, fr[..., 1, :], 0.024, 0.05)
    avenues = np.maximum(big_a, big_b)
    small_a, sx = grid_lines(p, fr[..., 0, :], 0.006, 0.15)
    small_b, sy = grid_lines(p, fr[..., 1, :], 0.006, 0.15)
    streets = np.maximum(small_a, small_b)
    # Each block a little different: rooftops, plazas, towers.
    def hashf(*v):
        x = np.zeros_like(v[0], dtype=np.int64)
        for i, a in enumerate(v):
            x = x ^ (a.astype(np.int64) * (73856093 + 19349663 * i))
        x = (x ^ (x >> 13)) * 1274126177
        return ((x ^ (x >> 16)) & 0xFFFF).astype(np.float32) / 0xFFFF

    block = hashf(sx, sy, (cid * 1000).astype(np.int64))

    # Champion City: rings of boulevards and radial avenues, the Senate and the Arena.
    cd = angular_distance(g, *CHAMPION)
    c = unit(*CHAMPION)
    east = np.cross([0, 0, 1], c)
    east /= np.linalg.norm(east)
    north = np.cross(c, east)
    ang = np.arctan2(p @ north, p @ east)
    rings = smoothstep(0.08, 0.02, np.abs((cd / 1.1) - np.round(cd / 1.1))) * smoothstep(9, 1, cd)
    spokes = smoothstep(0.04, 0.0, np.abs(np.sin(ang * 8)) * cd / 8) * smoothstep(12, 0.5, cd)
    monuments = np.maximum(
        smoothstep(0.08, 0.0, np.abs(angular_distance(g, *SENATE) - 0.3)),
        smoothstep(0.06, 0.0, np.abs(angular_distance(g, *ARENA) - 0.2)),
    )
    avenues = np.maximum(avenues, np.maximum(rings, spokes))
    print(f"grid {time.time() - t0:.1f}s")

    # Arteries: each hub joined to its nearest neighbours by long straight transit lines.
    xyz = np.array([unit(la, lo) for la, lo, _, _ in hubs])
    segs = []
    for i in range(len(hubs)):
        dots = xyz @ xyz[i]
        for j in np.argsort(-dots)[1:3]:
            if i < j or i not in np.argsort(-(xyz @ xyz[j]))[1:3]:
                segs.append(((hubs[i][0], hubs[i][1]), (hubs[j][0], hubs[j][1]), 1.0))
    arteries = 0.5 * near_arcs(g, segs, 0.22)
    # Trunk lines: the biggest hubs joined to each other across continents, brighter and wider.
    top = sorted(range(len(hubs)), key=lambda i: -hubs[i][2])[:32]
    txyz = xyz[top]
    trunks = []
    for a_ in range(len(top)):
        for b_ in np.argsort(-(txyz @ txyz[a_]))[1:3]:
            if a_ < b_:
                i, j = top[a_], top[b_]
                trunks.append(((hubs[i][0], hubs[i][1]), (hubs[j][0], hubs[j][1]), 1.0))
    arteries = np.maximum(arteries, near_arcs(g, trunks, 0.32))
    print(f"arteries {time.time() - t0:.1f}s: {len(segs)} lines, max {float(arteries.max()):.2f}, cover {float((arteries > 0.1).mean()):.4f}")

    # Parks: greenbelts kept along old river valleys and irregular preserved parkland, shaped
    # like nature rather than plots; rectangular planned parks only in the dense cores; a ring
    # of parks around the capital, and the lakefront strip.
    belts = smoothstep(0.035, 0.012, np.abs(fbm(n[6], p * 5 + warp * 1.2, 4)))
    belts = belts * smoothstep(0.35, 0.6, rank(fbm(n[7], p * 3 + 4.4, 3)))
    wild = smoothstep(0.93, 0.97, rank(fbm(n[2], p * 9 + warp * 2, 5)))
    planned = (hashf(bx, by, (cid * 1000).astype(np.int64) + 3) > 0.97) * smoothstep(0.35, 0.6, hubd)
    parks = np.maximum(np.maximum(belts, wild), planned).astype(np.float32)
    ring_d = np.abs(cd - 9)
    parks = np.maximum(parks, smoothstep(1.2, 0.6, ring_d) * (np.sin(ang * 4) > 0.2))
    shore = smoothstep(0.02, 0.0, np.abs(h - sea_level) - 0.004) * smoothstep(14, 4, cd)
    parks = np.maximum(parks, shore) * (1 - water)
    testbed = smoothstep(1.1, 0.9, ellipse(g, TESTBED["lat"], TESTBED["lon"], TESTBED["ax"], TESTBED["ay"]))
    ice = smoothstep(78, 86, alat + 3 * fbm(n[7], p * 8, 3))

    # Day: no flat tints (even-toned patches read as farm fields); instead the fine bright and
    # dark speckle of rooftops and shadows, silvery in the cores, darker grey in the sprawl.
    core = smoothstep(0.25, 1.0, hubd)
    grain = rank(fbm(n[3], p * 380, 2))
    v = (0.33 + 0.17 * core) * (0.8 + 0.28 * block) * (0.88 + 0.24 * grain)
    v = v * (1 - 0.3 * streets * smoothstep(0.2, 0.7, density)) * (1 - 0.1 * avenues)
    v = v * (1 - 0.35 * np.maximum(wheels, arteries))  # highways are dark bands by day
    city = v[..., None] * np.array([0.98, 1.0, 1.04], np.float32)
    city = city * (1 - 0.3 * monuments[..., None]) + 0.7 * monuments[..., None]
    # Only near the poles does the city thin out to bare tundra.
    ground = ramp(rank(fbm(n[2], p * 8 + warp, 4)), [(0, (0.44, 0.45, 0.44)), (1, (0.55, 0.56, 0.55))])
    built = polar_thin[..., None]
    land = ground * (1 - built) + city * built
    park = np.array([0.17, 0.27, 0.13], np.float32) * (0.8 + 0.4 * block[..., None]) * (0.85 + 0.3 * grain[..., None])
    land = land * (1 - parks[..., None]) + park * parks[..., None]
    patch_id = hashf(bx, by, (cid * 1000).astype(np.int64) + 7)
    patches = ramp(patch_id, [(0, (0.62, 0.52, 0.36)), (0.3, (0.14, 0.32, 0.12)), (0.55, (0.82, 0.85, 0.86)), (0.8, (0.42, 0.44, 0.24)), (1, (0.3, 0.22, 0.16))])
    land = land * (1 - testbed[..., None]) + patches * testbed[..., None]
    land = land * (1 - ice[..., None]) + np.array([0.8, 0.83, 0.86], np.float32) * ice[..., None]

    deep = np.array([0.03, 0.1, 0.18], np.float32)
    shelf = np.array([0.08, 0.26, 0.32], np.float32)
    s = smoothstep(0.05, 0.0, below)[..., None] ** 2
    sea = deep * (0.9 + 0.2 * fbm(n[5], p * 9, 3)[..., None]) * (1 - s) + shelf * s
    rgb = land * (1 - water[..., None]) + sea * water[..., None]
    print(f"colour {time.time() - t0:.1f}s")

    # Night: lights wherever people are, strongest in the hubs, traced along streets and avenues,
    # with the arteries as bright threads between cities.
    # The sprawl glows faintly everywhere; the hubs blaze.
    # Nearly everywhere is lit like an Earth city; the hubs blaze like megacity cores.
    # Glitter, not a wash: each block lit brightly or dimly, so the sprawl sparkles with dark
    # gaps between lit blocks (as real cities do from orbit), while hub cores fill in solid.
    sparkle = block**2.5 + 0.12
    lit = (1.6 * density * sparkle + 1.0 * hubd**1.3 * (0.6 + 0.4 * block)) * (0.75 + 0.25 * np.maximum(streets, avenues * smoothstep(0.1, 0.6, hubd)))
    # Transit lines: faint broken strings of light, brighter where they pass through towns.
    strings = 0.7 * arteries * (0.5 + 0.5 * smoothstep(0.4, 0.8, rank(fbm(n[7], p * 120, 2))))
    lit = lit + 0.35 * avenues * hubd**1.5 + strings + 0.6 * wheels + 0.8 * rings * smoothstep(9, 0, cd) + 1.2 * monuments
    lit = lit * (1 - water) * (1 - parks * 0.85) * (1 - testbed) * (1 - ice)
    # Coastal promenades light the shore.
    lit = lit + 0.3 * smoothstep(0.004, 0.0, np.abs(h - sea_level)) * smoothstep(0.2, 0.5, density)
    hue = 0.6 * smoothstep(0.7, 0.9, rank(fbm(n[1], p * 6 + 2.2, 3)))[..., None]
    emissive = (WARM * (1 - hue) + COOL * hue) * np.clip(lit, 0, 1.4)[..., None] * 0.75
    # Lit windows tint the city a touch by day as well.
    print(f"lights {time.time() - t0:.1f}s")

    # Glass and steel in the cores catch the sun.
    rough = np.where(water > 0.5, 0.35, 0.75 - 0.5 * core * (0.5 + 0.5 * block))
    height = (0.6 * density + 0.15 * block * built[..., 0] - 0.05 * streets) * (1 - water)
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.004, strength=1.0))
    save_clouds(out, *terran_clouds(g))
    write_pins(out / "pins.json", "Terran", PINS)
    print(f"done {time.time() - t0:.1f}s -> {out}, water {float((water > 0.5).mean()):.3f}")


def terran_clouds(g):
    """Sparse weather: scattered cloud, a couple of fronts, no great storms."""
    storms = [
        dict(lat=48, lon=-100, ax=16, ay=11, swirl=1.2, inflow=0.5, strength=0.7, face=0.6, front=(30, -125)),
        dict(lat=-44, lon=150, ax=14, ay=10, swirl=-1.1, inflow=0.5, strength=0.6, face=-0.5, front=(-28, 125)),
    ]
    return make_clouds(g, SEED, cover=0.18, storms=storms, veil=(0.0, 0.08), zoning=0.25)


def save_clouds(out: Path, clouds, thickness) -> None:
    out.mkdir(parents=True, exist_ok=True)
    save_gray(out / "clouds.webp", clouds)
    save_rgb(out / "clouds-normal.webp", normal_map(thickness * 0.006, strength=1.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/terran")
    ap.add_argument("--clouds-only", action="store_true", help="regenerate just the cloud layer")
    args = ap.parse_args()
    if args.clouds_only:
        save_clouds(args.out, *terran_clouds(make_grid(args.width)))
    else:
        generate(args.width, args.out)

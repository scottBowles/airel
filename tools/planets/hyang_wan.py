"""Hyang Wan (the rain-soaked water world): generate texture maps and pins from the spec below.

    python3 tools/planets/hyang_wan.py [--width 4096] [--out web/static/system/hyang-wan]

Lore (see .ideas/projects/solar-system-3d/bodies/hyang-wan.md and QUESTIONS.md):
- "Water planet. Technology. Constantly raining." Islands only (DM, Nov 2026): volcanic
  islands and archipelagos in open ocean, made by Gliton's eruptions in the creation story.
- On Mulgogi the rain has "blanched the landscape. Dull white … about the same shade of green.
  Everything is greyed out." So the land is a pale, washed grey-green with little contrast.
- Two rival weapons plants on opposite sides of the planet: Kamasu on Mulgogi, and JingLong
  on Hatatori Island "outside of a major city", the brightest lights on the planet.
- The squid migrate north each year through the East Isles to Thiton's Temple, an undersea
  cathedral on an open-ocean reef, now crumbled. The nearest land to it is "small,
  uninhabited islands" about five hours away; Mulgogi is 8–10 hours.
- High tech and "super luddite" side by side: some islands blaze at night, some stay dark.

Places use the brief's layout: Mulgogi at 24° W, the temple across the equator to its ENE,
Hatatori ~125° west of Kamasu. Longitude zero is arbitrary.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from clouds import make_clouds
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
    write_pins,
)

SEED = 404
LAND = 0.09  # share of the surface above water

# Named islands: (lat, lon, half-width lon°, half-height lat°, lift: how steeply they rise). Shores come from the noise.
ISLANDS = [
    dict(name="Mulgogi", lat=-7, lon=-24, ax=6.5, ay=4.5, lift=0.35),
    dict(name="Hatatori", lat=-5, lon=-155, ax=3, ay=2.4, lift=0.35),
]
# The East Isles: inhabited archipelago on the squid's road north.
EAST_ISLES = dict(lat=-8, lon=-6, ax=7, ay=5)
TEMPLE = (4, 15)
ISLETS = (12, 31)
# Sea floor around the temple stays deep: nothing but the islets within five hours, and no
# large island nearer than Mulgogi (8–10 hours).
CLEAR_RADIUS = 15
NO_BIG_LAND = 32

TOWNS = [  # (lat, lon, radius°, brightness)
    (-4.7, -154.8, 1.3, 1.3),  # Hatatori's major city
    (-5.2, -155.6, 0.35, 1.0),  # JingLong
    (-3.5, -29, 0.3, 1.2),  # Kamasu's dome
    (-5, -20, 0.6, 0.9),  # the port town where the Desconnegut landed
    (-9.5, -26, 0.4, 0.6),
    (-6, -22.5, 0.35, 0.5),
    (-10, -20.5, 0.3, 0.5),
]

PINS = [
    dict(name="Mulgogi", lat=-7, lon=-24, confidence="layout"),
    dict(name="Kamasu Complex", lat=-3.5, lon=-29, confidence="guess"),
    dict(name="Bagmulgwan", lat=-4.0, lon=-28.2, confidence="guess"),
    dict(name="Thiton's Temple", lat=TEMPLE[0], lon=TEMPLE[1], confidence="layout"),
    dict(name="Hatatori Island", lat=-5, lon=-155, confidence="layout"),
    dict(name="JingLong Facility", lat=-5.2, lon=-155.6, confidence="layout"),
]

LIGHT = np.array([1.0, 0.78, 0.52], np.float32)


def rank(x: np.ndarray) -> np.ndarray:
    u = np.empty(x.size, np.float32)
    u[np.argsort(x, axis=None)] = np.linspace(0, 1, x.size, dtype=np.float32)
    return u.reshape(x.shape)


def warped_ellipse(g, p, warp, noise, lat, lon, ax, ay):
    """Elliptical distance (1 at the edge) with its coordinates bent by noise: ragged shores."""
    wl = 1.4 * ay * fbm(noise, p * 4 + warp * 0.8 + 2.0, 6)
    wo = 1.4 * ax * fbm(noise, p * 4 + warp * 0.8 + 9.0, 6)
    dlat = (np.degrees(g.lat) + wl - lat) / ay
    dlon = ((np.degrees(g.lon) + wo - lon + 180) % 360 - 180) * np.cos(np.radians(lat)) / ax
    return np.sqrt(dlat**2 + dlon**2)


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n1, n2, n3, n4, n5, n6 = (Noise3(SEED * 10 + i) for i in range(6))
    p = g.xyz
    lat = np.degrees(g.lat)

    # One warped field: the sea floor, its rises, and the islands that break the surface.
    # Islands are a fine-grained field, gathered into archipelagos by a slower one, so no
    # land grows to continent size.
    warp = np.stack([fbm(n1, p * 1.8 + 11, 5), fbm(n2, p * 1.8 + 23, 5), fbm(n3, p * 1.8 + 37, 5)], -1)
    base = fbm(n4, p * 6.0 + warp * 1.4, octaves=8)
    ridges = ridged(n5, p * 8.0 + warp * 1.0, octaves=6)
    province = rank(fbm(n6, p * 2.4 + warp * 0.7, 5))
    h = rank(base + 0.3 * (ridges - 0.5)) + 0.3 * smoothstep(0.45, 0.95, province) - 0.5 * smoothstep(0.55, 0.1, province)
    print(f"field {time.time() - t0:.1f}s")

    # Hotspot chains: volcanoes in a line, young and tall at one end, worn down to shoals
    # at the other.
    cones = np.zeros_like(h)
    for _ in range(9):
        la, lo = float(rng.uniform(-55, 55)), float(rng.uniform(-180, 180))
        if angular_distance_pt(la, lo, *TEMPLE) < CLEAR_RADIUS + 8:
            continue
        ang = rng.uniform(0, 2 * np.pi)
        step = rng.uniform(1.6, 2.8)
        n = int(rng.integers(5, 10))
        for k in range(n):
            cla = la + k * step * np.sin(ang)
            clo = lo + k * step * np.cos(ang) / np.cos(np.radians(la))
            r = rng.uniform(0.5, 1.1) * (1 - 0.06 * k)
            tall = 0.9 * (1 - k / n) + 0.1
            t = angular_distance(g, cla, clo) / r
            near = t < 3
            cones[near] = np.maximum(cones[near], tall * np.exp(-(t[near] ** 2) * 1.2))
    h = h + cones * (0.7 + 0.5 * fbm(n2, p * 30, 3))

    # Open ocean around the temple, apart from the islets.
    islets = angular_distance(g, *ISLETS)
    temple_d = angular_distance(g, *TEMPLE)
    h = h - 0.6 * smoothstep(NO_BIG_LAND + 4, NO_BIG_LAND - 4, temple_d) * smoothstep(1.6, 3.0, islets)
    sea_level = np.quantile(h, 1 - LAND)

    # Named islands lift the noise field itself, so their shores, bays and points are as
    # natural as any other island's; a moat of open water keeps each one distinct.
    for isl in ISLANDS:
        d = warped_ellipse(g, p, warp, n3, isl["lat"], isl["lon"], isl["ax"], isl["ay"])
        h = h - 0.6 * smoothstep(0.9, 1.4, d) * smoothstep(2.6, 1.8, d)
        # Shore near d = 0.85, pushed in and out by the same noise as the rest.
        own = sea_level + isl["lift"] * (0.85 - d) + 0.4 * (rank(base) - 0.5) + 0.2 * (ridges - 0.5) + 0.5 * fbm(n5, p * 25 + warp, 4)
        h = np.where(d < 1.6, np.maximum(h, own), h)
    d = warped_ellipse(g, p, warp, n4, EAST_ISLES["lat"], EAST_ISLES["lon"], EAST_ISLES["ax"], EAST_ISLES["ay"])
    # Many small islands: the high-frequency peaks only.
    bumps = rank(fbm(n1, p * 40 + warp * 2, 4))
    h = np.maximum(h, sea_level - 0.1 + 0.2 * smoothstep(1.3, 0.4, d) * smoothstep(0.6, 0.92, bumps))
    h = np.maximum(h, sea_level - 0.1 + 0.16 * smoothstep(2.2, 0.6, islets) * smoothstep(0.75, 0.95, bumps))
    print(f"islands {time.time() - t0:.1f}s")

    u = h
    water = smoothstep(sea_level + 0.003, sea_level - 0.003, u)
    below = np.clip(sea_level - u, 0, None)

    # Ocean: deep slate-teal, a little warmer and lighter toward the equator; turquoise
    # only on the shelves around islands and over shoals.
    warm = smoothstep(55, 0, np.abs(lat))[..., None]
    deep = np.array([0.03, 0.09, 0.13], np.float32) * (1 - warm) + np.array([0.035, 0.12, 0.16], np.float32) * warm
    mid = np.array([0.05, 0.17, 0.21], np.float32)
    shelf = np.array([0.15, 0.36, 0.37], np.float32)
    s1 = smoothstep(0.06, 0.0, below)[..., None]
    s2 = smoothstep(0.02, 0.0, below)[..., None]
    swell = fbm(n5, p * 8 + warp * 1.5, 5)[..., None]
    water_rgb = deep * (0.9 + 0.25 * swell)
    water_rgb = water_rgb * (1 - s1) + mid * s1
    water_rgb = water_rgb * (1 - 0.8 * s2) + shelf * 0.8 * s2
    # Thiton's reef: a faint pale shoal, the ruin under it.
    reef = smoothstep(1.6, 0.3, temple_d + 2.5 * fbm(n2, p * 40 + warp, 4)) * 0.8
    water_rgb = water_rgb * (1 - 0.35 * reef[..., None]) + shelf * 0.35 * reef[..., None]

    # Land: rain-blanched grey-green, low contrast; bare dark rock on the young volcanoes.
    e = np.clip((u - sea_level) / (u.max() - sea_level), 0, 1)
    e = np.sqrt(e)
    land = ramp(
        e,
        [
            (0, (0.36, 0.41, 0.35)),
            (0.25, (0.40, 0.46, 0.38)),
            (0.6, (0.46, 0.50, 0.44)),
            (0.85, (0.52, 0.54, 0.50)),
            (1, (0.42, 0.42, 0.41)),
        ],
    )
    grain = fbm(n2, p * 90 + warp * 3, 4)
    land = land * (0.92 + 0.14 * grain[..., None]) * (0.88 + 0.24 * ridges[..., None])
    rock = smoothstep(0.35, 0.7, cones)[..., None]
    land = land * (1 - 0.5 * rock) + np.array([0.30, 0.30, 0.30], np.float32) * 0.5 * rock
    rgb = land * (1 - water[..., None]) + water_rgb * water[..., None]
    print(f"colour {time.time() - t0:.1f}s")

    # Lights: towns on inhabited islands, Hatatori's city brightest; some islands dark.
    lights = np.zeros_like(u)
    sprawl = fbm(n3, p * 300, 3)
    for la, lo, r, b in TOWNS:
        t = angular_distance(g, la, lo) / r
        near = t < 1.6
        core = smoothstep(1.6, 0.0, t[near])
        lights[near] += b * core * smoothstep(0.05 - 0.3 * core, 0.35, sprawl[near])
    # Settled islands, and luddite ones left dark.
    settled = smoothstep(0.45, 0.75, rank(fbm(n6, p * 6 + warp + 3.3, 4)))
    settled = np.maximum(settled, smoothstep(1.4, 0.6, warped_ellipse(g, p, warp, n3, -7, -24, 6.5, 4.5)) * 0.8)
    settled = np.maximum(settled, smoothstep(1.3, 0.5, d))
    settled = settled * smoothstep(1.6, 2.4, islets)
    coast = smoothstep(0.3, 0.0, e)
    speck = smoothstep(0.78, 0.92, rank(fbm(n2, p * 380 + 1.7, 2))) * (0.4 + 0.6 * smoothstep(0.4, 0.8, rank(fbm(n4, p * 70, 3))))
    lights += 0.8 * settled * (0.4 + 0.6 * coast) * speck
    lights = np.clip(lights, 0, 1.5) * (1 - water)
    # Ocean platforms (Kaminoan-style stilt cities): a sparse scatter of lone lights.
    plat_la = np.degrees(np.arcsin(rng.uniform(-0.8, 0.8, 70)))
    plat_lo = rng.uniform(-180, 180, 70)
    for la, lo in zip(plat_la, plat_lo):
        if angular_distance_pt(la, lo, *TEMPLE) < CLEAR_RADIUS:
            continue
        t = angular_distance(g, la, lo) / 0.12
        near = t < 1.5
        lights[near] += 0.6 * smoothstep(1.5, 0.0, t[near])
    emissive = LIGHT * np.clip(lights, 0, 1.5)[..., None] * 0.8
    rgb = rgb * (1 - 0.25 * np.clip(lights, 0, 1)[..., None]) + 0.12 * np.clip(lights, 0, 1)[..., None]
    print(f"lights {time.time() - t0:.1f}s")

    clouds, cloud_thick = hyang_clouds(g)
    print(f"clouds {time.time() - t0:.1f}s")
    cw = np.stack([fbm(n5, p * 2.5 + 3, 4), fbm(n6, p * 2.5 + 9, 4), fbm(n4, p * 2.5 + 17, 4)], -1)

    # Water roughness: wind-varied, so the glint is broken; rain-pocked seas are rough.
    pw = p * np.array([1.0, 1.0, 2.5], np.float32)
    wind = rank(fbm(n5, pw * 4 + cw * 1.2 + 4.2, 5) + 0.4 * fbm(n6, pw * 22 + 8.1, 3))
    rough = np.where(water > 0.5, 0.5 + 0.3 * wind, 0.9)
    height = np.clip(e, 0, 1) * (1 - water)

    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.03, strength=1.0))
    save_clouds(out, clouds, cloud_thick)
    write_pins(out / "pins.json", "Hyang Wan", PINS)
    print(f"done {time.time() - t0:.1f}s -> {out}, land {float((water < 0.5).mean()):.3f}")


def hyang_clouds(g):
    """Rain bands wound into a few cyclones, over a thin grey overcast ("everything is greyed
    out") that dulls the islands without hiding them."""
    # Storms at different stages along the mid-latitude storm tracks: mature commas trailing
    # cold fronts, young waves just kinking a front, an old one unwinding. A mature one sits
    # north-west of Mulgogi, in view. Positive swirl turns anticlockwise (the north's cyclones).
    storms = [
        dict(lat=40, lon=-38, ax=24, ay=17, swirl=2.0, face=0.8, front=(16, -64)),
        dict(lat=46, lon=70, ax=14, ay=10, swirl=1.0, inflow=0.5, strength=0.7, eye=0, face=0.5, front=(30, 44)),
        dict(lat=-44, lon=-125, ax=22, ay=16, swirl=-1.9, face=-0.8, front=(-20, -150)),
        dict(lat=58, lon=165, ax=18, ay=14, swirl=1.3, inflow=0.4, strength=0.6, eye=0.3),
        dict(lat=-50, lon=25, ax=13, ay=10, swirl=-1.0, inflow=0.5, strength=0.7, eye=0, front=(-34, 2)),
    ]
    return make_clouds(g, SEED, cover=0.38, storms=storms, veil=(0.25, 0.42), zoning=0.3)


def save_clouds(out: Path, clouds, thickness) -> None:
    out.mkdir(parents=True, exist_ok=True)
    save_gray(out / "clouds.webp", clouds)
    save_rgb(out / "clouds-normal.webp", normal_map(thickness * 0.006, strength=1.0))


def angular_distance_pt(la1, lo1, la2, lo2) -> float:
    a1, b1, a2, b2 = map(np.radians, (la1, lo1, la2, lo2))
    c = np.sin(a1) * np.sin(a2) + np.cos(a1) * np.cos(a2) * np.cos(b1 - b2)
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/hyang-wan")
    ap.add_argument("--clouds-only", action="store_true", help="regenerate just the cloud layer")
    args = ap.parse_args()
    if args.clouds_only:
        save_clouds(args.out, *hyang_clouds(make_grid(args.width)))
    else:
        generate(args.width, args.out)

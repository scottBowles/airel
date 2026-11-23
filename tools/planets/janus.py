"""Janus (half light, half dark): generate texture maps and pins from the spec below.

    python3 tools/planets/janus.py [--width 4096] [--out web/static/system/janus]

Lore (see .ideas/projects/solar-system-3d/bodies/janus.md and QUESTIONS.md):
- Tidally locked to the Red Sun; that alone makes the dark side (DM, Nov 2026). The sub-solar
  point is at (0, 0): the light side is lon -90..90, the dark side faces away, and the
  Mezzolux is the ring at lon ±90.
- The light side is an unbearably hot desert with very little life (DM). Nobody in the logs
  goes there. Here: rust and ochre desert, dune lines radiating from the sub-solar point (the
  surface winds of a locked world all run toward it), pale dry lakebeds, and a scorched,
  darkened plain right under the sun.
- The Mezzolux: "desolate, desert-like … ashy grey cacti … rock land", buttes and spires,
  flash-flood channels. About 40 miles across in the logs; drawn ~6° wide so it reads from
  orbit. Its people (shepherds, Visparo) make it the habitable band, lit by a string of towns.
- The dark side: temperate, kept from freezing by geysers whose steam makes its clouds. Dark
  rock, pale mineral crust around the geyser fields, no ice. A few surface settlements (the
  House of Knowledge); most cities are the Princes', floating above it, drawn as cool lights.
- The visited sites are on the lon -90 arc: west of the butte is dark (DM).
- Places in the Mezzolux cluster are spread about 10× from their true distances so the pins
  can be told apart (see the brief).
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
    ridged,
    save_gray,
    save_rgb,
    smoothstep,
    veins,
    write_pins,
)

SEED = 404
BAND = 3.0  # half-width of the Mezzolux as drawn, degrees of solar elevation

BUTTE = (8, -90.0)
HUT = (12, -90.4)
HOUSE = (12, -96)
CASTLE = (30, -125)  # House Roderick's floating castle, over a large mountain
BUTTE_COUNTRY = dict(lat=5, lon=-90, ax=2.5, ay=11)
WASTELANDS = dict(lat=-11, lon=-90, ax=3.5, ay=19)

# The Princes' floating cities: (lat, lon, size).
FLOATING = [(30, -125, 0.7), (-18, -132, 1.0), (42, -160, 0.8), (8, 150, 1.0), (-38, 118, 0.7), (22, 112, 0.6), (-52, -172, 0.5)]
# Dark-side surface settlements besides the House of Knowledge.
DARK_TOWNS = [(25, -104, 0.5), (-6, -110, 0.4), (40, 104, 0.4), (-28, 100, 0.45), (55, -115, 0.3)]

PINS = [
    dict(name="Mezzolux", lat=0, lon=-90, confidence="lore"),
    dict(name="The Penumbra", lat=14, lon=-90, confidence="layout"),
    dict(name="The House of Knowledge", lat=HOUSE[0], lon=HOUSE[1], confidence="layout"),
    dict(name="Visparo's Hut", lat=HUT[0], lon=HUT[1], confidence="layout"),
    dict(name="Janus Underground", lat=11.5, lon=-90.9, confidence="layout"),
    dict(name="Black Lake", lat=11.5, lon=-93, confidence="layout"),
    dict(name="The Wastelands", lat=WASTELANDS["lat"], lon=WASTELANDS["lon"], confidence="layout"),
    dict(name="Butte on Janus", lat=BUTTE[0], lon=BUTTE[1], confidence="layout"),
    dict(name="Sarcophagus of Gliten", lat=BUTTE[0] - 0.6, lon=BUTTE[1] + 0.3, confidence="lore"),
    dict(name="House Roderick's castle", lat=CASTLE[0], lon=CASTLE[1], confidence="guess"),
]

WARM = np.array([1.0, 0.72, 0.42], np.float32)
PRINCES = np.array([0.72, 0.6, 1.0], np.float32)


def ellipse(g, lat, lon, ax, ay):
    dlat = (np.degrees(g.lat) - lat) / ay
    dlon = ((np.degrees(g.lon) - lon + 180) % 360 - 180) * np.cos(np.radians(lat)) / ax
    return np.sqrt(dlat**2 + dlon**2)


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n = [Noise3(SEED * 10 + i) for i in range(8)]
    p = g.xyz
    # Solar elevation: 90 under the sun, 0 on the terminator, -90 at the far point.
    sun = np.degrees(np.arcsin(np.clip(p[..., 0], -1, 1)))
    # Wobble the terminator's ground a little so the band isn't ruled straight.
    sun_w = sun + 1.2 * fbm(n[0], p * 7, 4)

    warp = np.stack([fbm(n[0], p * 1.6 + 11, 5), fbm(n[1], p * 1.6 + 23, 5), fbm(n[2], p * 1.6 + 37, 5)], -1)
    base = rank(fbm(n[3], p * 2.6 + warp * 1.3, 8))
    ridges = ridged(n[4], p * 4.5 + warp, 6)
    h = 0.7 * base + 0.3 * ridges * smoothstep(0.35, 0.75, base)
    # The mountain under the floating castle.
    h = h + 0.5 * np.exp(-((angular_distance(g, *CASTLE) / 3.0) ** 2)) * (0.7 + 0.5 * ridges)
    e = rank(h)
    print(f"relief {time.time() - t0:.1f}s")

    day = smoothstep(-BAND, BAND, sun_w)  # 1 on the light side
    band = smoothstep(BAND + 1.5, BAND - 1.0, np.abs(sun_w))  # 1 in the Mezzolux
    grain = fbm(n[5], p * 260, 3)
    fine = fbm(n[6], p * 60 + warp, 4)

    # --- The light side: an unbearably hot desert. ------------------------------------------
    desert = ramp(
        rank(fbm(n[6], p * 4 + warp * 1.4, 6)) * 0.6 + 0.4 * e,
        [
            (0.0, (0.7, 0.6, 0.47)),  # dry lakebeds in the lows
            (0.18, (0.66, 0.46, 0.28)),
            (0.45, (0.58, 0.34, 0.19)),  # rust hamada
            (0.7, (0.46, 0.27, 0.16)),
            (1.0, (0.28, 0.19, 0.15)),  # dark highland rock
        ],
    )
    # Playas: flat pale pans in the lowest ground, crusted with salt.
    playa = smoothstep(0.07, 0.02, e + 0.05 * fine)
    desert = desert * (1 - playa[..., None]) + np.array([0.8, 0.74, 0.63], np.float32) * playa[..., None]
    # Dune seas: lines radiating from the sub-solar point, where every surface wind on a locked
    # world converges. They fade out near the point itself and in the uplands.
    ang = np.arctan2(p[..., 2], p[..., 1])
    ang_w = ang + 0.05 * fbm(n[7], p * 9 + warp, 4)
    dunes = 0.5 + 0.5 * np.sin(ang_w * 520 + 2.0 * fbm(n[2], p * 30, 3))
    erg = smoothstep(0.45, 0.7, rank(fbm(n[1], p * 3 + warp * 1.2 + 5, 5))) * smoothstep(0.6, 0.35, e)
    erg = erg * smoothstep(80, 60, sun) * smoothstep(5, 15, sun)
    sand = np.array([0.76, 0.52, 0.3], np.float32)
    desert = desert * (1 - 0.8 * erg[..., None]) + sand * (0.82 + 0.25 * dunes[..., None]) * 0.8 * erg[..., None]
    # Right under the sun: a scorched plain, darkened and glazed.
    scorch = smoothstep(68, 84, sun + 4 * fbm(n[3], p * 8, 4))
    desert = desert * (1 - 0.6 * scorch[..., None]) + np.array([0.22, 0.14, 0.11], np.float32) * 0.6 * scorch[..., None]
    # Dry riverbeds cut long ago, faint.
    wadis = veins(n[4], p * 10 + warp * 2, 0.05) * smoothstep(0.55, 0.75, rank(fbm(n[5], p * 3 + 2.2, 4)))
    desert = desert * (1 - 0.15 * wadis[..., None])

    # --- The dark side: dark rock, pale crust around the geyser fields, no ice. --------------
    rock = ramp(e, [(0.0, (0.2, 0.19, 0.18)), (0.5, (0.15, 0.14, 0.14)), (1.0, (0.11, 0.1, 0.11))])
    fields = smoothstep(0.82, 0.93, rank(fbm(n[2], p * 6 + warp * 1.5 + 9, 5)))
    vents = smoothstep(0.75, 0.95, rank(fbm(n[7], p * 140, 2))) * fields
    sinter = np.clip(0.55 * fields * (0.4 + 0.6 * smoothstep(-0.1, 0.3, fine)) + 0.6 * vents, 0, 1)
    rock = rock * (1 - sinter[..., None]) + np.array([0.62, 0.6, 0.56], np.float32) * sinter[..., None]

    # --- The Mezzolux: ashy grey rock land, buttes, flash-flood channels. --------------------
    ash = ramp(e, [(0.0, (0.5, 0.47, 0.43)), (0.6, (0.41, 0.39, 0.37)), (1.0, (0.3, 0.29, 0.28))])
    # Butte country: mesas (terraced lumps of the relief) along the visited arc.
    bc = smoothstep(1.3, 0.7, ellipse(g, BUTTE_COUNTRY["lat"], BUTTE_COUNTRY["lon"], BUTTE_COUNTRY["ax"], BUTTE_COUNTRY["ay"]) + 0.25 * fine)
    mesa_field = rank(fbm(n[1], p * 70 + warp * 2, 4))
    mesas = smoothstep(0.66, 0.7, mesa_field) * bc
    ash = ash * (1 - 0.35 * mesas[..., None]) + np.array([0.34, 0.27, 0.22], np.float32) * 0.35 * mesas[..., None]
    channels = np.maximum(veins(n[3], p * 40 + warp * 3, 0.06), 0.7 * veins(n[6], p * 90 + warp * 4, 0.08))
    ash = ash * (1 - 0.25 * channels[..., None])
    # The Wastelands: bleached and bare, south along the band.
    waste = smoothstep(1.2, 0.7, ellipse(g, WASTELANDS["lat"], WASTELANDS["lon"], WASTELANDS["ax"], WASTELANDS["ay"]) + 0.3 * fine)
    ash = ash * (1 - 0.6 * waste[..., None]) + np.array([0.66, 0.63, 0.57], np.float32) * 0.6 * waste[..., None]

    rgb = rock * (1 - day[..., None]) + desert * day[..., None]
    rgb = rgb * (1 - band[..., None]) + ash * band[..., None]
    rgb = rgb * (0.92 + 0.12 * grain[..., None])
    print(f"colour {time.time() - t0:.1f}s")

    # --- Lights: towns along the Mezzolux, a few dark-side settlements, the floating cities. --
    lights = np.zeros(g.lat.shape, np.float32)
    cool = np.zeros(g.lat.shape, np.float32)
    speck = fbm(n[4], p * 320, 3)
    # The habitable band: small towns strung along it, thickest near the visited arc.
    towns = smoothstep(0.86, 0.95, rank(fbm(n[5], p * 45 + 3.3, 3)))
    near_arc = 0.5 + 0.5 * smoothstep(60, 10, angular_distance(g, 0, -90))
    towns = smoothstep(0.7, 0.9, rank(fbm(n[5], p * 45 + 3.3, 3)))
    # Settled ground runs a little way into the dark (the House of Knowledge is a drive from the
    # band), thinning out away from the terminator.
    settled = smoothstep(-12, -1.5, sun_w + 3 * fine) * smoothstep(3, 0, sun_w)
    lights += 1.0 * settled * towns * near_arc * smoothstep(0.0, 0.3, speck + 0.2)
    lights += 0.35 * settled * smoothstep(0.8, 0.95, rank(fbm(n[6], p * 400 + 7.7, 2)))  # homesteads
    for la, lo, s in [(HOUSE[0], HOUSE[1], 0.8), *DARK_TOWNS]:
        t = angular_distance(g, la, lo) / (3.0 * s)
        near = t < 1.5
        lights[near] += (0.5 + 0.6 * s) * smoothstep(1.5, 0.0, t[near]) * smoothstep(-0.1, 0.25, speck[near])
    # The Princes' cities: a bright core and a scatter of lit districts around it.
    dots = smoothstep(0.55, 0.85, rank(fbm(n[3], p * 220 + 4.4, 2)))
    for la, lo, s in FLOATING:
        t = angular_distance(g, la, lo) / (2.2 * s)
        near = t < 1.3
        cool[near] += s * (1.1 * smoothstep(0.3, 0.0, t[near]) + 0.9 * smoothstep(1.3, 0.2, t[near]) * dots[near])
    lights *= 1 - day
    emissive = WARM * np.clip(lights, 0, 1.2)[..., None] + PRINCES * np.clip(cool, 0, 1.3)[..., None]
    print(f"lights {time.time() - t0:.1f}s")

    rough = 0.9 - 0.2 * playa * day - 0.15 * scorch
    height = np.clip(e + 0.08 * mesas - 0.04 * channels * band - 0.03 * wadis * day, 0, 1)
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.02, strength=1.0))
    save_clouds(out, *janus_clouds(g))
    write_pins(out / "pins.json", "Janus", PINS)
    print(f"done {time.time() - t0:.1f}s -> {out}")


def janus_clouds(g):
    """Steam from the geysers over the dark side, thickest a little way past the terminator where
    warm air meets the cold; storms along the Mezzolux (flash floods, lightning); the light side
    almost clear."""
    storms = [
        dict(lat=20, lon=-100, ax=8, ay=6, swirl=1.2, inflow=0.6, strength=0.8),
        dict(lat=-25, lon=97, ax=7, ay=5, swirl=-1.1, inflow=0.6, strength=0.8),
    ]
    clouds, thick = make_clouds(g, SEED, cover=0.35, storms=storms, veil=(0.0, 0.08), zoning=0.0)
    sun = np.degrees(np.arcsin(np.clip(g.xyz[..., 0], -1, 1)))
    where = 0.08 + 0.92 * smoothstep(4, -10, sun) * (0.55 + 0.45 * smoothstep(-70, -15, sun))
    return clouds * where, thick * where


def save_clouds(out: Path, clouds, thickness) -> None:
    out.mkdir(parents=True, exist_ok=True)
    save_gray(out / "clouds.webp", clouds)
    save_rgb(out / "clouds-normal.webp", normal_map(thickness * 0.006, strength=1.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/janus")
    ap.add_argument("--clouds-only", action="store_true", help="regenerate just the cloud layer")
    args = ap.parse_args()
    if args.clouds_only:
        save_clouds(args.out, *janus_clouds(make_grid(args.width)))
    else:
        generate(args.width, args.out)

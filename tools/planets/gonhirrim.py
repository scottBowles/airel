"""Gonhirrim (the gas giant): generate texture maps from the feature spec below.

    python3 tools/planets/gonhirrim.py [--width 4096] [--out web/static/system/gonhirrim]

Lore (DB notes, "On the Planets", session logs; see .ideas/projects/solar-system-3d/bodies/gonhirrim.md):
- A gas giant with seven inhabited moons; nobody lives on the planet itself.
- "Too much of a storm all the time. Cloud." Attempts to delve into it haven't got far.
- "The eighth moon" is what the dwarves call its centre: where their crafter god lived or
  lives, and where their fallen go to rest. Nobody has got there and returned.
- A strong magnetic field (it blocks comms from orbit).

The text gives no colours; the DM asked for something Jupiter-like that looks good. Turbulent
zonal bands in creams, ochres, rust and salmon, a dusky blue-grey nod to "the blue seal of
Gonhirrim" at the poles, one great storm, and a dozen small ovals. The core is only hinted
at: the great storm's eye holds a faint ember glow that shows on the night side.
"""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import numpy as np

from planetgen import Noise3, fbm, make_grid, normal_map, ramp, save_gray, save_rgb, smoothstep, unit

SEED = 808

# The great storm: the vortex the core hides under. (lat, lon, half-width lon°, half-height lat°)
GREAT_STORM = dict(lat=-22, lon=40, ax=14, ay=8, swirl=2.6)
SMALL_STORMS = 14


def tangent_basis(lat: float, lon: float):
    c = unit(lat, lon)
    east = np.array([-math.sin(math.radians(lon)), math.cos(math.radians(lon)), 0], np.float32)
    north = np.cross(c, east)
    return c, east, north


def storm_coords(p: np.ndarray, s: dict):
    """Elliptical distance (1 at the storm's edge) and the local frame of a storm."""
    c, e, n = tangent_basis(s["lat"], s["lon"])
    pe, pn, pc = p @ e, p @ n, p @ c
    de = np.degrees(np.arctan2(pe, pc)) / s["ax"]
    dn = np.degrees(np.arctan2(pn, pc)) / s["ay"]
    return np.sqrt(de * de + dn * dn) + (pc < 0) * 10.0, c


def swirl(p: np.ndarray, s: dict) -> np.ndarray:
    """Rotate points about the storm's centre by an angle that fades with distance."""
    d, c = storm_coords(p, s)
    ang = s["swirl"] * np.exp(-(d**2) * 1.6)
    cos, sin = np.cos(ang)[..., None], np.sin(ang)[..., None]
    k = c[None, None, :]
    return p * cos + np.cross(k, p) * sin + k * (p @ c)[..., None] * (1 - cos)


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n1, n2, n3, n4 = (Noise3(SEED + i) for i in range(4))

    # Small storms sit near band edges at mid latitudes, alternating hemispheres.
    smalls = []
    for i in range(SMALL_STORMS):
        lat = float(rng.uniform(12, 52) * (1 if i % 2 else -1))
        size = float(rng.uniform(1.6, 3.6))
        smalls.append(dict(lat=lat, lon=float(rng.uniform(-180, 180)), ax=size * 1.5, ay=size, swirl=float(rng.uniform(1.6, 2.6)) * rng.choice([-1, 1])))

    q = g.xyz
    q = swirl(q, GREAT_STORM)
    for s in smalls:
        q = swirl(q, s)
    print(f"swirls {time.time() - t0:.1f}s")

    # Zonal flow: noise stretched along longitude, so features streak east-west.
    a = np.stack([q[..., 0] * 1.6, q[..., 1] * 1.6, q[..., 2] * 11.0], -1)
    w1 = fbm(n1, a + 3.1, octaves=6)
    w2 = fbm(n2, a * 2.2 + w1[..., None] * 1.4 + 7.7, octaves=6)
    w3 = fbm(n3, a * 6.0 + w2[..., None] * 2.0 + 1.3, octaves=4)
    print(f"flow {time.time() - t0:.1f}s")

    # Bands: a random light/dark and hue value every few degrees of latitude.
    lat_q = np.degrees(np.arcsin(np.clip(q[..., 2], -1, 1)))
    edges = np.cumsum(rng.uniform(4.5, 11.0, size=40))
    edges = edges - edges[len(edges) // 2] + rng.uniform(-3, 3)
    tone = rng.uniform(0, 1, size=len(edges))
    tone[::2] = 0.55 + 0.45 * tone[::2]  # alternate pale zones and dark belts
    tone[1::2] = 0.45 * tone[1::2]
    hue = rng.uniform(0, 1, size=len(edges))
    # Turbulence is strongest where bands meet; polar regions lose their bands.
    y = lat_q + 4.5 * w1 + 2.6 * w2 + 1.1 * w3
    # Extra churn where neighbouring bands differ most: festoons and eddies along the edges.
    edge = np.abs(np.interp(y + 0.8, edges, tone) - np.interp(y - 0.8, edges, tone))
    w4 = fbm(n4, a * 3.3 + w2[..., None] * 2.5 + 4.4, octaves=5)
    y = y + 6.0 * smoothstep(0.05, 0.4, edge) * w4
    band_tone = np.interp(y, edges, tone)
    band_hue = np.interp(y + 3.0 * w2, edges, hue)
    polar = smoothstep(58, 84, np.abs(lat_q) + 8 * w1)
    band_tone = band_tone * (1 - polar) + (0.45 + 0.35 * w2 + 0.3 * w3) * polar
    band_tone = np.clip(band_tone + 0.18 * w3, 0, 1)

    light = ramp(band_tone, [(0, (0.30, 0.17, 0.11)), (0.25, (0.52, 0.30, 0.19)), (0.5, (0.74, 0.52, 0.34)), (0.75, (0.88, 0.74, 0.55)), (1, (0.95, 0.90, 0.80))])
    salmon = ramp(band_tone, [(0, (0.34, 0.14, 0.12)), (0.3, (0.62, 0.30, 0.24)), (0.6, (0.84, 0.55, 0.45)), (1, (0.95, 0.84, 0.76))])
    rgb = light * (1 - band_hue[..., None] * 0.55) + salmon * band_hue[..., None] * 0.55
    dusk = ramp(band_tone, [(0, (0.24, 0.21, 0.24)), (0.5, (0.46, 0.44, 0.48)), (1, (0.74, 0.70, 0.68))])
    rgb = rgb * (1 - polar[..., None] * 0.6) + dusk * polar[..., None] * 0.6

    # The great storm: a brick-red oval with a pale collar and a spiral inside.
    d, _ = storm_coords(g.xyz, GREAT_STORM)
    spiral = fbm(n4, q * 9.0 + 5.0, octaves=5)
    inner = smoothstep(1.0, 0.75, d + 0.08 * spiral)
    collar = smoothstep(1.35, 1.05, d) * (1 - inner)
    storm_rgb = ramp(np.clip(0.5 + 0.9 * spiral + 0.35 * d, 0, 1), [(0, (0.45, 0.13, 0.08)), (0.5, (0.70, 0.30, 0.18)), (1, (0.90, 0.60, 0.42))])
    rgb = rgb * (1 - inner[..., None]) + storm_rgb * inner[..., None]
    rgb = rgb * (1 - collar[..., None] * 0.5) + np.array([0.95, 0.88, 0.76], np.float32) * collar[..., None] * 0.5

    # Small storms: mostly pale ovals, some dark brown, blended into the flow they turn.
    for i, s in enumerate(smalls):
        ds, _ = storm_coords(g.xyz, s)
        m = smoothstep(1.05, 0.35, ds + 0.35 * w3 + 0.2 * w2) * 0.6
        col = np.array([0.95, 0.91, 0.84] if i % 3 else [0.36, 0.20, 0.14], np.float32)
        rgb = rgb * (1 - m[..., None]) + col * m[..., None]

    # The eighth moon, hinted: a faint ember deep in the great storm's eye.
    eye = np.exp(-((d / 0.16) ** 2)) * (0.7 + 0.3 * spiral)
    emissive = np.array([1.0, 0.55, 0.18], np.float32) * (eye * 0.55)[..., None]
    rgb = rgb * (1 - eye[..., None] * 0.35) + np.array([0.55, 0.22, 0.10], np.float32) * eye[..., None] * 0.35

    # Gentle relief so the terminator shows cloud texture; the rest is matte.
    height = 0.5 + 0.25 * band_tone + 0.15 * w3
    print(f"colour {time.time() - t0:.1f}s")

    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", np.full(height.shape, 0.92, np.float32))
    save_rgb(out / "normal.webp", normal_map(height * 0.004, strength=1.0))
    (out / "pins.json").write_text('{"body": "Gonhirrim", "pins": []}\n')
    print(f"done {time.time() - t0:.1f}s -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/gonhirrim")
    args = ap.parse_args()
    generate(args.width, args.out)

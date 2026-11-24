"""Hielo ("the ice rock"): generate texture maps from the spec below.

    python3 tools/planets/hielo.py [--width 4096] [--out web/static/system/hielo]

Lore (see .ideas/projects/solar-system-3d/bodies/hielo.md, assets.md, QUESTIONS.md):
- "Not a planet… In the asteroid belt, rather than orbiting a sun. Frozen, largely
  uninhabitable." "The Pluto of this world. It is an oversized asteroid." The belt's largest body.
- Ice caves (Whidmore's energy canisters; the Roper's cave), Hammer and Kiln mixing Hiobium, a
  science station where scientists died, Bode Augur's self-exile. "Some natural creatures, but
  no people": only outposts, so a handful of faint lights.
- The user's take on the old model (assets.md): grey-white, cratered; keep it, maybe more craters.
- No places in the DB besides Hielo itself, so no pins.

Real analogue, and how it's translated:
- Pluto (New Horizons): a bright, smooth, uncratered nitrogen-ice plain (Sputnik Planitia) whose
  surface is broken into gentle convection cells; old, heavily cratered uplands around it; dark
  equatorial regions; grey-blue methane-frosted uplands; a blue haze (set in the app). Pluto's dark
  terrain is red-brown tholin; here it's kept a muted grey-brown, as the user pictured a grey-white
  body and broad strong colour reads as damage.
- Charon and Ariel: long chasms and graben in fractured ice. Here the ice-cave country is a field
  of such chasms, drawn as relief (the normal map), with fresher bluish ice in the floors, not as
  dark lines.
- Callisto and Ganymede: bright-rayed fresh craters on dark ice; a few here.

Interpretations (all guesses, from the brief): the plain at (10, 175); dark rough land around
(-20, -120); the chasm field at (16, -38); the Hiobium works (5, 10), the science station
(-10, 60) and Bode's camp (50, -90) as faint points of light; soft polar frost.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from clouds import rank
from moons import crater, random_points
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
    worley,
    write_pins,
)

SEED = 1616
PLAIN = (10, 175, 30)
PLAIN2 = (-6, 157, 20)  # a second, offset lobe: the plain is heart-like, not a disc  # centre and radius°: the bright smooth ice plain
DARK = (-15, -120, 48)  # the dark rough land
CHASMS = (16, -38, 12)  # the ice-cave country
CRATERS = 1200
RAYED = 6
LIGHTS = [
    (5, 10, 0.4, 0.9),  # Hammer and Kiln's Hiobium works
    (-10, 60, 0.25, 0.6),  # the science station
    (50, -90, 0.12, 0.45),  # Bode Augur's camp
    (16.5, -36.5, 0.15, 0.45),  # Whidmore's canisters in the ice caves
]
LAMP = np.array([1.0, 0.85, 0.65], np.float32)


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n = [Noise3(SEED * 10 + i) for i in range(12)]
    p = g.xyz
    lat = np.degrees(g.lat)

    warp = np.stack([fbm(n[0], p * 1.8 + 11, 5), fbm(n[1], p * 1.8 + 23, 5), fbm(n[2], p * 1.8 + 37, 5)], -1)
    base = fbm(n[3], p * 2.4 + warp, 6)
    ridges = ridged(n[4], p * 5 + warp * 1.2, 6)
    detail = fbm(n[5], p * 24 + warp * 2, 4)

    # The plain: a lobed basin, edged by noise so its shore wanders.
    pd = np.minimum(angular_distance(g, PLAIN[0], PLAIN[1]) / PLAIN[2], angular_distance(g, PLAIN2[0], PLAIN2[1]) / PLAIN2[2])
    pd = pd + 0.6 * fbm(n[6], p * 3 + warp, 4) + 0.1 * fbm(n[7], p * 14, 3)
    plain = smoothstep(1.0, 0.8, pd)
    # A margin where the plain's ice laps over the old land: paler, smoothed, partly buried.
    margin = smoothstep(1.35, 1.0, pd) * (1 - plain)
    # Dark land with a crisp, lobed edge (Pluto's dark regions end sharply), ragged by detail.
    dd = angular_distance(g, DARK[0], DARK[1]) / DARK[2] + 0.45 * fbm(n[7], p * 2.5 + warp, 5) + 0.12 * fbm(n[8], p * 12 + warp, 4)
    dark = smoothstep(1.0, 0.85, dd) * (0.75 + 0.25 * smoothstep(0.85, 0.4, dd))
    dark = dark * (1 - plain)
    print(f"field {time.time() - t0:.1f}s")

    # Craters everywhere but the plain (young ice, resurfaced). Power-law sizes.
    crat = np.zeros(g.lat.shape, np.float32)
    ejecta = np.zeros(g.lat.shape, np.float32)
    lats, lons = random_points(rng, CRATERS, (-88, 88))
    radii = 0.25 + 9.0 * rng.uniform(0, 1, CRATERS) ** 4
    for la, lo, r in zip(lats, lons, radii):
        rows = np.where(np.abs(lat[:, 0] - la) < 3 * r + 0.5)[0]
        sub = (slice(rows[0], rows[-1] + 1), slice(None))
        t = angular_distance(g, la, lo)[sub] / r
        near = t < 3
        crat[sub][near] += crater(t[near]) * (0.09 + 0.016 * r)
        ejecta[sub][near] += np.exp(-((t[near] - 1.5) ** 2) / 0.4) * 0.3
    crat *= (1 - plain) * (1 - 0.6 * margin)
    ejecta *= 1 - plain
    # A few fresh craters with bright rays of clean ice.
    rays = np.zeros(g.lat.shape, np.float32)
    rl, ro = random_points(rng, RAYED, (-60, 60))
    for la, lo in zip(rl, ro):
        r = float(rng.uniform(0.6, 1.4))
        c = unit(la, lo)
        east = np.cross([0, 0, 1], c)
        east /= np.linalg.norm(east)
        north = np.cross(c, east)
        d = angular_distance(g, la, lo)
        a = np.arctan2(p @ north, p @ east)
        # Rays: a few broad, soft streaks (low angular frequency), not a starburst of spikes.
        spokes = 0.5 + 0.5 * np.cos(a * int(rng.integers(3, 6)) + 1.3 * fbm(n[8], p * 3, 2) + rng.uniform(0, 6.3))
        rays = np.maximum(rays, smoothstep(9 * r, 1.0 * r, d) ** 1.5 * (0.3 + 0.7 * spokes) * smoothstep(0.6 * r, 1.3 * r, d))
        rays = np.maximum(rays, 0.6 * smoothstep(1.3 * r, 0.9 * r, d))
        t = d / r
        crat += crater(np.minimum(t, 3)) * (t < 3) * 0.08
    rays *= 1 - plain
    print(f"craters {time.time() - t0:.1f}s")

    # Convection cells on the plain: gentle tone and height between cell centres and edges.
    f1, f2, cid = worley(p * 10 + 0.6 * warp + 0.05 * np.stack([fbm(n[9], p * 60, 2)] * 3, -1), SEED)
    # Soft rounded domes with broad shallow troughs, not tiles: a sharp edge drew a crazed web.
    cell_edge = smoothstep(0.0, 0.5, f2 - f1)  # 0 at the troughs
    cell_tone = (cid % 97) / 96.0

    # Chasms: long, sub-parallel graben, from a stretched ridged field, inside the cave country.
    cd = angular_distance(g, CHASMS[0], CHASMS[1]) / CHASMS[2] + 0.3 * fbm(n[9], p * 4 + warp, 3)
    field = smoothstep(1.2, 0.5, cd)
    # Squashed hard along one axis so the crests run long and nearly parallel (graben, as on
    # Charon), few octaves so they're continuous valleys, not scratches.
    # Laid out in the surface's own frame at the cave country, so they run parallel there.
    c = unit(CHASMS[0], CHASMS[1])
    east = np.cross([0, 0, 1], c)
    east /= np.linalg.norm(east)
    north = np.cross(c, east)
    ang = np.radians(30)
    across = (p @ east) * np.cos(ang) + (p @ north) * np.sin(ang)
    along = -(p @ east) * np.sin(ang) + (p @ north) * np.cos(ang)
    q = np.stack([across * 30, along * 3, (p @ c) * 3], -1) + 0.4 * warp
    trough = smoothstep(0.75, 0.9, ridged(n[10], q, 2)) * field
    print(f"plain+chasms {time.time() - t0:.1f}s")

    # Height: one field, the plain sunk and flat, chasms cut, craters.
    h = 0.5 + 0.25 * base + 0.12 * (ridges - 0.5) * (1 + dark) + 0.03 * detail
    # The plain's ice laps up over a wide margin, so its edge is a gentle slope, not a scarp
    # (a narrow drop cast a hard straight line in low sun).
    sink = smoothstep(1.45, 0.8, pd)
    h = h * (1 - sink) + (0.38 + 0.003 * cell_edge) * sink
    h = h + crat - 0.15 * trough
    height = np.clip(h, 0, 1)

    # --- Colour ---------------------------------------------------------------------------
    upland = ramp(
        np.clip(0.5 + 0.9 * base + 0.3 * (ridges - 0.5), 0, 1),
        [
            (0.0, (0.5, 0.52, 0.56)),  # grey-blue frosted lowland
            (0.5, (0.62, 0.63, 0.66)),
            (1.0, (0.72, 0.72, 0.73)),  # pale grey ridges
        ],
    )
    upland = upland * (0.9 + 0.12 * detail[..., None])
    darkrgb = np.array([0.23, 0.22, 0.215], np.float32) * (0.8 + 0.4 * ridges[..., None]) * (0.9 + 0.2 * detail[..., None])
    rgb = upland * (1 - 0.85 * dark[..., None]) + darkrgb * 0.85 * dark[..., None]
    # Crater floors a little darker, ejecta a little brighter: old dust over ice.
    floor = np.clip(-crat * 8, 0, 1)[..., None]
    rgb = rgb * (1 - 0.06 * floor) * (1 + 0.1 * np.clip(ejecta, 0, 1)[..., None])
    rgb = rgb * (1 - rays[..., None] * 0.45) + np.array([0.84, 0.86, 0.88], np.float32) * rays[..., None] * 0.45
    # Chasm floors: fresh bluish ice.
    rgb = rgb * (1 - 0.25 * trough[..., None]) + np.array([0.55, 0.62, 0.7], np.float32) * 0.25 * trough[..., None]
    # The plain: bright cream-white ice, cells faintly varied, troughs barely darker.
    # Neutral, a touch cool: a cream white rendered khaki-olive under the warm sun.
    plainrgb = np.array([0.8, 0.81, 0.83], np.float32) * (0.98 + 0.02 * cell_edge[..., None])
    rgb = rgb * (1 - 0.5 * margin[..., None]) + np.array([0.78, 0.78, 0.77], np.float32) * 0.5 * margin[..., None]
    rgb = rgb * (1 - plain[..., None]) + plainrgb * plain[..., None]
    # Polar frost: soft, ragged, brightest at the poles.
    frost = smoothstep(58, 80, np.abs(lat) + 10 * fbm(n[11], p * 6 + warp, 4))
    rgb = rgb * (1 - 0.6 * frost[..., None]) + np.array([0.85, 0.87, 0.9], np.float32) * 0.6 * frost[..., None]
    print(f"colour {time.time() - t0:.1f}s")

    # --- Lights: outposts only -------------------------------------------------------------
    glint = np.random.default_rng(SEED + 1).random(g.lat.shape).astype(np.float32)
    lights = np.zeros(g.lat.shape, np.float32)
    for la, lo, r, b in LIGHTS:
        d = angular_distance(g, la, lo) / r
        # A small cluster and a soft halo about three times wider, so an outpost shows from orbit.
        lights += b * (smoothstep(1.0, 0.2, d) + 0.6 * (glint > 0.7) * smoothstep(2.5, 1.0, d) + 0.25 * smoothstep(3.5, 0.5, d))
    emissive = LAMP * np.clip(lights, 0, 1)[..., None]

    # A touch cooler overall: under the warm sun the blue-grey read sepia.
    rgb = rgb * np.array([0.98, 1.0, 1.04], np.float32)
    rough = np.clip(0.8 - 0.25 * plain - 0.1 * frost, 0, 1)
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.045, strength=1.0))
    write_pins(out / "pins.json", "Hielo", [])
    print(f"done {time.time() - t0:.1f}s -> {out}, plain {float((plain > 0.5).mean()):.3f}, dark {float((dark > 0.5).mean()):.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/hielo")
    generate(**vars(ap.parse_args()))

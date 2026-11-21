"""Gonhirrim's seven moons: generate texture maps and place pins from the specs below.

    python3 tools/planets/moons.py [names...] [--width 2048] [--out web/static/system]

Lore (see .ideas/projects/solar-system-3d/bodies/gonhirrim-moons.md and QUESTIONS.md):
- Dwarven mining moons, one god per moon. "Largely mining colonies"; they "completely
  rejected terraforming". All seven have air, weather and inhabitants (DM, Nov 2026).
- Broadly similar, each with its own character. So: one shared generator (rock shaped by a
  single warped noise field, craters, mining pits, settlement lights, a cloud layer) and a
  style per moon drawn from its god and its name.
- Durinfol (Thiton, water/life): the saltwater Crystal Coral Lake, Erebôr at its north end,
  the floating temple at its south end (Pilgrimage on Durinfol; WINEPRESS). Temperate.
- Broadbeam (Gliten, air/balance): mountains above a still "great fog"; stratus cloud
  (The Floating Cube; Stories in Gliten's Chapel).
- Ironfist (Mazoë, justice/courage): Darnit's home; the Golly mines; the Lady's Ladle and the
  Colosseum of Mazoë in one town (The Lady's Ladle…ing Stew; Thunderbowl Fights).
- Firebeard (Tyronóë, dreams), Blacklock (Moronóë, hearth), Stiffbeard (Yafel, knowledge),
  Stonefoot (Glitonea, earth/law): nothing beyond the god; styled from god and name.

Convention: the moons are taken to be tidally locked, with lon 0 facing Gonhirrim.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

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

C = tuple[float, float, float]

MOONS: dict[str, dict] = {
    "durinfol": dict(
        name="Durinfol",
        seed=301,
        water=0.40,
        mountains=0.45,
        rock=[(0, (0.30, 0.34, 0.20)), (0.35, (0.38, 0.40, 0.24)), (0.65, (0.46, 0.40, 0.31)), (1, (0.62, 0.58, 0.54))],
        rock2=[(0, (0.24, 0.36, 0.18)), (0.5, (0.34, 0.42, 0.22)), (1, (0.55, 0.52, 0.45))],
        sea=((0.03, 0.12, 0.20), (0.07, 0.34, 0.40)),
        ice=68,
        craters=6,
        mine_pits=10,
        settlements=16,
        clouds=0.42,
        features=[
            dict(kind="lake", lat=12, lon=30, ax=2.6, ay=6.2, colour=(0.10, 0.52, 0.52)),
            dict(kind="town", lat=18.5, lon=30, r=1.3, bright=1.6),
            dict(kind="town", lat=5.8, lon=30, r=0.35, bright=0.8),
        ],
        pins=[
            dict(name="Erebôr", lat=18.5, lon=30, confidence="layout"),
            dict(name="Temple of Thiton (Durinfol)", lat=5.8, lon=30, confidence="layout"),
            dict(name="Crystal Coral Lake", lat=12, lon=31.5, confidence="guess"),
        ],
    ),
    "broadbeam": dict(
        name="Broadbeam",
        seed=302,
        water=0.06,
        mountains=1.0,
        rock=[(0, (0.33, 0.33, 0.33)), (0.4, (0.50, 0.48, 0.45)), (0.75, (0.64, 0.61, 0.56)), (1, (0.82, 0.81, 0.80))],
        rock2=[(0, (0.40, 0.36, 0.30)), (0.5, (0.60, 0.55, 0.46)), (1, (0.78, 0.74, 0.66))],
        sea=((0.06, 0.10, 0.16), (0.16, 0.26, 0.32)),
        ice=74,
        craters=10,
        mine_pits=14,
        settlements=9,
        clouds=0.40,
        fog=0.75,
        features=[dict(kind="highland", lat=35, lon=-40, r=10, height=0.35)],
        pins=[dict(name="Gliten's Floating Cube Chapel", lat=35, lon=-40, confidence="guess")],
    ),
    "ironfist": dict(
        name="Ironfist",
        seed=303,
        water=0.06,
        mountains=0.7,
        rock=[(0, (0.22, 0.09, 0.06)), (0.35, (0.40, 0.16, 0.09)), (0.7, (0.56, 0.27, 0.15)), (1, (0.70, 0.45, 0.32))],
        rock2=[(0, (0.18, 0.11, 0.09)), (0.5, (0.33, 0.20, 0.15)), (1, (0.52, 0.38, 0.30))],
        sea=((0.05, 0.07, 0.10), (0.14, 0.20, 0.24)),
        ice=78,
        craters=14,
        mine_pits=26,
        settlements=16,
        clouds=0.18,
        features=[
            dict(kind="mines", lat=-17, lon=63, r=5.0, pits=28),
            dict(kind="town", lat=-20, lon=60, r=1.1, bright=1.4),
        ],
        pins=[
            dict(name="Lady's Ladle", lat=-20.4, lon=59.4, confidence="layout"),
            dict(name="Colosseum of Mazoë", lat=-19.6, lon=60.7, confidence="layout"),
            dict(name="Golly mines", lat=-16.5, lon=64, confidence="layout"),
        ],
    ),
    "firebeard": dict(
        name="Firebeard",
        seed=304,
        water=0.05,
        mountains=0.6,
        rock=[(0, (0.20, 0.12, 0.18)), (0.35, (0.38, 0.20, 0.18)), (0.7, (0.58, 0.30, 0.16)), (1, (0.76, 0.52, 0.34))],
        rock2=[(0, (0.18, 0.12, 0.24)), (0.5, (0.34, 0.24, 0.40)), (1, (0.56, 0.46, 0.58))],
        sea=((0.08, 0.05, 0.14), (0.20, 0.14, 0.32)),
        ice=80,
        craters=12,
        mine_pits=12,
        settlements=10,
        clouds=0.22,
        features=[],
        pins=[],
    ),
    "blacklock": dict(
        name="Blacklock",
        seed=305,
        water=0.08,
        mountains=0.55,
        rock=[(0, (0.06, 0.06, 0.06)), (0.4, (0.13, 0.12, 0.11)), (0.75, (0.22, 0.20, 0.18)), (1, (0.36, 0.34, 0.32))],
        rock2=[(0, (0.10, 0.07, 0.05)), (0.5, (0.20, 0.14, 0.10)), (1, (0.34, 0.27, 0.21))],
        sea=((0.03, 0.04, 0.06), (0.10, 0.13, 0.16)),
        ice=80,
        craters=12,
        mine_pits=16,
        settlements=30,
        light_boost=1.4,
        clouds=0.2,
        features=[],
        pins=[],
    ),
    "stiffbeard": dict(
        name="Stiffbeard",
        seed=306,
        water=0.07,
        mountains=0.35,
        terraces=7,
        rock=[(0, (0.46, 0.42, 0.36)), (0.4, (0.64, 0.60, 0.52)), (0.75, (0.78, 0.75, 0.68)), (1, (0.90, 0.88, 0.84))],
        rock2=[(0, (0.52, 0.44, 0.32)), (0.5, (0.70, 0.62, 0.48)), (1, (0.86, 0.80, 0.68))],
        sea=((0.05, 0.10, 0.14), (0.16, 0.30, 0.34)),
        ice=76,
        craters=10,
        mine_pits=14,
        settlements=12,
        clouds=0.25,
        features=[],
        pins=[],
    ),
    "stonefoot": dict(
        name="Stonefoot",
        seed=307,
        water=0.03,
        mountains=0.4,
        rock=[(0, (0.20, 0.16, 0.12)), (0.4, (0.34, 0.28, 0.22)), (0.75, (0.46, 0.40, 0.33)), (1, (0.60, 0.55, 0.48))],
        rock2=[(0, (0.24, 0.22, 0.20)), (0.5, (0.38, 0.36, 0.33)), (1, (0.55, 0.53, 0.50))],
        sea=((0.05, 0.07, 0.08), (0.14, 0.20, 0.20)),
        ice=82,
        craters=220,
        crater_max=11.0,
        mine_pits=16,
        settlements=10,
        clouds=0.14,
        features=[],
        pins=[],
    ),
}

LIGHT = np.array([1.0, 0.72, 0.40], np.float32)


def rank(x: np.ndarray) -> np.ndarray:
    """Rank-normalise to 0..1, so thresholds mean area fractions at any resolution."""
    u = np.empty(x.size, np.float32)
    u[np.argsort(x, axis=None)] = np.linspace(0, 1, x.size, dtype=np.float32)
    return u.reshape(x.shape)


def ellipse(g, lat, lon, ax, ay):
    """Elliptical distance (1 at the edge) around a point, axes in degrees of lon/lat."""
    dlat = (np.degrees(g.lat) - lat) / ay
    dlon = ((np.degrees(g.lon) - lon + 180) % 360 - 180) * np.cos(np.radians(lat)) / ax
    return np.sqrt(dlat**2 + dlon**2)


def random_points(rng, n, lat_range=(-70, 70)):
    """Points spread evenly over the sphere (lat limited)."""
    z = rng.uniform(np.sin(np.radians(lat_range[0])), np.sin(np.radians(lat_range[1])), n)
    return np.degrees(np.arcsin(z)), rng.uniform(-180, 180, n)


def crater(t: np.ndarray) -> np.ndarray:
    """Crater profile against distance in crater radii: bowl, raised rim, fading ejecta."""
    bowl = -(1 - np.minimum(t, 1) ** 2) * (t < 1)
    rim = 0.35 * np.exp(-(((t - 1) / 0.18) ** 2))
    return bowl + rim


def generate(slug: str, m: dict, width: int, out_root: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(m["seed"])
    n1, n2, n3, n4, n5, n6 = (Noise3(m["seed"] * 10 + i) for i in range(6))
    p = g.xyz

    # One warped field shapes everything: highlands, basins, coasts.
    warp = np.stack([fbm(n1, p * 1.8 + 11, 5), fbm(n2, p * 1.8 + 23, 5), fbm(n3, p * 1.8 + 37, 5)], -1)
    base = fbm(n4, p * 2.2 + warp * 0.9, octaves=9)
    ridges = ridged(n5, p * 3.6 + warp * 0.7, octaves=7)
    h = base + m["mountains"] * 0.55 * (ridges - 0.5)
    geology = fbm(n6, p * 1.4 + warp * 0.5, octaves=5)  # which rock type, slowly varying
    print(f"  {slug}: field {time.time() - t0:.1f}s")

    for f in m["features"]:
        if f["kind"] == "highland":
            d = angular_distance(g, f["lat"], f["lon"]) / f["r"]
            h = h + f["height"] * smoothstep(1.3, 0.2, d) * (0.6 + 0.8 * ridges)

    u = rank(h)
    if m.get("terraces"):  # stepped mesas and scarps
        k = m["terraces"]
        s = u * k
        u = (np.floor(s) + smoothstep(0.7, 1.0, s - np.floor(s))) / k

    # Craters: a power-law spread of sizes, more small than large.
    crat = np.zeros_like(u)
    ejecta = np.zeros_like(u)
    lats, lons = random_points(rng, m["craters"], (-80, 80))
    radii = 0.5 + m.get("crater_max", 7.0) * rng.uniform(0, 1, m["craters"]) ** 2.5
    for la, lo, r in zip(lats, lons, radii):
        t = angular_distance(g, la, lo) / r
        near = t < 3
        crat[near] += crater(t[near]) * (0.10 + 0.012 * r)
        ejecta[near] += np.exp(-((t[near] - 1.6) ** 2) / 0.5) * 0.4 * (0.6 + 0.8 * fbm(n3, p[near] * 40, 2))
    u = np.clip(u + crat, 0, 1.2)

    # Mining pits: terraced, with pale spoil around them.
    pits = []
    plat, plon = random_points(rng, m["mine_pits"])
    pits += [(a, b, rng.uniform(0.35, 0.9)) for a, b in zip(plat, plon)]
    for f in m["features"]:
        if f["kind"] == "mines":
            for _ in range(f["pits"]):
                rr = f["r"] * np.sqrt(rng.uniform())
                ang = rng.uniform(0, 2 * np.pi)
                pits.append((f["lat"] + rr * np.sin(ang), f["lon"] + rr * np.cos(ang) / np.cos(np.radians(f["lat"])), rng.uniform(0.3, 1.1)))
    pit_depth = np.zeros_like(u)
    spoil = np.zeros_like(u)
    rings = np.zeros_like(u)
    for la, lo, r in pits:
        t = angular_distance(g, la, lo) / r
        near = t < 2.2
        tn = t[near]
        steps = np.floor(np.clip(1 - tn, 0, 1) * 5) / 5
        pit_depth[near] = np.maximum(pit_depth[near], steps)
        rings[near] = np.maximum(rings[near], (tn < 1) * (0.5 + 0.5 * np.cos(tn * np.pi * 10)))
        spoil[near] = np.maximum(spoil[near], smoothstep(2.2, 1.0, tn) * (tn >= 1))
    u = u - pit_depth * 0.08
    print(f"  {slug}: craters+pits {time.time() - t0:.1f}s")

    # Water fills the lowest ground; then lakes from the spec.
    sea_level = np.quantile(u, m["water"]) if m["water"] > 0 else -1
    water = smoothstep(sea_level + 0.004, sea_level - 0.004, u)
    depth = np.clip((sea_level - u) / max(sea_level, 1e-3), 0, 1)
    water_rgb = np.array(m["sea"][1], np.float32) * (1 - depth[..., None]) + np.array(m["sea"][0], np.float32) * depth[..., None]
    for f in m["features"]:
        if f["kind"] == "lake":
            d = ellipse(g, f["lat"], f["lon"], f["ax"], f["ay"])
            d = d + 0.08 * fbm(n1, p * 30, 4)
            lake = smoothstep(1.0, 0.94, d)
            shallow = smoothstep(0.55, 1.0, d)
            col = np.array(f["colour"], np.float32) * (0.75 + 0.35 * shallow[..., None])
            water_rgb = water_rgb * (1 - lake[..., None]) + col * lake[..., None]
            water = np.maximum(water, lake)
            u = np.where(lake > 0.5, np.minimum(u, sea_level), u)

    # Land colour: elevation above the water, two rock types blended by geology.
    e = np.clip((u - sea_level) / (1 - sea_level), 0, 1)
    rock = ramp(e, m["rock"])
    rock2 = ramp(e, m["rock2"])
    mix = smoothstep(-0.25, 0.35, geology)[..., None]
    land = rock * (1 - mix) + rock2 * mix
    grain = fbm(n2, p * 60 + warp * 3, 4)
    land = land * (0.88 + 0.24 * grain[..., None])
    # Ridge crests catch light, gullies darken: detail at every scale from the same field.
    land = land * (0.78 + 0.44 * ridges[..., None])
    floor = np.clip(-crat * 6, 0, 1)[..., None]
    rim = np.clip(crat * 8, 0, 1)[..., None]
    land = land * (1 + 0.3 * ejecta[..., None]) * (1 - 0.3 * floor) * (1 + 0.35 * rim)
    pale = np.array(m["rock"][-1][1], np.float32)
    land = land * (1 - 0.45 * spoil[..., None]) + pale * 0.45 * spoil[..., None]
    land = land * (1 - 0.25 * rings[..., None])
    land = land * (1 - 0.35 * pit_depth[..., None])

    # Polar ice.
    ice = smoothstep(m["ice"] - 2, m["ice"] + 4, np.abs(np.degrees(g.lat)) + 14 * geology + 6 * grain + 8 * (e - 0.4))
    ice_rgb = np.array([0.88, 0.90, 0.92], np.float32)

    rgb = land * (1 - water[..., None]) + water_rgb * water[..., None]
    rgb = rgb * (1 - ice[..., None]) + ice_rgb * ice[..., None]

    # Settlements: clusters of lights, on low ground near water or mines.
    emissive = np.zeros_like(rgb)
    lights = np.zeros_like(u)
    slat, slon = random_points(rng, m["settlements"] * 4)
    pick = []
    for la, lo in zip(slat, slon):
        i = int((90 - la) / 180 * g.height)
        j = int((lo + 180) / 360 * width)
        i, j = min(i, g.height - 1), min(j, width - 1)
        if water[i, j] < 0.5 and ice[i, j] < 0.5 and e[i, j] < 0.6:
            pick.append((la, lo, rng.uniform(0.4, 1.0), rng.uniform(0.5, 1.0)))
        if len(pick) >= m["settlements"]:
            break
    pick += [(f["lat"], f["lon"], f["r"], f["bright"]) for f in m["features"] if f["kind"] == "town"]
    sprawl = fbm(n3, p * 220, 3)
    for la, lo, r, b in pick:
        t = angular_distance(g, la, lo) / r
        near = t < 1.6
        core = smoothstep(1.6, 0.0, t[near])
        lights[near] += b * core * smoothstep(0.05 - 0.25 * core, 0.35, sprawl[near])
    for la, lo, r in pits:
        t = angular_distance(g, la, lo) / r
        near = t < 1.4
        lights[near] += 0.35 * smoothstep(1.4, 0.8, t[near]) * smoothstep(0.1, 0.3, sprawl[near])
    lights = np.clip(lights * m.get("light_boost", 1.0), 0, 1.5) * (1 - water) * (1 - ice)
    emissive = LIGHT * lights[..., None] * 0.8
    rgb = rgb * (1 - 0.3 * np.clip(lights, 0, 1)[..., None]) + np.array([0.45, 0.42, 0.40], np.float32) * 0.3 * np.clip(lights, 0, 1)[..., None]
    print(f"  {slug}: colour+lights {time.time() - t0:.1f}s")

    # Clouds: their own warped field; Broadbeam's fog also fills the valleys.
    cw = np.stack([fbm(n5, p * 2.5 + 3, 4), fbm(n6, p * 2.5 + 9, 4), fbm(n4, p * 2.5 + 17, 4)], -1)
    # Stretched a little east-west, as winds shear cloud along latitude.
    pc = p * np.array([1.0, 1.0, 1.8], np.float32)
    cf = rank(fbm(n1, pc * 3.6 + cw * 1.6, octaves=8) + 0.35 * fbm(n2, pc * 16 + cw * 3, 5))
    cover = m["clouds"]
    clouds = smoothstep(1 - cover, 1 - cover + 0.3, cf) ** 1.5
    if m.get("fog"):
        clouds = np.maximum(clouds, m["fog"] * smoothstep(0.32, 0.12, e) * (1 - water) * smoothstep(-0.3, 0.3, fbm(n3, p * 5, 4)))

    rough = np.where(water > 0.5, 0.25, 0.88 - 0.25 * ice)
    height = np.clip(u, 0, 1) * (1 - water) + np.clip(sea_level, 0, 1) * water

    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.05 * (0.5 + m["mountains"]), strength=1.0))
    save_gray(out / "clouds.webp", clouds)
    write_pins(out / "pins.json", m["name"], m["pins"])
    print(f"  {slug}: done {time.time() - t0:.1f}s -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", default=list(MOONS))
    ap.add_argument("--width", type=int, default=2048)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system")
    args = ap.parse_args()
    for name in args.names:
        generate(name, MOONS[name], args.width, args.out)

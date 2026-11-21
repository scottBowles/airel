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
        settled=0.32,
        clouds=0.42,
        features=[
            dict(kind="lake", lat=12, lon=30, ax=3.2, ay=6.8, colour=(0.10, 0.52, 0.52)),
            dict(kind="town", lat=18.5, lon=30, r=1.6, bright=0.9),
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
        settled=0.18,
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
        settled=0.26,
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
        settled=0.38,
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
        rock=[(0, (0.18, 0.15, 0.13)), (0.4, (0.30, 0.26, 0.23)), (0.75, (0.42, 0.38, 0.34)), (1, (0.56, 0.53, 0.49))],
        rock2=[(0, (0.22, 0.21, 0.20)), (0.5, (0.36, 0.35, 0.34)), (1, (0.52, 0.51, 0.50))],
        sea=((0.05, 0.07, 0.08), (0.14, 0.20, 0.20)),
        ice=82,
        craters=220,
        crater_max=11.0,
        crater_contrast=1.8,
        mine_pits=16,
        settlements=10,
        settled=0.14,
        clouds=0.14,
        features=[],
        pins=[],
    ),
    # Not one of Gonhirrim's: Hyang Wan's moon. Two logs see it set over Mulgogi; nothing else
    # is known, so it is airless and uninhabited: plain grey rock, heavily cratered.
    "hyang-wan-moon": dict(
        name="Hyang Wan's moon",
        seed=411,
        water=0.0,
        mountains=0.3,
        rock=[(0, (0.20, 0.20, 0.21)), (0.4, (0.33, 0.33, 0.34)), (0.75, (0.46, 0.46, 0.46)), (1, (0.62, 0.62, 0.61))],
        rock2=[(0, (0.16, 0.16, 0.17)), (0.5, (0.27, 0.27, 0.28)), (1, (0.44, 0.44, 0.45))],
        sea=((0, 0, 0), (0, 0, 0)),
        ice=99,
        craters=320,
        crater_max=13.0,
        crater_contrast=2.0,
        mine_pits=0,
        settlements=0,
        settled=0,
        clouds=0,
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

    # Lakes from the spec sit in raised basins, so land surrounds them; their shores follow
    # the same noise as everything else instead of a drawn outline.
    lakes = []
    for f in m["features"]:
        if f["kind"] == "lake":
            # Warp the ellipse's coordinates by a few degrees: bays, points and a ragged shore.
            wl = 0.55 * f["ay"] * fbm(n3, p * 5 + warp * 0.8 + 2.0, 6)
            wo = 0.55 * f["ax"] * fbm(n4, p * 5 + warp * 0.8 + 9.0, 6)
            dlat = (np.degrees(g.lat) + wl - f["lat"]) / f["ay"]
            dlon = ((np.degrees(g.lon) + wo - f["lon"] + 180) % 360 - 180) * np.cos(np.radians(f["lat"])) / f["ax"]
            d = np.sqrt(dlat**2 + dlon**2)
            lakes.append((f, d + 0.45 * fbm(n1, p * 9 + warp * 0.6, 5) + 0.1 * fbm(n2, p * 40, 3)))

    # Water fills the lowest ground.
    sea_level = np.quantile(u, m["water"]) if m["water"] > 0 else -1
    for f, d in lakes:
        basin = smoothstep(2.8, 1.7, d)
        u = u * (1 - basin) + np.maximum(u, sea_level + 0.05) * basin
    water = smoothstep(sea_level + 0.004, sea_level - 0.004, u)
    depth = np.clip((sea_level - u) / max(sea_level, 1e-3), 0, 1)
    sea_deep, sea_shallow = (np.array(c, np.float32) for c in (m["sea"][0], m["sea"][1]))
    water_rgb = sea_shallow * (1 - depth[..., None]) + sea_deep * depth[..., None]
    for f, d in lakes:
        lake = smoothstep(1.0, 0.92, d)
        ldepth = smoothstep(0.95, 0.2, d) * 0.6
        col = sea_shallow * (1 - ldepth[..., None]) + sea_deep * ldepth[..., None]
        # Coral: a faint cast of the lake's own colour over all of it. A brighter rim reads
        # as an outline, since the sea coasts have none.
        col = col * 0.85 + np.array(f["colour"], np.float32) * 0.15
        water_rgb = water_rgb * (1 - lake[..., None]) + col * lake[..., None]
        water = np.maximum(water, lake)
        u = np.where(lake > 0.5, sea_level - 0.01, u)

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
    cc = m.get("crater_contrast", 1.0)
    land = land * (1 + 0.3 * cc * ejecta[..., None]) * (1 - 0.3 * cc * floor) * (1 + 0.35 * cc * rim)
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
    # Towns (small sprawls) and many more villages (single specks), on habitable ground.
    def habitable(n_want, tries, r_range, b_range):
        out = []
        la_, lo_ = random_points(rng, tries)
        for la, lo in zip(la_, lo_):
            i = min(int((90 - la) / 180 * g.height), g.height - 1)
            j = min(int((lo + 180) / 360 * width), width - 1)
            if water[i, j] < 0.5 and ice[i, j] < 0.5 and e[i, j] < 0.6:
                out.append((la, lo, rng.uniform(*r_range), rng.uniform(*b_range)))
            if len(out) >= n_want:
                break
        return out

    n_towns = m["settlements"] * 3
    pick = habitable(n_towns, n_towns * 6, (0.3, 0.8), (0.5, 1.0))
    pick += habitable(n_towns * 3, n_towns * 18, (0.18, 0.35), (0.4, 0.8))
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
    # Settled regions: a speckle of homesteads and roads over some of the low ground,
    # thickest near coasts, so the night side reads as inhabited rather than a few dots.
    region = smoothstep(1 - m.get("settled", 0.2), 1.0001, rank(fbm(n6, p * 3.0 + warp * 0.8 + 5.5, 5)))
    coast = smoothstep(0.35, 0.0, e)
    speck = smoothstep(0.80, 0.93, rank(fbm(n2, p * 260 + 1.7, 2))) * (0.4 + 0.6 * smoothstep(0.4, 0.8, rank(fbm(n4, p * 50, 3))))
    if m.get("settled", 0.2) > 0:
        lights += 0.7 * region * (0.35 + 0.65 * coast) * speck
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

    # Water: calm patches shine and windy ones don't, so sunglint is a soft, broken sheen,
    # streaked along the winds, rather than one clean mirror spot.
    pw = p * np.array([1.0, 1.0, 2.5], np.float32)
    wind = rank(fbm(n5, pw * 4 + cw * 1.2 + 4.2, 5) + 0.4 * fbm(n6, pw * 22 + 8.1, 3))
    rough_water = 0.43 + 0.3 * wind
    rough = np.where(water > 0.5, rough_water, 0.88 - 0.25 * ice)
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

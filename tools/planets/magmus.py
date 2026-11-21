"""Magmus: generate texture maps and place pins from the feature spec below.

    python3 tools/planets/magmus.py [--width 4096] [--out web/static/system/magmus]

Lore (DB notes, "On the Planets", session logs):
- The surface is a chaotic lava ocean that ships sail ("a boat on top of chaotic lava ocean",
  Quarrel's Cargo, 2023-10-02). Lava flows, geysers; "a land that's burning itself".
- The 12 Solidlands are where the lava doesn't flow: "waypoints of immobility in a
  constantly swirling landscape". The north cap (Roaring Kettle) is the largest (Taco Night
  and Tide Pools, 2023-10-23).
- Three Wells: Roaring Kettle (north cap), Well of Destiny (south cap), Well of Wisdom (an
  equatorial island / massive archipelago).
- "Cleaveland is nestled between the Mother of Giants and the Mountain of the Fire Giants"
  (Escape to the Phoenix's Wrath, 2024-07-01); its capital "moves with the lava".
- Old Bae is the northwestern-most part of greater Cleaveland (2024-11-18).
- Brawnheim is in the north; Hrothulf is from the southwest (2022-12-05).
- Most Solidlands in the southwest are crossed off on the Vardum's map (2024-10-21): Vigrid,
  Gungnir and Surtesy are placed there.

Latitudes and longitudes not fixed by the lore are this script's choices: change them here
and re-run. `confidence` on each pin says which is which.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from planetgen import (
    worley,
    veins,
    ramp,
    Noise3,
    angular_distance,
    fbm,
    make_grid,
    normal_map,
    ridged,
    save_gray,
    save_rgb,
    segment_distance,
    smoothstep,
    write_pins,
)

SEED = 1729

# Solidlands. kind: blob (rounded landmass), cap (polar), archipelago, strip (along an arc).
# height: peak elevation above the lava (0..1); profile: mountain | plateau | mesa | shield | plain | cone
SOLIDLANDS = [
    dict(name="The Roaring Kettle", kind="cap", pole=1, edge=62, profile="plain", height=0.25),
    dict(name="The Well of Destiny", kind="cap", pole=-1, edge=-66, profile="plain", height=0.22),
    dict(name="The Well of Wisdom", kind="archipelago", lat=2, lon=128, spread=(12, 34), islands=60, height=0.18),
    dict(name="Ymir — the Mother of all Giants", kind="blob", lat=24, lon=9, r=11.9, profile="mountain", height=1.0),
    dict(name="Muspell — Mountain of the Fire Giants", kind="blob", lat=20, lon=-12, r=11.2, profile="mountain", height=0.8),
    dict(name="Thestal Halls of Heorot", kind="blob", lat=44, lon=-68, r=14.0, profile="plateau", height=0.35),
    dict(name="Vigrid, the Last Battlefield", kind="blob", lat=-27, lon=-108, r=15.4, profile="plain", height=0.15),
    dict(name="Kenaz", kind="blob", lat=12, lon=62, r=7.7, profile="mesa", height=0.45),
    dict(name="Sinmara — an upland of cinders", kind="blob", lat=-38, lon=38, r=12.6, profile="plateau", height=0.4),
    dict(name="Surtesy — a volcanic island", kind="blob", lat=-12, lon=-58, r=4.9, profile="cone", height=0.6),
    dict(name="Svalinn — the Great Shield", kind="blob", lat=30, lon=128, r=16.8, profile="shield", height=0.45),
    dict(name="Gungnir — a thin stretch of lava delta marshlands", kind="strip", a=(-42, -150), b=(-22, -126), r=3.6, profile="plain", height=0.06),
]

# The Vale of Cleaveland: a lava channel between Ymir and Muspell, where the capital rides the flow.
CLEAVELAND = dict(a=(34, -2.5), b=(8, -1.0), r=1.6)

# Towns that show lights on the night side (others get small scattered settlements).
TOWN_LIGHTS = {"Vale of Cleaveland", "Old Bae", "Thestal Halls of Heorot", "Brawnheim", "Kenaz", "Hot Springs of Canaz"}

# Place pins: name as in the DB, lat/lon, and how sure the placement is.
#   lore: the logs fix it; layout: the logs give the rough area; guess: nothing in the lore yet
PINS = [
    dict(name="The Roaring Kettle", lat=80, lon=0, confidence="lore"),
    dict(name="The Well of Destiny", lat=-80, lon=0, confidence="lore"),
    dict(name="The Well of Wisdom", lat=2, lon=128, confidence="lore"),
    dict(name="Ymir — the Mother of all Giants", lat=24, lon=9, confidence="layout"),
    dict(name="Forge at Mother of Giants", lat=24.5, lon=10, confidence="layout"),
    dict(name="Muspell — Mountain of the Fire Giants", lat=20, lon=-12, confidence="layout"),
    dict(name="Vale of Cleaveland", lat=21, lon=-1.5, confidence="lore"),
    dict(name="Old Bae", lat=31, lon=-4, confidence="layout"),
    dict(name="Thestal Halls of Heorot", lat=44, lon=-68, confidence="guess"),
    dict(name="Brawnheim", lat=67.5, lon=-35, confidence="layout"),
    dict(name="Vigrid, the Last Battlefield", lat=-27, lon=-108, confidence="layout"),
    dict(name="Kenaz", lat=12, lon=62, confidence="guess"),
    dict(name="Hot Springs of Canaz", lat=12, lon=62.4, confidence="guess"),
    dict(name="Sinmara — an upland of cinders", lat=-38, lon=38, confidence="guess"),
    dict(name="Surtesy — a volcanic island", lat=-12, lon=-58, confidence="layout"),
    dict(name="Svalinn — the Great Shield", lat=30, lon=128, confidence="guess"),
    dict(name="Gungnir — a thin stretch of lava delta marshlands", lat=-32, lon=-138, confidence="layout"),
]


def profile_height(kind: str, t: np.ndarray, g) -> np.ndarray:
    """t = distance from centre / radius (0 centre, 1 coast). Returns 0..1 shape."""
    if kind == "mountain":
        return np.exp(-(t * 2.2) ** 2)
    if kind == "cone":
        cone = np.clip(1 - t, 0, 1) ** 1.4
        crater = smoothstep(0.18, 0.0, t) * 0.5
        return cone - crater
    if kind == "shield":
        return np.clip(1 - t * t, 0, 1) ** 0.7
    if kind == "plateau":
        return smoothstep(1.0, 0.55, t)
    if kind == "mesa":
        top = smoothstep(1.0, 0.8, t)
        lake = smoothstep(0.38, 0.25, t) * 0.55
        return top - lake
    return smoothstep(1.0, 0.3, t) * 0.6 + 0.4 * (t < 1)  # plain


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    p = g.xyz
    n1, n2, n3 = Noise3(SEED), Noise3(SEED + 1), Noise3(SEED + 2)
    lat_deg = np.degrees(g.lat)

    coast = fbm(n1, p * 4.0, octaves=6) + 0.5 * fbm(n3, p * 16.0, octaves=4)  # shared coastline wobble
    detail = fbm(n2, p * 9.0, octaves=6)  # land detail
    fine = fbm(n3, p * 40.0, octaves=4)  # small-island coastlines
    print(f"  noise base {time.time() - t0:.1f}s")

    land = np.zeros(g.lat.shape, np.float32)  # 0..1 land coverage
    elev = np.zeros(g.lat.shape, np.float32)  # land elevation 0..1
    ash = np.zeros(g.lat.shape, np.float32)  # pale ash/cinder tint
    glow_vents = np.zeros(g.lat.shape, np.float32)

    def add(mask, height):
        nonlocal land, elev
        land = np.maximum(land, mask)
        elev = np.maximum(elev, height * mask)

    for s in SOLIDLANDS:
        if s["kind"] == "cap":
            edge = s["edge"] + coast * 6
            t = (lat_deg - edge) * s["pole"]
            mask = smoothstep(-0.6, 0.6, t)
            add(mask, s["height"] * (0.6 + 0.4 * smoothstep(0, 15, t)))
        elif s["kind"] == "archipelago":
            rng = np.random.default_rng(SEED + 7)
            for _ in range(s["islands"]):
                la = s["lat"] + rng.normal() * s["spread"][0] / 2
                lo = s["lon"] + rng.normal() * s["spread"][1] / 2
                r = rng.uniform(0.6, 2.6)
                d = angular_distance(g, la, lo) / r + coast * 0.35 + 0.45 * fine
                add(smoothstep(1.0, 0.85, d), s["height"] * profile_height("cone", np.clip(d, 0, 1), g) + 0.04)
        else:
            if s["kind"] == "strip":
                d = segment_distance(g, s["a"], s["b"])
            else:
                d = angular_distance(g, s["lat"], s["lon"])
            t = d / s["r"] + coast * 0.55
            mask = smoothstep(1.0, 0.9, t)
            add(mask, s["height"] * profile_height(s["profile"], np.clip(t, 0, 1.2), g))
            if s["profile"] in ("mountain", "cone"):
                glow_vents = np.maximum(glow_vents, smoothstep(0.16, 0.0, t))
            if "cinders" in s["name"]:
                ash = np.maximum(ash, mask)

    # Cleaveland: a lava channel cut between Ymir and Muspell.
    vale = smoothstep(1.0, 0.0, segment_distance(g, CLEAVELAND["a"], CLEAVELAND["b"]) / CLEAVELAND["r"] + coast * 0.25)
    land = land * (1 - vale)
    elev = elev * (1 - vale)
    sea = 1 - land
    print(f"  features {time.time() - t0:.1f}s")

    # ---- Land relief: broken, multi-scale volcanic ground everywhere, ridges in the mountains.
    n4, n5 = Noise3(SEED + 3), Noise3(SEED + 4)
    ridges = ridged(n3, p * 14.0, octaves=6)
    rough_ground = fbm(n4, p * 60.0, octaves=5)  # metre-scale rubble, flows, cones
    cones = smoothstep(0.80, 0.95, ridged(n5, p * 34.0, octaves=2))  # small cinder cones and spatter ridges
    mountainous = smoothstep(0.3, 0.9, elev)
    elev_full = elev + land * (0.07 * detail + 0.04 * rough_ground + 0.06 * cones + 0.3 * mountainous * (ridges - 0.45))
    elev_full = np.clip(elev_full, 0, 1.3)
    print(f"  land {time.time() - t0:.1f}s")

    # ---- Lava: one heat field (0 cold crust … 1 white-hot) drives colour and glow.
    warp = np.stack([fbm(n1, p * 3 + 11, 4), fbm(n2, p * 3 + 23, 4), fbm(n3, p * 3 + 37, 4)], -1)
    swirl = fbm(n2, p * 6 + warp * 1.6, octaves=8)
    q = np.quantile(swirl, [0.04, 0.12, 0.35, 0.7])
    # Open molten lava in the lowest swirls, cooling through orange and red into crust.
    flow_heat = np.interp(swirl, q, [1.0, 0.62, 0.16, 0.04]).astype(np.float32)
    # Crust plates: cooler plate interiors, hotter edges; a branching crack network at two scales.
    plates = ridged(n4, p * 9 + warp * 1.2, octaves=3)
    # Crust breaks into polygonal plates (cellular noise): rifts of varying width between big
    # plates, finer cracks within them. Each plate has its own temperature, and crust is
    # warmer near a crack.
    wob = fbm(n4, p * 30, octaves=3)[..., None] * 0.06
    f1, f2, cell = worley(p * 11 + warp * 0.9 + wob, SEED + 21)
    edge_big = f2 - f1
    width = 0.03 + 0.05 * smoothstep(-0.3, 0.5, fbm(n5, p * 8, 3))
    cracks_big = smoothstep(width, 0.0, edge_big)
    g1, g2, cell_s = worley(p * 34 + warp * 1.6 + wob * 2, SEED + 22)
    cracks_mid = smoothstep(0.06, 0.0, g2 - g1) * smoothstep(0.2, 0.6, cell_s)  # not every plate is cracked
    print(f"  plates {time.time() - t0:.1f}s")
    plate_heat = 0.02 + 0.15 * cell ** 4 + 0.04 * cell_s
    near_crack = np.exp(-edge_big / 0.08) * 0.12
    cracks_mid_heat = cracks_mid * 0.45
    # Regions differ: active zones have hot, wide rifts; calm ones dull red seams.
    activity = smoothstep(-0.35, 0.35, fbm(n3, p * 2.5 + 5, 4))
    crack_heat = cracks_big * (0.18 + 0.55 * activity + 0.2 * cell)
    sea_heat = np.maximum.reduce([flow_heat, crack_heat, cracks_mid_heat * (0.5 + 0.5 * activity), plate_heat + near_crack])
    plates = cell
    print(f"  lava {time.time() - t0:.1f}s")

    # Rivers on land: a branching network that crosses the Solidlands from sea to sea, avoiding
    # the high ground; fine fissures feed it. Vents glow at the summits.
    rivers = np.maximum(veins(n3, p * 7 + warp * 1.0, 0.05), veins(n4, p * 16 + warp * 1.5, 0.035) * 0.7)
    rivers *= smoothstep(0.6, 0.15, elev_full)
    fissures = cracks_mid * smoothstep(0.8, 0.2, elev_full) * 0.8
    # Shorelines crumble: the land's edge is cooling flows and spatter, not a clean line.
    shore = smoothstep(0.0, 0.35, land) * smoothstep(0.95, 0.45, land)
    land_heat = np.maximum.reduce([rivers * 0.85, fissures * 0.5, glow_vents * 0.95, shore * (0.3 + 0.5 * cracks_big)])

    heat = land * land_heat + sea * sea_heat
    # Colours of heat: deep red → red → orange → yellow-orange → yellow-white.
    heat_rgb = ramp(heat, [(0.0, (0, 0, 0)), (0.08, (0.28, 0.02, 0.0)), (0.25, (0.75, 0.09, 0.01)),
                           (0.45, (1.0, 0.30, 0.03)), (0.7, (1.0, 0.58, 0.10)), (1.0, (1.0, 0.88, 0.5))])
    emissive = heat_rgb * (heat ** 1.2)[..., None]

    # ---- Towns: warm-white lights, so there's visible civilisation on the night side.
    rng = np.random.default_rng(SEED + 11)
    lights = np.zeros(g.lat.shape, np.float32)
    towns = [(pp["lat"], pp["lon"], 1.0) for pp in PINS if pp["name"] in TOWN_LIGHTS]
    for s_ in SOLIDLANDS:  # scattered smaller settlements on every Solidland
        if s_["kind"] in ("blob", "strip"):
            c = (s_["lat"], s_["lon"]) if s_["kind"] == "blob" else tuple((np.array(s_["a"]) + np.array(s_["b"])) / 2)
            for _ in range(3):
                towns.append((c[0] + rng.normal() * 3, c[1] + rng.normal() * 3, 0.45))
    for la, lo, w in towns:
        d = angular_distance(g, la, lo)
        cluster = np.exp(-(d / (0.9 * w + 0.4)) ** 2)
        lights = np.maximum(lights, cluster * smoothstep(0.55, 0.85, (fine + 1) / 2 + 0.2 * w) * w)
    lights *= land
    emissive += lights[..., None] * np.array([1.0, 0.82, 0.55], np.float32) * 0.8

    # ---- Albedo: basalt, rust and ochre, sulphur near heat, ash on the heights, obsidian flows.
    t = np.clip(0.5 + 0.8 * detail, 0, 1)
    rock = ramp(t, [(0.0, (0.11, 0.10, 0.10)), (0.3, (0.22, 0.18, 0.15)), (0.55, (0.38, 0.22, 0.12)),
                    (0.75, (0.52, 0.33, 0.15)), (0.9, (0.36, 0.30, 0.24)), (1.0, (0.28, 0.25, 0.22))])
    rubble = (0.85 + 0.3 * rough_ground)[..., None]
    rock = rock * rubble
    # Solidlands are old cooled lava: fractured into blocks with dark joints.
    joints = smoothstep(0.0, 0.05, g2 - g1) * 0.35 + smoothstep(0.0, 0.08, edge_big) * 0.25 + 0.4
    rock = rock * joints[..., None] * 1.35
    sulphur = (smoothstep(0.15, 0.5, np.maximum(land_heat, glow_vents * 0.6)) * smoothstep(-0.1, 0.4, fine))[..., None]
    rock = rock * (1 - sulphur * 0.7) + np.array([0.62, 0.55, 0.18], np.float32) * sulphur * 0.7
    ashy = np.clip(np.maximum(ash, smoothstep(0.7, 1.05, elev_full) * 0.7) * (0.7 + 0.3 * rough_ground), 0, 1)[..., None]
    rock = rock * (1 - ashy) + np.array([0.46, 0.44, 0.41], np.float32) * ashy
    obsidian = smoothstep(0.7, 0.85, plates) * smoothstep(0.3, 0.1, elev_full) * 0.6
    rock = rock * (1 - obsidian[..., None] * 0.8) + np.array([0.03, 0.03, 0.035], np.float32) * obsidian[..., None] * 0.8
    crust_c = ramp(plates, [(0.0, (0.05, 0.045, 0.045)), (0.5, (0.09, 0.05, 0.04)), (1.0, (0.16, 0.06, 0.04))])
    crust_c = crust_c * (0.8 + 0.4 * (rough_ground[..., None] + 1) / 2)
    hot = smoothstep(0.4, 0.85, heat)[..., None]
    base = rock * land[..., None] + crust_c * sea[..., None]
    albedo = base * (1 - hot) + heat_rgb * 0.8 * hot

    # ---- Roughness and height
    rough = land * (0.9 - 0.5 * obsidian - 0.2 * ashy[..., 0]) + sea * (0.75 - 0.4 * smoothstep(0.3, 0.8, heat))
    height = land * elev_full + sea * (0.012 * plates - 0.01 * smoothstep(0.3, 0.8, heat))

    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", albedo)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", np.clip(height, 0, 1))
    save_rgb(out / "normal.webp", normal_map(height * 0.09, strength=1.0))
    write_pins(out / "pins.json", "Magmus", PINS)
    print(f"  wrote {out} in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/magmus")
    a = ap.parse_args()
    generate(a.width, a.out)

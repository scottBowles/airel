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
            mask = smoothstep(-4, 4, t)
            add(mask, s["height"] * (0.6 + 0.4 * smoothstep(0, 15, t)))
        elif s["kind"] == "archipelago":
            rng = np.random.default_rng(SEED + 7)
            for _ in range(s["islands"]):
                la = s["lat"] + rng.normal() * s["spread"][0] / 2
                lo = s["lon"] + rng.normal() * s["spread"][1] / 2
                r = rng.uniform(0.6, 2.6)
                d = angular_distance(g, la, lo) / r + coast * 0.35 + 0.45 * fine
                add(smoothstep(1.2, 0.7, d), s["height"] * profile_height("cone", np.clip(d, 0, 1), g) + 0.04)
        else:
            if s["kind"] == "strip":
                d = segment_distance(g, s["a"], s["b"])
            else:
                d = angular_distance(g, s["lat"], s["lon"])
            t = d / s["r"] + coast * 0.55
            mask = smoothstep(1.25, 0.7, t)
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

    # One chaotic heat field drives everything: lava, coasts and the glow on the land.
    # (Separate pattern systems for plates, cracks and rivers didn't join up; one field does.)
    warp = np.stack([fbm(n1, p * 2.5 + 11, 5), fbm(n2, p * 2.5 + 23, 5), fbm(n3, p * 2.5 + 37, 5)], -1)
    warp2 = np.stack([fbm(n3, p * 6 + warp * 1.2 + 5, 4), fbm(n1, p * 6 + warp * 1.2 + 9, 4), fbm(n2, p * 6 + warp * 1.2 + 13, 4)], -1)
    n4, n5 = Noise3(SEED + 3), Noise3(SEED + 4)
    field = fbm(n2, p * 4.5 + warp * 1.8 + warp2 * 0.6, octaves=10)
    # Fine grain at every scale (the original Blender Magmus's strength), riding the same flow.
    field = field + 0.3 * fbm(n4, p * 30 + warp2 * 2.0, octaves=6) + 0.14 * fbm(n5, p * 120 + warp2 * 4.0, octaves=4)
    # Rank-normalise to 0..1 so the proportions hold at any resolution.
    u = (np.argsort(np.argsort(field.ravel())) / (field.size - 1)).reshape(field.shape).astype(np.float32)
    print(f"  field {time.time() - t0:.1f}s")

    # Coasts follow the field: hot lava eats into the land's edge, cool crust extends it.
    land = smoothstep(0.35, 0.65, land + (0.5 - u) * 0.55)
    elev = elev * land
    sea = 1 - land

    # Lava: about half cooled dark crust, the rest glowing in a continuous range.
    sea_heat = smoothstep(0.22, 1.0, u) ** 1.6
    # Land: the same field, cooled to dim embers, with its hottest threads still glowing as
    # rivers and fissures; vents at the summits.
    land_heat = np.maximum.reduce([sea_heat * 0.14, smoothstep(0.955, 0.995, u) * 0.8, glow_vents * 0.95])
    heat = land * land_heat + sea * sea_heat
    heat_rgb = ramp(heat, [(0.0, (0, 0, 0)), (0.1, (0.30, 0.03, 0.0)), (0.28, (0.62, 0.08, 0.01)),
                           (0.5, (0.92, 0.25, 0.02)), (0.7, (1.0, 0.45, 0.05)), (0.86, (1.0, 0.66, 0.14)),
                           (1.0, (1.0, 0.86, 0.45))])
    emissive = heat_rgb * (0.25 + 0.75 * heat)[..., None] * smoothstep(0.0, 0.12, heat)[..., None]

    # Towns: faint warm lights on the land, visible on the night side.
    rng = np.random.default_rng(SEED + 11)
    lights = np.zeros(g.lat.shape, np.float32)
    towns = [(pp["lat"], pp["lon"], 1.0) for pp in PINS if pp["name"] in TOWN_LIGHTS]
    for s_ in SOLIDLANDS:
        if s_["kind"] in ("blob", "strip"):
            c = (s_["lat"], s_["lon"]) if s_["kind"] == "blob" else tuple((np.array(s_["a"]) + np.array(s_["b"])) / 2)
            for _ in range(3):
                towns.append((c[0] + rng.normal() * 3, c[1] + rng.normal() * 3, 0.45))
    for la, lo, w in towns:
        d = angular_distance(g, la, lo)
        lights = np.maximum(lights, np.exp(-(d / (0.9 * w + 0.4)) ** 2) * smoothstep(0.55, 0.85, (fine + 1) / 2 + 0.2 * w) * w)
    lights *= smoothstep(0.6, 0.9, land)
    emissive += lights[..., None] * np.array([1.0, 0.82, 0.55], np.float32) * 0.45

    # Albedo: crust and rock share the field's mottling, so lava and land read as one world.
    crust = ramp(u, [(0.0, (0.05, 0.03, 0.025)), (0.2, (0.12, 0.05, 0.03)), (0.35, (0.22, 0.07, 0.03))])
    t = np.clip(0.5 + 0.8 * detail, 0, 1)
    rock = ramp(t, [(0.0, (0.10, 0.09, 0.09)), (0.4, (0.20, 0.16, 0.13)), (0.7, (0.34, 0.20, 0.11)), (1.0, (0.28, 0.24, 0.20))])
    rock = rock * (0.75 + 0.5 * u)[..., None]
    ashy = np.clip(np.maximum(ash, smoothstep(0.7, 1.05, elev) * 0.6), 0, 1)[..., None]
    rock = rock * (1 - ashy) + np.array([0.42, 0.40, 0.37], np.float32) * ashy
    base = rock * land[..., None] + crust * sea[..., None]
    hot = smoothstep(0.1, 0.6, heat)[..., None]
    albedo = base * (1 - hot) + heat_rgb * 0.7 * hot

    # Relief: mountains and land texture, gentle ripples in the crust.
    ridges = ridged(n3, p * 14.0, octaves=6)
    mountainous = smoothstep(0.3, 0.9, elev)
    elev_full = elev + land * (0.06 * detail + 0.25 * mountainous * (ridges - 0.45))
    height = np.clip(elev_full, 0, 1.3) + sea * 0.015 * (1 - u)
    rough = land * (0.9 - 0.2 * ashy[..., 0]) + sea * (0.8 - 0.45 * smoothstep(0.3, 0.8, heat))

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

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
    dict(name="The Roaring Kettle", kind="cap", pole=1, edge=66, profile="plain", height=0.25),
    dict(name="The Well of Destiny", kind="cap", pole=-1, edge=-70, profile="plain", height=0.22),
    dict(name="The Well of Wisdom", kind="archipelago", lat=2, lon=128, spread=(9, 26), islands=46, height=0.18),
    dict(name="Ymir — the Mother of all Giants", kind="blob", lat=24, lon=9, r=8.5, profile="mountain", height=1.0),
    dict(name="Muspell — Mountain of the Fire Giants", kind="blob", lat=20, lon=-12, r=8.0, profile="mountain", height=0.8),
    dict(name="Thestal Halls of Heorot", kind="blob", lat=44, lon=-68, r=10, profile="plateau", height=0.35),
    dict(name="Vigrid, the Last Battlefield", kind="blob", lat=-27, lon=-108, r=11, profile="plain", height=0.15),
    dict(name="Kenaz", kind="blob", lat=12, lon=62, r=5.5, profile="mesa", height=0.45),
    dict(name="Sinmara — an upland of cinders", kind="blob", lat=-38, lon=38, r=9, profile="plateau", height=0.4),
    dict(name="Surtesy — a volcanic island", kind="blob", lat=-12, lon=-58, r=3.5, profile="cone", height=0.6),
    dict(name="Svalinn — the Great Shield", kind="blob", lat=30, lon=128, r=12, profile="shield", height=0.45),
    dict(name="Gungnir — a thin stretch of lava delta marshlands", kind="strip", a=(-42, -150), b=(-22, -126), r=2.6, profile="plain", height=0.06),
]

# The Vale of Cleaveland: a lava channel between Ymir and Muspell, where the capital rides the flow.
CLEAVELAND = dict(a=(34, -2.5), b=(8, -1.0), r=1.6)

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

    # Land surface detail: rough rock everywhere, ridges in the mountains.
    print(f"  features {time.time() - t0:.1f}s")
    ridges = ridged(n3, p * 14.0, octaves=5)
    mountainous = smoothstep(0.35, 0.9, elev)
    elev_full = elev + land * (0.05 * detail + 0.25 * mountainous * (ridges - 0.5))
    elev_full = np.clip(elev_full, 0, 1.2)
    ash = np.maximum(ash, smoothstep(0.75, 1.0, elev_full) * 0.6)

    # Lava ocean: domain-warped swirls, dark cooled crust rafting on bright molten lava.
    print(f"  land {time.time() - t0:.1f}s")
    warp = np.stack([fbm(n1, p * 3 + 11, 4), fbm(n2, p * 3 + 23, 4), fbm(n3, p * 3 + 37, 4)], -1)
    swirl = fbm(n2, p * 6 + warp * 1.6, octaves=6)
    q_open, q_edge = np.quantile(swirl, [0.06, 0.15])
    crust = smoothstep(q_open, q_edge, swirl)  # 1 = cooled crust; ~15% open molten lava
    cracks = ridged(n1, p * 18 + warp * 2.0, octaves=4)
    seam = smoothstep(0.76, 0.92, cracks)
    crust = crust * (1 - seam * 0.85)

    # Glowing seams on land: lava rivers in low ground and at the coast.
    rivers = smoothstep(0.90, 0.97, ridged(n3, p * 7 + warp * 0.8, octaves=3)) * smoothstep(0.45, 0.12, elev_full)
    shore = smoothstep(0.02, 0.5, land) * smoothstep(1.0, 0.6, land)

    sea = 1 - land
    print(f"  lava {time.time() - t0:.1f}s")

    # --- Albedo
    basalt = np.array([0.15, 0.13, 0.12], np.float32)
    cinder = np.array([0.30, 0.16, 0.10], np.float32)
    ashc = np.array([0.42, 0.40, 0.37], np.float32)
    molten = np.array([0.95, 0.38, 0.06], np.float32)
    crustc = np.array([0.045, 0.022, 0.018], np.float32)
    tint = np.clip(0.5 + 0.9 * detail, 0, 1)[..., None]
    land_c = basalt * (1 - tint * 0.7) + cinder * tint * 0.7
    weathered = np.clip(smoothstep(0.2, 0.9, elev_full) * 0.5 + 0.5 * mountainous * ridges, 0, 1)[..., None]
    land_c = land_c * (1 - weathered * 0.5) + np.array([0.30, 0.26, 0.23], np.float32) * weathered * 0.5
    land_c = land_c * (1 - ash[..., None]) + ashc * ash[..., None]
    land_c = land_c * (1 - rivers[..., None]) + molten * rivers[..., None]
    lava_c = molten * (1 - crust[..., None]) + crustc * crust[..., None]
    albedo = land_c * land[..., None] + lava_c * sea[..., None]

    # --- Emission (0..1, multiply by an intensity in the renderer)
    emit_sea = (1 - crust) * (0.45 + 0.55 * smoothstep(q_edge, q_open - 0.08, swirl))
    emit = sea * emit_sea + land * np.maximum(rivers, glow_vents * 0.9) + shore * 0.6
    heat = np.clip(emit, 0, 1)[..., None]
    red, orange, yellow = (np.array(c, np.float32) for c in ([0.55, 0.06, 0.02], [1.0, 0.36, 0.05], [1.0, 0.78, 0.35]))
    col = np.where(heat < 0.5, red + (orange - red) * (heat / 0.5), orange + (yellow - orange) * ((heat - 0.5) / 0.5))
    emissive = col * heat + sea[..., None] * crust[..., None] * np.array([0.05, 0.008, 0.0], np.float32)  # faint heat through the crust

    # --- Roughness and height
    rough = land * (0.88 - 0.25 * ash) + sea * (0.35 + 0.55 * crust)
    height = land * elev_full + sea * (crust * 0.015 - 0.01)

    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", albedo)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", np.clip(height, 0, 1))
    save_rgb(out / "normal.webp", normal_map(height * 0.06, strength=1.0))
    write_pins(out / "pins.json", "Magmus", PINS)
    print(f"  wrote {out} in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/magmus")
    a = ap.parse_args()
    generate(a.width, a.out)

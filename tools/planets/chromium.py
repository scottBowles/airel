"""Chromium ("the dark planet"): generate texture maps from the spec below.

    python3 tools/planets/chromium.py [--width 4096] [--out web/static/system/chromium]

Lore (see .ideas/projects/solar-system-3d/bodies/chromium.md and assets.md):
- "Planet of the Dragons. Unheard from, and anyone who goes there doesn't come back." Nobody has
  been there; it has no places in the DB, so no pins. The display reads "uncharted".
- The user's plan (assets.md): keep it mysterious. A near-black, low-reflectance world under dark
  storm cloud, a faint ember glow in fissures and the odd flash of lightning (the lightning is a
  shader on the cloud layer: `clouds.lightning` in bodies.ts).
- The Halls of the Pantheon are on Chromium (a vision, Iconic Conflicts, 2021-01-18). Nobody
  knows where; here they're one faint, cool point of light at (0, 0) that nothing explains. Easy
  to remove (HALLS).

Real analogue, and how it's translated:
- Surface: flood basalt and the lunar maria (albedo ~0.07, the darkest large surfaces we see from
  orbit), with fresh obsidian-black glassy flows (~0.03). Rough highlands a touch lighter and
  browner. The name's "chrome" nod is the glassy plains: smoother (a dull sheen at low sun) and the
  faintest blue-violet cast, too slight to read as a colour.
- Fissures: Iceland's and Ethiopia's (Afar) rifts and Io's paterae. From orbit a rift zone is a
  broad belt of parallel en-echelon cracks, not one line; at night only a few segments glow, dull
  red where lava is crusting, and a handful of vents (calderas) glow brighter. Here: five rift
  belts along great circles, each a few degrees wide, holding broken ember cracks, plus ~40 vents
  mostly in the belts. The glow is dim (embers, not Magmus), deep red to orange.
- Cloud: a thunderstorm world, nearer Venus's cover than Earth's: ~75% thick, dark-grey (the
  colour is set in the app), with storm systems and a thin veil over the gaps. Like Mystra the
  layer doesn't drift, so the ember glow can be mapped up into it (clouds-glow.webp) and shows
  as a dull red smear in the cloud over each rift at night.

Interpretations (all invented): rift positions, the vents, the highland share (~35%), no seas, no
polar caps (nothing says it's cold or wet).
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from clouds import make_clouds, rank
from mystra import blur
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
    segment_distance,
    smoothstep,
    unit,
    write_pins,
)

SEED = 1313
HIGHLAND = 0.35

# Rift belts: great-circle arcs (start, end) and half-width in degrees. All invented.
RIFTS = [
    ((38, -150), (-12, -95), 6.0),
    ((-48, -40), (6, 20), 7.0),
    ((52, 40), (14, 110), 5.5),
    ((-20, 120), (-62, 175), 5.0),
    ((24, -40), (58, -5), 4.0),
]
VENTS = 40
HALLS = (0.0, 0.0)  # the Halls of the Pantheon (a guess; see the docstring)

EMBER = np.array([1.0, 0.32, 0.08], np.float32)
HOT = np.array([1.0, 0.6, 0.25], np.float32)
PALE = np.array([0.85, 0.82, 0.7], np.float32)


def generate(width: int, out: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(SEED)
    n = [Noise3(SEED * 10 + i) for i in range(12)]
    p = g.xyz

    # --- Terrain: one warped field for highland and plain ---------------------------------
    warp = np.stack([fbm(n[0], p * 1.8 + 11, 5), fbm(n[1], p * 1.8 + 23, 5), fbm(n[2], p * 1.8 + 37, 5)], -1)
    broad = rank(fbm(n[3], p * 2.2 + warp * 1.2, 5))
    detail = fbm(n[4], p * 10 + warp * 2, 5)
    ridges = ridged(n[5], p * 6 + warp * 1.4, 5)
    high = smoothstep(1 - HIGHLAND - 0.12, 1 - HIGHLAND + 0.12, broad + 0.1 * detail)

    # Rift belts: distance to each arc, wobbled so the belts aren't ruled lines.
    wob = 1.5 * fbm(n[6], p * 6 + warp, 3)
    belt = np.zeros(g.lat.shape, np.float32)
    for a, b, w in RIFTS:
        d = segment_distance(g, a, b) + wob
        belt = np.maximum(belt, smoothstep(w, 0.3 * w, d))
    # Fresh flows spill out of the rifts across the plains: the youngest, glassiest, blackest rock.
    fresh = smoothstep(0.35, 0.75, rank(fbm(n[7], p * 4 + warp * 1.5, 5) + 0.9 * blur(belt, 2.0 * g.width / 360))) * (1 - 0.7 * high)
    print(f"terrain {time.time() - t0:.1f}s")

    # Cracks: en-echelon segments inside the belts. The crests of a stretched ridged field, broken
    # into dashes by a second field, so only some segments are open (and glowing) at once.
    crest = ridged(n[8], p * 30 + warp * 3, 3)
    crack = smoothstep(0.84, 0.93, crest) * belt
    dash = smoothstep(0.3, 0.55, rank(fbm(n[9], p * 18 + warp * 2, 3)))
    glow = crack * dash
    # A wider, dimmer skirt: warm ground around the open cracks (blurred by a coarser field).
    skirt = smoothstep(0.7, 0.93, crest) * belt * smoothstep(0.3, 0.7, rank(fbm(n[9], p * 18 + warp * 2, 3)))

    # Vents: calderas, most in the belts.
    lat = np.degrees(g.lat)
    lon = np.degrees(g.lon)
    weight = (0.04 + belt) * np.cos(g.lat)
    weight = weight.ravel().astype(np.float64)
    weight /= weight.sum()
    vents = np.zeros(g.lat.shape, np.float32)
    pit = np.zeros(g.lat.shape, np.float32)
    placed: list[np.ndarray] = []
    for idx in rng.choice(weight.size, size=2000, p=weight):
        if len(placed) >= VENTS:
            break
        la, lo = float(lat.flat[idx]), float(lon.flat[idx])
        c = unit(la, lo)
        if any(np.degrees(np.arccos(np.clip(c @ q, -1, 1))) < 4.0 for q in placed):
            continue
        placed.append(c)
        r = 0.12 * float(rng.lognormal(0, 0.4))
        rows = np.where(np.abs(lat[:, 0] - la) < 8 * r + 0.5)[0]
        sub = (slice(rows[0], rows[-1] + 1), slice(None))
        d = angular_distance(g, la, lo)[sub] / r
        b = float(rng.uniform(0.4, 1.0)) * (0.3 + 0.7 * float(belt.flat[idx]))
        vents[sub] = np.maximum(vents[sub], b * (smoothstep(1.0, 0.2, d) + 0.25 * smoothstep(4.0, 1.0, d)))
        pit[sub] = np.maximum(pit[sub], smoothstep(2.5, 0.8, d))
    print(f"fissures {time.time() - t0:.1f}s, {len(placed)} vents")

    # --- Colour ---------------------------------------------------------------------------
    mott = fbm(n[10], p * 60 + warp * 3, 3)
    base = ramp(
        np.clip(0.6 * high + 0.25 * rank(detail) + 0.15 * ridges * high, 0, 1),
        [
            (0.0, (0.035, 0.036, 0.042)),  # basalt plain
            (0.5, (0.05, 0.048, 0.05)),
            (0.8, (0.07, 0.064, 0.06)),  # rough highland
            (1.0, (0.085, 0.077, 0.07)),
        ],
    )
    base = base * (0.88 + 0.2 * mott[..., None])
    glass = np.array([0.024, 0.025, 0.034], np.float32)  # obsidian, the faintest violet-blue
    rgb = base * (1 - 0.75 * fresh[..., None]) + glass * 0.75 * fresh[..., None]
    # Inside the belts: slightly lighter, ashy ground, darker crack lines, scorched skirts.
    rgb = rgb * (1 + 0.25 * belt[..., None] * (1 - fresh[..., None])) * (1 - 0.5 * crack[..., None])
    rgb = rgb * (1 - 0.5 * pit[..., None])
    print(f"colour {time.time() - t0:.1f}s")

    # --- Lights: embers ------------------------------------------------------------------
    heat = np.clip(0.8 * glow + 0.12 * skirt + vents, 0, 1.2)
    hue = smoothstep(0.5, 1.0, heat)[..., None]
    emissive = (EMBER * (1 - hue) + HOT * hue) * heat[..., None] * 0.7
    halls = angular_distance(g, *HALLS)
    emissive = emissive + PALE * 0.35 * smoothstep(0.12, 0.0, halls)[..., None]
    print(f"lights {time.time() - t0:.1f}s, cracks lit {float((glow > 0.3).mean()):.4f}")

    # Glassy flows smooth (a dull sheen), highlands and ash rough.
    rough = np.clip(0.88 - 0.4 * fresh + 0.05 * high, 0, 1)
    height = np.clip(0.45 * broad + 0.2 * high + 0.1 * ridges * high + 0.04 * detail - 0.08 * belt - 0.03 * pit, 0, 1)
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.02, strength=1.0))
    print(f"maps {time.time() - t0:.1f}s, highland {float((high > 0.5).mean()):.3f}, belts {float((belt > 0.5).mean()):.3f}")

    clouds, thickness = storm_deck(g)
    save_gray(out / "clouds.webp", clouds)
    # Smoothed first: the raw thickness crazed into fine veins in grazing light at the terminator.
    save_rgb(out / "clouds-normal.webp", normal_map(blur(thickness, 0.15 * g.width / 360) * 0.006, strength=1.0))
    print(f"  clouds: alpha>0.5 {float((clouds > 0.5).mean()):.3f}, alpha<0.2 {float((clouds < 0.2).mean()):.3f}")
    save_ember_glow(out, emissive)
    write_pins(out / "pins.json", "Chromium", [])
    print(f"done {time.time() - t0:.1f}s -> {out}")


def save_ember_glow(out: Path, emissive: np.ndarray) -> None:
    """clouds-glow.webp: the embers as the storm deck above them shows them. Wider than Mystra's
    halos (~1° and ~2.5°), so each rift belt shows as one continuous dull band, not beads."""
    h, w = emissive.shape[:2]
    small = emissive[: h - h % 4, : w - w % 4].reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3))
    px = (w // 4) / 360
    glow = np.stack([0.5 * blur(small[..., c], 1.0 * px) + 0.5 * blur(small[..., c], 2.5 * px) for c in range(3)], -1)
    peak = float(np.percentile(glow.max(-1), 99.9))
    save_rgb(out / "clouds-glow.webp", np.clip(glow / max(peak, 1e-6), 0, 1) ** 0.8)


def storm_deck(g):
    """Thick storm cloud over ~3/4 of the planet: big comma systems at mid-latitudes, a few
    tighter cells low, a thin veil over the gaps."""
    storms = [
        dict(lat=42, lon=-120, ax=28, ay=18, swirl=1.6, inflow=0.7, face=0.6, front=(15, -150)),
        dict(lat=-38, lon=10, ax=30, ay=18, swirl=-1.7, inflow=0.7, face=-0.8, front=(-12, 40)),
        dict(lat=50, lon=80, ax=22, ay=15, swirl=1.4, inflow=0.8, face=1.2),
        dict(lat=-45, lon=150, ax=24, ay=16, swirl=-1.5, inflow=0.7),
        dict(lat=12, lon=-30, ax=7, ay=7, swirl=2.4, inflow=1.3, eye=0.6, strength=3.0, round=True),
    ]
    return make_clouds(g, SEED, cover=0.62, storms=storms, veil=(0.35, 0.55), zoning=0.15)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system/chromium")
    generate(**vars(ap.parse_args()))

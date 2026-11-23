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

from clouds import billow, make_clouds, rank
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


def volcanic_sites(g, e, sun, count=5):
    """Centres (lat, lon, radius°) of the day side's volcanic provinces: the highest broad ground,
    spread apart, away from the terminator and the scorched centre."""
    h, w = e.shape
    k = h // 32
    coarse = e[: h // k * k, : w // k * k].reshape(h // k, k, w // k, k).mean(axis=(1, 3))
    s = sun[k // 2 :: k, k // 2 :: k][: coarse.shape[0], : coarse.shape[1]]
    lat = np.degrees(g.lat[k // 2 :: k, 0])[: coarse.shape[0]]
    lon = np.degrees(g.lon[0, k // 2 :: k])[: coarse.shape[1]]
    score = np.where((s > 18) & (s < 66), coarse, -1)
    picked = []
    for i in np.argsort(score, axis=None)[::-1]:
        r, c = np.unravel_index(i, score.shape)
        if score[r, c] < 0 or len(picked) == count:
            break
        u = np.array([np.cos(np.radians(lat[r])) * np.cos(np.radians(lon[c])), np.cos(np.radians(lat[r])) * np.sin(np.radians(lon[c])), np.sin(np.radians(lat[r]))])
        if all(np.degrees(np.arccos(np.clip(u @ q, -1, 1))) > 32 for _, q in picked):
            picked.append(((float(lat[r]), float(lon[c])), u))
    sizes = [9, 8, 8, 7, 7]
    return [(la, lo, sizes[i]) for i, ((la, lo), _) in enumerate(picked)]


def geyser_fields(g):
    """Where the geyser fields are on the dark side, 0..1 (also where its steam fog sits)."""
    n = [Noise3(SEED * 10 + i) for i in range(3)]
    p = g.xyz
    warp = np.stack([fbm(n[0], p * 1.6 + 11, 5), fbm(n[1], p * 1.6 + 23, 5), fbm(n[2], p * 1.6 + 37, 5)], -1)
    return smoothstep(0.82, 0.93, rank(fbm(n[2], p * 6 + warp * 1.5 + 9, 5)))


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
    # Hot deserts from orbit are light tan to ochre (the Sahara, Arabia, the Lut), with dark
    # patches only where there are volcanic fields or old varnished plateaus, and white salt flats.
    # The base is paler than it looks lit: the Red Sun pushes everything toward orange.
    desert = ramp(
        rank(fbm(n[6], p * 4 + warp * 1.4, 6)) * 0.55 + 0.45 * e,
        [
            (0.0, (0.78, 0.68, 0.53)),
            (0.35, (0.72, 0.6, 0.44)),  # tan plains
            (0.7, (0.64, 0.5, 0.35)),  # ochre
            (1.0, (0.5, 0.39, 0.29)),  # upland rock
        ],
    )
    desert = desert * (0.9 + 0.2 * fine[..., None])
    # Volcanic provinces: a few big lava fields on high ground, like the Sahara's Tibesti and
    # Haruj. Each is a dark core with lobed flows reaching outward and a scatter of cones.
    volc = np.zeros(g.lat.shape, np.float32)
    lava_gap = np.full(g.lat.shape, 99.0, np.float32)  # degrees beyond the nearest province's rim
    for k, (la, lo, r) in enumerate(volcanic_sites(g, e, sun)):
        c = unit(la, lo)
        east = np.cross([0, 0, 1], c)
        east /= np.linalg.norm(east)
        north = np.cross(c, east)
        d = angular_distance(g, la, lo)
        lava_gap = np.minimum(lava_gap, d - r)
        near = d < 1.6 * r
        a = np.arctan2(p[near] @ north, p[near] @ east)
        ring = np.stack([np.cos(a) * 0.9, np.sin(a) * 0.9, np.full_like(a, k * 3.7)], -1)
        edge = r * (0.6 + 0.4 * np.clip(0.5 + 1.4 * fbm(n[7], ring, 2), 0, 1))
        dd = d[near] + 0.8 * fbm(n[5], p[near] * 25, 4)
        lava = smoothstep(edge, edge * 0.9, dd)
        # Flows of different ages: patches of lighter and darker lava, darker toward the core.
        flows = smoothstep(-0.25, 0.25, fbm(n[6], p[near] * 18, 3))
        volc[near] = np.maximum(volc[near], lava * (0.75 + 0.25 * flows) * (0.8 + 0.2 * smoothstep(r, 0, dd)))
        for _ in range(int(r * 1.5)):
            ca, cb = rng.normal(0, 0.35 * r, 2)
            cone = angular_distance(g, la + ca, lo + cb / np.cos(np.radians(la)))
            m = cone < 0.6
            volc[m] = np.maximum(volc[m], smoothstep(0.5, 0.15, cone[m]))
    desert = desert * (1 - 0.8 * volc[..., None]) + np.array([0.14, 0.12, 0.11], np.float32) * 0.8 * volc[..., None]
    # Salt flats: blinding white pans in the low basins, sharp-edged.
    # Dry lake beds in the lowest basins, drawn out long (a stretched field), each ringed by a pale
    # clay halo that fades into the tan. Never on the lava.
    basin = e + 0.05 * fbm(n[3], p * np.array([2.0, 2.0, 7.0], np.float32) * 3 + warp, 4)
    clear = smoothstep(0.0, 6.0, lava_gap)  # salt flats keep well away from the lava
    playa = smoothstep(0.06, 0.04, basin) * smoothstep(8, 20, sun) * clear
    clay = smoothstep(0.11, 0.06, basin) * smoothstep(8, 20, sun) * clear
    desert = desert * (1 - 0.45 * clay[..., None]) + np.array([0.84, 0.77, 0.64], np.float32) * 0.45 * clay[..., None]
    desert = desert * (1 - playa[..., None]) + np.array([0.9, 0.88, 0.84], np.float32) * (0.92 + 0.1 * grain[..., None]) * playa[..., None]
    # Every surface wind on a locked world runs toward the sub-solar point, so everything wind-made
    # radiates from it: yardangs (long ridges carved from the rock) in the hot centre, dune seas
    # in a ring farther out.
    ang = np.arctan2(p[..., 2], p[..., 1])
    ang_w = ang + 0.05 * fbm(n[7], p * 9 + warp, 4)
    # Thin, nearly straight ridges a few texels apart: finer or wigglier and they shimmer as moiré.
    yard = smoothstep(0.7, 1.0, 0.5 + 0.5 * np.sin(ang_w * 700 + 0.6 * fbm(n[2], p * 8, 3)))
    carved = smoothstep(40, 58, sun) * smoothstep(0.3, 0.55, rank(fbm(n[3], p * 5 + warp + 7, 4))) * (1 - clay) * (1 - volc)
    desert = desert * (1 - 0.14 * carved[..., None] * yard[..., None])
    dunes = 0.5 + 0.5 * np.sin(ang_w * 520 + 2.0 * fbm(n[2], p * 30, 3))
    erg = smoothstep(0.5, 0.7, rank(fbm(n[1], p * 3 + warp * 1.2 + 5, 5))) * smoothstep(0.6, 0.35, e)
    erg = erg * smoothstep(52, 38, sun) * smoothstep(6, 16, sun) * (1 - playa)
    sand = np.array([0.8, 0.62, 0.42], np.float32)
    desert = desert * (1 - 0.85 * erg[..., None]) + sand * (0.8 + 0.3 * dunes[..., None]) * 0.85 * erg[..., None]
    # Right under the sun: a smaller, softer scorched plain (fiction: nothing on Earth is hot
    # enough to darken ground like this, but it marks the hottest point at a glance).
    scorch = smoothstep(74, 86, sun + 4 * fbm(n[3], p * 8, 4))
    desert = desert * (1 - 0.5 * scorch[..., None]) + np.array([0.22, 0.16, 0.13], np.float32) * 0.5 * scorch[..., None]
    # Dry riverbeds cut long ago, faint.
    wadis = veins(n[4], p * 10 + warp * 2, 0.05) * smoothstep(0.55, 0.75, rank(fbm(n[5], p * 3 + 2.2, 4)))
    desert = desert * (1 - 0.15 * wadis[..., None])

    # --- The dark side: dark rock, pale crust around the geyser fields, no ice. --------------
    rock = ramp(e, [(0.0, (0.2, 0.19, 0.18)), (0.5, (0.15, 0.14, 0.14)), (1.0, (0.11, 0.1, 0.11))])
    fields = geyser_fields(g)
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
    lat = np.degrees(g.lat)
    glint = np.random.default_rng(SEED + 1).random(g.lat.shape).astype(np.float32)

    def town(la, lo, r, b):
        """A small town seen at night from orbit: a solid bright centre, street lights thinning out
        toward its edge, and a road or two leading away as a dotted line."""
        rows = np.where(np.abs(lat[:, 0] - la) < 3.6 * r)[0]
        sub = (slice(rows[0], rows[-1] + 1), slice(None))
        d = angular_distance(g, la, lo)[sub]
        t = d / r
        c = unit(la, lo)
        east = np.cross([0, 0, 1], c)
        east /= np.linalg.norm(east)
        north = np.cross(c, east)
        a = np.arctan2(p[sub] @ north, p[sub] @ east)
        core = smoothstep(0.45, 0.1, t)
        streets = (glint[sub] > 0.3 + 0.5 * t) * smoothstep(1.4, 0.3, t)
        roads = np.zeros_like(d)
        for bearing in rng.uniform(0, 2 * np.pi, int(rng.integers(1, 4))):
            perp = np.abs(d * np.sin(a - bearing))
            along = d * np.cos(a - bearing)
            roads = np.maximum(roads, smoothstep(0.05, 0.015, perp) * (along > 0) * smoothstep(3.5 * r, 1.2 * r, d) * (glint[sub] > 0.45))
        lights[sub] += b * (0.7 * core + 0.5 * streets + 0.3 * roads)

    # The habitable band: a chain of small towns, oases with empty rock land between, all the
    # way round, a little way into the dark; a faint scatter of homesteads and camps.
    for _ in range(46):
        la = float(np.degrees(np.arcsin(rng.uniform(-0.94, 0.94))))
        el = -rng.uniform(0.5, 9)  # solar elevation: how far into the dark
        side = rng.choice([-1, 1])
        cl = np.sin(np.radians(el)) / np.cos(np.radians(la))
        lo = side * float(np.degrees(np.arccos(np.clip(cl, -1, 1))))
        town(la, lo, rng.uniform(0.3, 0.8), rng.uniform(0.6, 1.0))
    settled = smoothstep(-12, -1.5, sun_w + 3 * fine) * smoothstep(3, 0, sun_w)
    lights += 0.3 * settled * smoothstep(0.96, 0.995, rank(fbm(n[6], p * 400 + 7.7, 2)))  # homesteads
    for la, lo, s in [(HOUSE[0], HOUSE[1], 0.8), *DARK_TOWNS]:
        town(la, lo, 0.9 * s + 0.2, 0.6 + 0.5 * s)
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
    height = np.clip(e + 0.12 * volc * day + 0.08 * mesas - 0.04 * channels * band - 0.03 * wadis * day, 0, 1)
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
    """A locked world's night side is mostly clear: its air cools and sinks, and flows along the
    ground toward the day side. Cloud comes from the geysers: steam meeting cold air makes fog
    banks and plumes over the geyser fields. A thin haze elsewhere, and a broken line of storms
    along the Mezzolux, where the cold air meets the hot (the logs' flash floods and lightning).
    The day side is dry and clear."""
    n = [Noise3(SEED * 13 + i) for i in range(4)]
    p = g.xyz
    sun = np.degrees(np.arcsin(np.clip(p[..., 0], -1, 1)))
    night = smoothstep(2, -4, sun)
    texture, thick = make_clouds(g, SEED, cover=0.5, storms=[], veil=(0.0, 0.0), zoning=0.0)
    puffs = billow(n[0], p * 30 + fbm(n[1], p * 6, 3)[..., None], 4)
    # Fog over the geyser fields, spreading a little past them.
    fields = geyser_fields(g)
    near = smoothstep(0.0, 0.6, fields + 0.5 * fbm(n[2], p * 8, 3))
    fog = near * (0.45 + 0.5 * puffs) * night
    # Storms strung along the terminator, just on the dark side.
    line = smoothstep(-9, -3, sun) * smoothstep(1, -1.5, sun) * smoothstep(0.45, 0.7, rank(fbm(n[3], p * 4, 4)))
    storms = line * texture
    haze = 0.05 * night * (0.5 + puffs)
    alpha = np.clip(np.maximum.reduce([fog, storms, haze]), 0, 1)
    return alpha.astype(np.float32), (thick * np.maximum(near, line) * night + 0.5 * fog).astype(np.float32)


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

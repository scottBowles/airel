"""Didymus, the twin planets: generate texture maps and pins for both twins.

    python3 tools/planets/didymus.py [didymus-prime didymus] [--width N] [--out web/static/system]

Writes web/static/system/didymus-prime/ (the larger twin, every DB place) and
web/static/system/didymus/ (the smaller twin, no DB places). Default widths: Prime 4096,
Didymus 2048 (see WIDTHS).

Lore (see .ideas/projects/solar-system-3d/bodies/didymus.md, and the DM's answers at the top of
bodies/QUESTIONS.md, which override the brief):
- One small planet, broken in two long ago (the Solar Cannon's test shot, Iconic Conflicts);
  the halves revolve around each other as one system. Each twin is smaller than half a typical
  planet (DM). Prime is the larger and kidney-bean shaped, the other smaller and rounder (DM).
- The break was long ago: at most a small, weathered remnant shows (DM). So no glassed fracture
  face (the brief's proposal). Interpretation: the bean's indent IS the old break face, worn
  down over ages into a broad, shallow, dust-floored lowland (like Mars's Hellas basin: an
  ancient scar that now reads as a bright dusty plain). The remnant is one small, eroded
  crescent of dark knobby rock (old melt) on the basin floor, half buried in dust. The smaller
  twin has the same, smaller and rounder. Both break faces sit at (0, 180), facing each other
  (the pair is taken to be mutually tidally locked).
- "Since the cataclysm ... the place is burned pretty deep" (Didymus Prime log): broad
  charred, dark grey-brown ground, thickest around the old break and fading outward, mottled
  and streaked by drifting dust (like Mars's dark albedo regions, e.g. Syrtis Major).
- "Lots of sand ... very few living waters, so life is gathered around them" (DB notes);
  "dustbowl"; "how do you get water out of a rock?". Rust and red sand and stony plains (the
  Simpson Desert's red dunes, the Pilbara's old iron-red ranges, Mars's butterscotch dust),
  not Janus's pale tan Sahara. No salt or claypans (Janus's signature; tried, they read as
  ragged pale decals). Old weathered craters with Mars-style wind streaks: the thin, dusty
  air keeps them, and every streak points downwind.
- Living waters: Prime 4 (Goshen's the largest), the other twin 2 (brief: 4 / 2-3). Each is a
  tiny dark lake with a dark olive fringe. Positions besides Goshen's are guesses.
- Whidmore "is still buying up land ... to terraform and turn it into agriculture": a small
  cluster of centre-pivot fields near Goshen (brief: farm patches near 30, 70), like the pivot
  farms of Saudi Arabia's Wadi As-Sirhan. Invented look; the lore only says agriculture.
- Lights: Goshen, "the biggest city on the planet", the one real cluster; Ashtown a dim speck
  (a ghost town); faint scattered specks (trailer towns, warehouses, call centres, nomad
  camps). The other twin barely inhabited (DM default): a few faint specks at its waters.
- No clouds: thin dusty air. Haze is a render setting (see the hand-off report).

Shape: the app deforms the sphere into a bean (integration work). Taken here: long axis
through the poles (about 1.45 : 1), indent centred on (0, 180). So nothing important sits
poleward of about 55° or right in the indent's middle.
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
    unit,
    write_pins,
)

BREAK = (0.0, 180.0)  # centre of each twin's old break face, facing the other twin

GOSHEN = (24.0, 52.0)  # brief: guess, at the largest living water
ASHTOWN = (14.0, 118.0)  # brief: guess, toward the old break, in burned ground

PRIME_PINS = [
    dict(name="Goshen", lat=GOSHEN[0], lon=GOSHEN[1], confidence="guess"),
    dict(name="The Labyrinth", lat=23.6, lon=53.6, confidence="guess"),  # One Horn Riders' compound, Goshen's edge
    dict(name="Ashtown", lat=ASHTOWN[0], lon=ASHTOWN[1], confidence="guess"),
    dict(name="Copper Kettle", lat=14.0, lon=118.0, confidence="layout"),
    dict(name="Daedalus Headquarters", lat=14.05, lon=118.15, confidence="layout"),
    dict(name="Ashtown Bomb Shelter", lat=13.95, lon=118.0, confidence="layout"),
]

TWINS: dict[str, dict] = {
    "didymus-prime": dict(
        name="Didymus Prime",
        seed=707,
        break_r=36,  # the worn break basin's radius, degrees
        remnant=dict(lat=7, lon=171, ax=2.2, ay=6.0, tilt=25),  # small eroded crescent of old melt
        burned=0.24,  # share of the surface that is charred dark ground
        sand=0.20,  # share in red sand seas
        ranges=0.22,  # share in old eroded ranges
        craters=46,
        small_craters=500,
        char=[(0, (0.22, 0.18, 0.16)), (0.5, (0.28, 0.22, 0.19)), (1, (0.35, 0.27, 0.22))],
        # Living waters: (lat, lon, radius°). Goshen's is the largest (brief); others invented.
        waters=[(GOSHEN[0] - 0.5, GOSHEN[1] - 0.9, 0.75), (-9, 14, 0.4), (36, -38, 0.45), (-27, -86, 0.35)],
        farms=dict(lat=29.5, lon=66, n=34, spread=(2.6, 5.5)),
        # (lat, lon, radius°, brightness, roads). Goshen: the one real cluster, with its edge
        # settlements (the One Horn Riders' compound, construction sites, warehouses) around it.
        # Ashtown: a dim speck, a near ghost town.
        towns=[
            (GOSHEN[0], GOSHEN[1], 0.95, 1.0, 3),
            (23.6, 53.6, 0.22, 0.45, 1),
            (25.2, 50.3, 0.18, 0.35, 0),
            (22.4, 50.9, 0.15, 0.3, 0),
            (26.0, 54.4, 0.14, 0.25, 0),
            (ASHTOWN[0], ASHTOWN[1], 0.16, 0.32, 1),
        ],
        # Faint settlements: a few at the waters, the rest scattered (trailers, warehouses, camps).
        specks=16,
        pins=PRIME_PINS,
    ),
    "didymus": dict(
        name="Didymus",
        seed=708,
        break_r=28,
        remnant=dict(lat=-5, lon=-174, ax=1.8, ay=4.5, tilt=-35),
        burned=0.55,  # the smaller twin: darker, more charred, rockier, more craters
        sand=0.08,
        ranges=0.26,
        craters=78,
        small_craters=420,
        # Greyer, cooler char than Prime's: bare basalt-like ground the dust has blown off.
        char=[(0, (0.19, 0.17, 0.16)), (0.5, (0.25, 0.21, 0.19)), (1, (0.32, 0.26, 0.22))],
        waters=[(-14, 38, 0.4), (21, -61, 0.3)],
        farms=None,
        towns=[],
        specks=4,
        pins=[],
    ),
}
WIDTHS = {"didymus-prime": 4096, "didymus": 2048}

WARM = np.array([1.0, 0.7, 0.4], np.float32)


def rank(x: np.ndarray) -> np.ndarray:
    """Rank-normalise to 0..1, so thresholds mean area fractions at any resolution."""
    u = np.empty(x.size, np.float32)
    u[np.argsort(x, axis=None)] = np.linspace(0, 1, x.size, dtype=np.float32)
    return u.reshape(x.shape)


def frame(lat, lon):
    c = unit(lat, lon)
    east = np.cross([0, 0, 1], c)
    east /= np.linalg.norm(east)
    return c, east, np.cross(c, east)


def rows_near(g, lat, reach):
    lat_deg = np.degrees(g.lat[:, 0])
    rows = np.where(np.abs(lat_deg - lat) < reach)[0]
    return slice(rows[0], rows[-1] + 1)


def wind_bearing(lat):
    """Prevailing surface wind's heading (radians, 0 = east, π/2 = north) by latitude: easterlies
    in the tropics blow west, westerlies at mid latitudes blow east, with a poleward lean."""
    t = smoothstep(22, 34, abs(lat))
    west = np.pi + np.sign(lat) * -0.25  # toward the west, leaning equatorward
    east = 0.0 + np.sign(lat) * 0.3
    return float(west * (1 - t) + east * t)


def generate(slug: str, m: dict, width: int, out_root: Path) -> None:
    t0 = time.time()
    g = make_grid(width)
    rng = np.random.default_rng(m["seed"])
    n = [Noise3(m["seed"] * 10 + i) for i in range(10)]
    p = g.xyz
    lat = np.degrees(g.lat)

    # --- One warped field: relief, and from it everything else. ---------------------------
    warp = np.stack([fbm(n[0], p * 1.5 + 11, 5), fbm(n[1], p * 1.5 + 23, 5), fbm(n[2], p * 1.5 + 37, 5)], -1)
    base = rank(fbm(n[3], p * 2.4 + warp * 1.2, 8))
    # Old ranges (the Pilbara's worn, folded iron ranges): provinces of the high ground.
    province = rank(fbm(n[4], p * 1.8 + warp * 0.8 + 3, 5) + 0.6 * (base - 0.5))
    rmask = smoothstep(1 - m["ranges"] - 0.06, 1 - m["ranges"] + 0.08, province)
    ridges = ridged(n[5], p * 6 + warp * 0.8, 6)  # lightly warped: more bends and it swirls like a fingerprint
    h = 0.78 * base + 0.3 * rmask * (ridges - 0.35)

    # The worn break: a broad, shallow, smooth-floored basin facing the other twin, its rim
    # ragged (driven by the same warp) so it isn't a drawn circle.
    d_break = angular_distance(g, *BREAK) + 9 * fbm(n[6], p * 2.2 + warp, 5)
    R = m["break_r"]
    bowl = smoothstep(R * 1.15, R * 0.35, d_break)
    floor = smoothstep(R * 0.8, R * 0.2, d_break)
    h = h * (1 - 0.5 * floor) + 0.2 * (1 - 0.5 * floor) - 0.3 * bowl

    # The remnant: one small eroded crescent of dark knobby rock (old melt), off-centre.
    rm = m["remnant"]
    c, east, north = frame(rm["lat"], rm["lon"])
    x = np.degrees(np.arcsin(np.clip(p @ east, -1, 1)))
    y = np.degrees(np.arcsin(np.clip(p @ north, -1, 1)))
    tl = np.radians(rm["tilt"])
    xr, yr = x * np.cos(tl) + y * np.sin(tl), -x * np.sin(tl) + y * np.cos(tl)
    bend = 0.06 * yr**2  # a crescent, bowed away from the basin's centre
    ell = np.sqrt(((xr - bend) / rm["ax"]) ** 2 + (yr / rm["ay"]) ** 2) * ((p @ c) > 0)
    ell = np.where((p @ c) > 0, ell, 9)
    knobs = ridged(n[7], p * 40 + warp, 4)
    remnant = smoothstep(1.15, 0.45, ell + 0.35 * fbm(n[8], p * 18, 4)) * (0.35 + 0.65 * smoothstep(0.35, 0.7, knobs))
    h = h + 0.12 * remnant

    # Craters: old and weathered (soft rims, shallow), a power law of sizes.
    z = rng.uniform(np.sin(np.radians(-62)), np.sin(np.radians(62)), m["craters"])
    clat = np.degrees(np.arcsin(z))
    clon = rng.uniform(-180, 180, m["craters"])
    crad = 0.35 + 4.5 * rng.uniform(0, 1, m["craters"]) ** 3
    crat = np.zeros(g.lat.shape, np.float32)
    rimc = np.zeros(g.lat.shape, np.float32)
    streak = np.zeros(g.lat.shape, np.float32)  # downwind tails
    for la, lo, r in zip(clat, clon, crad):
        reach = r * 9 + 1
        sub = rows_near(g, la, reach)
        cc, ce, cn = frame(la, lo)
        ps = p[sub]
        d = np.degrees(np.arccos(np.clip(ps @ cc, -1, 1)))
        t = d / r
        wob = 1 + 0.12 * fbm(n[9], ps * (40 / max(r, 0.6)) + la, 3)
        tw = t * wob
        crat[sub] += (-(1 - np.minimum(tw, 1) ** 2) * (tw < 1) * 0.6 + 0.25 * np.exp(-(((tw - 1) / 0.25) ** 2))) * (0.05 + 0.01 * r)
        rimc[sub] = np.maximum(rimc[sub], np.exp(-(((tw - 1) / 0.22) ** 2)))
        # Wind streak: a tapering tail downwind, as long as several crater widths.
        b = wind_bearing(la) + 0.25 * rng.normal()
        lx = np.degrees(np.arcsin(np.clip(ps @ ce, -1, 1)))
        ly = np.degrees(np.arcsin(np.clip(ps @ cn, -1, 1)))
        along = lx * np.cos(b) + ly * np.sin(b)
        perp = -lx * np.sin(b) + ly * np.cos(b)
        length = min(r * rng.uniform(3, 7), 12.0)
        widen = r * (0.8 + 0.5 * np.clip(along / length, 0, 1))
        tail = smoothstep(-0.2 * r, 0.6 * r, along) * smoothstep(length, 0.3 * length, along)
        tail = tail * np.exp(-((perp / widen) ** 2)) * ((ps @ cc) > 0)
        streak[sub] = np.maximum(streak[sub], tail * (0.6 + 0.4 * rng.uniform()))
    # Many small craters (no tails worth drawing): the fine pitting that keeps a close view
    # crisp, more of them on the older, barer ground.
    k = m["small_craters"]
    z = rng.uniform(np.sin(np.radians(-75)), np.sin(np.radians(75)), k)
    for la, lo, r in zip(np.degrees(np.arcsin(z)), rng.uniform(-180, 180, k), 0.1 + 0.3 * rng.uniform(0, 1, k) ** 2):
        sub = rows_near(g, la, r * 2 + 0.2)
        t = np.degrees(np.arccos(np.clip(p[sub] @ unit(la, lo), -1, 1))) / r
        near = t < 2
        tn = t[near]
        crat[sub][near] += (-(1 - np.minimum(tn, 1) ** 2) * (tn < 1) * 0.6 + 0.25 * np.exp(-(((tn - 1) / 0.25) ** 2))) * 0.05
        rimc[sub][near] = np.maximum(rimc[sub][near], 0.7 * np.exp(-(((tn - 1) / 0.25) ** 2)))
    h = h + crat
    e = rank(h)
    print(f"  {slug}: relief {time.time() - t0:.1f}s")

    # --- Ground cover, all from the same fields. -------------------------------------------
    fine = fbm(n[8], p * 40 + warp, 4)
    grain = fbm(n[9], p * 150, 2)
    # Gibber and rubble: fine mottling a few texels across (no finer, or it's TV static).
    # Rubbly in some places, smooth dust in others, so it never reads as an even film grain.
    rubble = smoothstep(-0.2, 0.4, fbm(n[1], p * 7 + warp, 3))
    gibber = (fbm(n[0], p * (width / 9.0) + warp, 2) + 0.6 * fbm(n[1], p * (width / 20.0), 2)) * (0.3 + 0.7 * rubble)
    # Wind-drawn texture: noise squashed north-south, so its streaks lie east-west.
    pw = p * np.array([1.0, 1.0, 2.0], np.float32)  # 3x read as brushed paint on the char
    drift = fbm(n[6], pw * 12 + warp * 2, 4)

    # Charred ground: dark where the burn reached deepest, thickest toward the old break and
    # fading outward; soft-edged and streaked by drifting dust, as Mars's dark regions are.
    # Leaning toward the break side, broadly; the worn basin's floor a little less, since dust
    # has since filled it (as on Mars). Gentle weights, so neither reads as a ring or a target.
    near_break = smoothstep(R + 70, R * 0.5, d_break)
    edge = 0.25 * fbm(n[8], p * 11 + warp * 2, 5)  # detail at every scale along the boundary
    burn_f = rank(fbm(n[7], p * 2.0 + warp * 1.5 + 5, 7) + 0.4 * near_break - 0.3 * floor + 0.1 * drift + edge)
    thr = 1 - m["burned"]
    # Wide, graded edges, and darker the deeper into the burn: no flat two-tone print.
    burned = smoothstep(thr - 0.22, thr + 0.16, burn_f) * (0.6 + 0.4 * smoothstep(thr, 1.0, burn_f))
    burned = burned * (0.85 + 0.15 * smoothstep(-0.3, 0.3, drift))  # dust drifts over it in streaks
    # Around the living waters the ground has had water and life since; clear of char.
    for la, lo, r in m["waters"]:
        burned = burned * smoothstep(3 + 3 * r, 7 + 8 * r, angular_distance(g, la, lo) + 2.5 * fine)
    if m["farms"]:  # Whidmore farms where the ground isn't charred
        f = m["farms"]
        burned = burned * smoothstep(4, 9, angular_distance(g, f["lat"], f["lon"]) + 2.5 * fine)

    # Red sand seas: in the low ground, downwind (the drift field), never on the ranges.
    sand_f = rank(fbm(n[1], pw * 2.2 + warp * 1.3 + 9, 6) - 0.9 * e - 0.6 * rmask + 0.2 * fbm(n[2], pw * 14 + warp, 4))
    sand = smoothstep(1 - m["sand"] - 0.14, 1 - m["sand"] + 0.12, sand_f) * (1 - 0.8 * burned)
    sand = sand * (0.7 + 0.3 * smoothstep(-0.4, 0.4, drift))  # thinning in streaks, not a flat fill

    # No claypans or salt: drawn small they came out as ragged pale decals, and white pans
    # are Janus's signature. The low ground is dust and red sand instead.

    # Base: stony rust plains, darker and browner up on the high ground (gibber and rock).
    tone = rank(fbm(n[2], p * 4 + warp * 1.4, 6)) * 0.5 + 0.5 * e
    rgb = ramp(
        tone,
        [
            (0.0, (0.66, 0.46, 0.33)),  # dusty lowland
            (0.4, (0.60, 0.40, 0.28)),  # rust plains (Mars's bright regions, butterscotch)
            (0.75, (0.50, 0.33, 0.23)),  # stony upland
            (1.0, (0.41, 0.27, 0.20)),  # old rock
        ],
    )
    rgb = rgb * (0.92 + 0.16 * fine[..., None])
    # The ranges: dark iron-red rock, crests catching light, gullies shaded.
    rock = np.array([0.42, 0.26, 0.18], np.float32) * (0.75 + 0.55 * ridges[..., None])
    rgb = rgb * (1 - 0.7 * rmask[..., None]) + rock * 0.7 * rmask[..., None]
    # The basin floor: pale fine dust (Hellas), a little paler and pinker than the plains.
    dust = np.array([0.70, 0.52, 0.40], np.float32) * (0.95 + 0.08 * drift[..., None])
    rgb = rgb * (1 - 0.3 * floor[..., None]) + dust * 0.3 * floor[..., None]
    # Red sand: redder and brighter than the plains, with faint wind streaking.
    sand_c = np.array([0.73, 0.45, 0.28], np.float32) * (0.93 + 0.12 * drift[..., None])
    rgb = rgb * (1 - 0.85 * sand[..., None]) + sand_c * 0.85 * sand[..., None]
    # Charred ground: grey-brown, mottled.
    char = ramp(rank(fbm(n[3], p * 9 + warp, 4)), m["char"])
    rgb = rgb * (1 - 0.9 * burned[..., None]) + char * 0.9 * burned[..., None]
    # Crater rims a touch paler; wind streaks pale on dark ground (dust laid in the lee) and
    # dark on pale ground (dust scoured away).
    rgb = rgb * (1 + 0.1 * rimc[..., None])
    # (Which way is set by the smooth burn field: a threshold on brightness flipped the sign
    # inside a tail and cut ragged patches out of it.)
    sgn = (2 * smoothstep(0.15, 0.6, burned) - 1)[..., None]
    rgb = rgb * (1 + 0.24 * sgn * streak[..., None])
    # The remnant: old dark melt, half dusted over.
    melt = np.array([0.17, 0.14, 0.13], np.float32)
    rmt = remnant * (0.75 + 0.25 * smoothstep(0.2, -0.2, drift))
    rgb = rgb * (1 - 0.8 * rmt[..., None]) + melt * 0.8 * rmt[..., None]

    # Living waters: a tiny dark lake in a hollow, a dark olive fringe of life around it.
    water = np.zeros(g.lat.shape, np.float32)
    green = np.zeros(g.lat.shape, np.float32)
    for la, lo, r in m["waters"]:
        sub = rows_near(g, la, r * 5 + 1)
        ps = p[sub]
        d = angular_distance(g, la, lo)[sub]
        # Drawn out along a hollow (as Siwa's lakes lie in a long depression): a string of
        # small pools, and a ribbon of life along it reaching past them.
        _, oe, on = frame(la, lo)
        b = rng.uniform(0, np.pi)
        lx = np.degrees(np.arcsin(np.clip(ps @ oe, -1, 1)))
        ly = np.degrees(np.arcsin(np.clip(ps @ on, -1, 1)))
        along = lx * np.cos(b) + ly * np.sin(b)
        # A winding hollow, not a straight trough: bend it and let it wander.
        across = -lx * np.sin(b) + ly * np.cos(b) + 0.1 * along**2 / r + 0.45 * r * fbm(n[4], ps * (4 / r) + lo, 3)
        dd = np.sqrt((along / 3.0) ** 2 + across**2) * ((ps @ unit(la, lo)) > 0) + 9 * ((ps @ unit(la, lo)) <= 0)
        jag = r * 0.35 * fbm(n[4], ps * (25 / r) + lo, 4)
        pools = smoothstep(0.1, 0.5, fbm(n[5], ps * (12 / r) + la, 3) + 0.3)
        water[sub] = np.maximum(water[sub], smoothstep(0.32 * r, 0.2 * r, dd + jag) * pools)
        # Life reaches farther along the hollow than across it, in patches, not as a ring.
        dg = np.sqrt((along / 5.0) ** 2 + across**2) * ((ps @ unit(la, lo)) > 0) + 9 * ((ps @ unit(la, lo)) <= 0)
        patches = smoothstep(-0.25, 0.35, fbm(n[6], ps * (30 / r) + lo, 3))
        green[sub] = np.maximum(green[sub], smoothstep(1.1 * r, 0.2 * r, dg + 2.0 * jag) * (0.25 + 0.75 * patches))
    # Whidmore's farms: centre-pivot circles, some green, some fallow, strung along a line.
    pivots = np.zeros(g.lat.shape, np.float32)
    fallow = np.zeros(g.lat.shape, np.float32)
    if m["farms"]:
        f = m["farms"]
        for i in range(f["n"]):
            s = rng.uniform(-1, 1)
            la = f["lat"] + s * f["spread"][0] * 0.6 + rng.normal(0, 0.6)
            lo = f["lon"] + s * f["spread"][1] + rng.normal(0, 0.8)
            r = rng.uniform(0.1, 0.22)
            sub = rows_near(g, la, r * 2 + 0.5)
            d = angular_distance(g, la, lo)[sub]
            disc = smoothstep(r, r * 0.8, d)
            if rng.uniform() < 0.7:
                pivots[sub] = np.maximum(pivots[sub], disc * rng.uniform(0.7, 1.0))
            else:
                fallow[sub] = np.maximum(fallow[sub], disc)
    veg = np.array([0.20, 0.23, 0.13], np.float32)
    rgb = rgb * (1 - 0.75 * green[..., None]) + veg * 0.75 * green[..., None]
    rgb = rgb * (1 - pivots[..., None]) + np.array([0.26, 0.29, 0.17], np.float32) * pivots[..., None]
    rgb = rgb * (1 - 0.5 * fallow[..., None]) + np.array([0.50, 0.38, 0.28], np.float32) * 0.5 * fallow[..., None]
    rgb = rgb * (1 - water[..., None]) + np.array([0.05, 0.08, 0.09], np.float32) * water[..., None]
    rgb = rgb * (1 + 0.05 * grain[..., None] + 0.1 * gibber[..., None] * (1 - water[..., None]))
    print(f"  {slug}: colour {time.time() - t0:.1f}s")

    # --- Lights. ---------------------------------------------------------------------------
    lights = np.zeros(g.lat.shape, np.float32)
    glint = np.random.default_rng(m["seed"] + 1).random(g.lat.shape).astype(np.float32)

    def town(la, lo, r, b, n_roads):
        """A bright core, street lights thinning outward, and roads as dotted lines."""
        sub = rows_near(g, la, 4.5 * r + 0.5)
        d = angular_distance(g, la, lo)[sub]
        t = d / r
        _, te, tn = frame(la, lo)
        a = np.arctan2(p[sub] @ tn, p[sub] @ te)
        core = smoothstep(0.45, 0.1, t)
        streets = (glint[sub] > 0.3 + 0.5 * t) * smoothstep(1.4, 0.3, t)
        roads = np.zeros_like(d)
        for bearing in rng.uniform(0, 2 * np.pi, n_roads):
            perp = np.abs(d * np.sin(a - bearing))
            along = d * np.cos(a - bearing)
            roads = np.maximum(roads, smoothstep(0.05, 0.015, perp) * (along > 0) * smoothstep(4.0 * r, 1.2 * r, d) * (glint[sub] > 0.55))
        lights[sub] += b * (0.7 * core + 0.5 * streets + 0.3 * roads)

    for la, lo, r, b, k in m["towns"]:
        town(la, lo, r, b, k)
    # Faint specks: half at the waters' edges, half scattered on open ground.
    spots = []
    for la, lo, r in m["waters"]:
        if (la, lo) != (GOSHEN[0] - 0.5, GOSHEN[1] - 0.9):
            spots.append((la + rng.normal(0, 0.4), lo + rng.normal(0, 0.5)))
    while len(spots) < m["specks"]:
        la = float(np.degrees(np.arcsin(rng.uniform(-0.8, 0.8))))
        lo = float(rng.uniform(-180, 180))
        if np.degrees(np.arccos(np.clip(unit(la, lo) @ unit(*BREAK), -1, 1))) > R + 10:
            spots.append((la, lo))
    for la, lo in spots:
        town(la, lo, rng.uniform(0.1, 0.22), rng.uniform(0.18, 0.32), 0)
    lights = np.clip(lights, 0, 1.2)
    emissive = WARM * lights[..., None]
    # Built-up ground by day: Goshen's core a little greyer.
    built = np.clip(lights, 0, 1)[..., None] * 0.35
    rgb = rgb * (1 - built) + np.array([0.42, 0.37, 0.33], np.float32) * built
    print(f"  {slug}: lights {time.time() - t0:.1f}s")

    rough = np.clip(0.92 - 0.6 * water, 0, 1)
    height = np.clip(e * (1 - water) + 0.02 * pivots + 0.006 * gibber, 0, 1)
    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    save_rgb(out / "albedo.webp", rgb)
    save_rgb(out / "emissive.webp", emissive)
    save_gray(out / "roughness.webp", rough)
    save_gray(out / "height.webp", height)
    save_rgb(out / "normal.webp", normal_map(height * 0.012, strength=1.0))
    write_pins(out / "pins.json", m["name"], m["pins"])
    print(f"  {slug}: done {time.time() - t0:.1f}s -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", default=list(TWINS))
    ap.add_argument("--width", type=int, default=None, help="override both twins' widths")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "web/static/system")
    args = ap.parse_args()
    for name in args.names:
        generate(name, TWINS[name], args.width or WIDTHS[name], args.out)

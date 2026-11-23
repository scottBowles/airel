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
  ancient scar whose floor now reads as a smooth, bright, low-contrast dust plain, ringed by
  darker, rougher ground). The remnant is one small, eroded crescent of dark knobby rock (old
  melt) on the basin floor, half buried in dust. The smaller twin has the same, smaller. Both
  break faces sit at (0, 180), facing each other (the pair is taken to be mutually tidally
  locked).
- "Since the cataclysm ... the place is burned pretty deep" (Didymus Prime log): broad
  charred, warm brown-black ground (burned rock), thickest in a ring around the old break and
  reaching outward in a few big lobes, streaked by drifting dust (like Mars's dark albedo
  regions, e.g. Syrtis Major). One large-scale field drives it (distance from the break,
  strongly warped, plus low-frequency noise), so it forms a few big provinces with graded
  edges, not a print of same-sized blotches. The smaller twin is more charred: two or three
  big dark provinces.
- "Lots of sand ... very few living waters, so life is gathered around them" (DB notes);
  "dustbowl"; "how do you get water out of a rock?". Rust and red sand and stony plains (the
  Simpson Desert's red dunes, the Pilbara's old iron-red ranges), and Mars's contrast between
  bright butterscotch dust provinces and the dark ones. Not Janus's pale tan Sahara. No salt
  or claypans (Janus's signature; tried, they read as ragged pale decals). Old weathered
  craters with Mars-style wind streaks: the thin, dusty air keeps them, and every streak
  points downwind. The smaller twin gets a handful of larger craters, dust-floored on dark
  ground, as eye anchors.
- Living waters: Prime 4 (Goshen's the largest), the other twin 2 (brief: 4 / 2-3). Each is a
  tiny round dark lake with a graded olive fringe. Positions besides Goshen's are guesses.
- Whidmore "is still buying up land ... to terraform and turn it into agriculture": a few
  small centre-pivot fields near Goshen (brief: farm patches near 30, 70), like Saudi Arabia's
  pivot farms; light and few, so at disc scale they're tone, not dots. Invented look.
- Lights: Goshen, "the biggest city on the planet", the one real cluster; Ashtown a dim speck
  (a ghost town); faint scattered specks (trailer towns, warehouses, call centres, nomad
  camps). The other twin barely inhabited (DM default): a few faint specks at its waters.
- No clouds: thin dusty air. Haze is a render setting (see the hand-off report).

Shape: the app deforms the sphere into a bean (integration work). Taken here: long axis
through the poles (about 1.45 : 1), indent centred on (0, 180). So nothing important sits
poleward of about 55° or right in the indent's middle, and the poles (the bean's tips) get
the same detail as everywhere else.
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
        burned=0.26,  # share of the surface that is charred dark ground
        # The char is one large field: distance from the break, warped by cap_warp degrees per
        # unit of low-frequency fbm (about ±0.17 std, so ±19° here), plus an independent
        # low-frequency field (weight char_far) for provinces that reach away from the break.
        cap_warp=110,
        cap_scale=90,  # degrees of distance per unit of the char field
        char_far=1.2,  # small: Prime's burn hugs the break
        bright=0.30,  # share in bright dust provinces (Mars's butterscotch regions)
        sand=0.18,  # share in red sand seas
        ranges=0.22,  # share in old eroded ranges
        craters=46,
        small_craters=500,
        anchors=0,
        # Warm brown-black char: burned rock, not grey soot.
        char=[(0, (0.17, 0.12, 0.09)), (0.5, (0.24, 0.17, 0.12)), (1, (0.33, 0.23, 0.16))],
        # Living waters: (lat, lon, radius°). Goshen's is the largest (brief); others invented.
        waters=[(GOSHEN[0] - 0.5, GOSHEN[1] - 0.9, 0.75), (-9, 14, 0.4), (36, -38, 0.45), (-27, -86, 0.35)],
        farms=dict(lat=29.5, lon=66, n=12, spread=(2.6, 5.5)),
        # (lat, lon, radius°, brightness, roads). Goshen: the one real cluster, with its edge
        # settlements (the One Horn Riders' compound, construction sites, warehouses) around it.
        # Ashtown: a dim speck, a near ghost town.
        towns=[
            (GOSHEN[0], GOSHEN[1], 0.95, 1.0, 2),
            (23.6, 53.6, 0.22, 0.45, 0),
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
        burned=0.50,  # the smaller twin: darker, more charred, rockier, more craters
        cap_warp=130,
        cap_scale=200,  # weak pull to the break: a threshold near 90° from it ran along a meridian
        char_far=3.0,  # large: two or three big char provinces, not one cap
        bright=0.14,
        sand=0.08,
        ranges=0.26,
        craters=60,
        small_craters=420,
        anchors=6,  # a handful of larger craters to catch the eye
        char=[(0, (0.15, 0.11, 0.08)), (0.5, (0.22, 0.15, 0.11)), (1, (0.31, 0.21, 0.15))],
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


def _rotation(seed: int) -> np.ndarray:
    q, _ = np.linalg.qr(np.random.default_rng(seed).normal(size=(3, 3)))
    return q.astype(np.float32)


ROT = (_rotation(1), _rotation(2))


def fbm_iso(noise: Noise3, p: np.ndarray, octaves: int) -> np.ndarray:
    """fbm with the lattice hidden, for the large-scale fields. Perlin noise's lowest octave
    lines up with its lattice planes, and with an integer offset those pass through x, y, z = 0:
    a field that is mostly one low octave drew a straight char edge along the ±90° meridians.
    Two copies in different orientations, summed (same spread as one), have no shared planes."""
    return (fbm(noise, p @ ROT[0], octaves) + fbm(noise, p @ ROT[1] + 0.5, octaves)) / np.sqrt(2)


def soft_ridged(noise: Noise3, p: np.ndarray, octaves: int = 5) -> np.ndarray:
    """Like planetgen.ridged, 0..1, but with rounded crests: a sharp crease in a low octave
    shaded as a long hairline crack across tens of degrees."""
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for i in range(octaves):
        v = noise(p * freq + i * 7.77)
        total = total + amp * (1 - np.sqrt(v * v + 0.03)) ** 2
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return np.clip(total / norm / 0.83, 0, 1)


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
    n = [Noise3(m["seed"] * 10 + i) for i in range(12)]
    p = g.xyz

    # --- One warped field: relief, and from it everything else. ---------------------------
    warp = np.stack([fbm_iso(n[0], p * 1.5 + 11, 5), fbm_iso(n[1], p * 1.5 + 23, 5), fbm_iso(n[2], p * 1.5 + 37, 5)], -1)
    base = rank(fbm(n[3], p * 2.4 + warp * 1.2, 8))
    # Old ranges (the Pilbara's worn, folded iron ranges): provinces of the high ground.
    province = rank(fbm_iso(n[4], p * 1.8 + warp * 0.8 + 3, 5) + 0.6 * (base - 0.5))
    rmask = smoothstep(1 - m["ranges"] - 0.06, 1 - m["ranges"] + 0.08, province)
    # Rounded crests, lightly warped (more bends and it swirls like a fingerprint).
    ridges = soft_ridged(n[5], p * 10 + warp * 0.8, 5)  # short crests: at 6 one ran 25° as a crack
    h = 0.78 * base + 0.18 * rmask * (ridges - 0.35)

    # The worn break: a broad, shallow, smooth-floored basin facing the other twin, its rim
    # ragged (the warp moves it several degrees) so it isn't a drawn circle.
    d0 = angular_distance(g, *BREAK)
    d_break = d0 + 28 * fbm_iso(n[6], p * 2.0 + warp, 5)
    R = m["break_r"]
    bowl = smoothstep(R * 1.15, R * 0.35, d_break)
    floor = smoothstep(R * 1.0, R * 0.2, d_break)
    # Around it, a ring of rougher, broken ground (Hellas's rim: Hellespontus, Promethei).
    ring = smoothstep(R * 1.9, R * 1.15, d_break) * smoothstep(R * 0.55, R * 0.95, d_break)
    h = h * (1 - 0.7 * floor) + 0.25 * (0.7 * floor) - 0.3 * bowl + 0.1 * ring * (ridges - 0.4)

    # The remnant: one small eroded crescent of dark knobby rock (old melt), off-centre.
    rm = m["remnant"]
    c, east, north = frame(rm["lat"], rm["lon"])
    x = np.degrees(np.arcsin(np.clip(p @ east, -1, 1)))
    y = np.degrees(np.arcsin(np.clip(p @ north, -1, 1)))
    tl = np.radians(rm["tilt"])
    xr, yr = x * np.cos(tl) + y * np.sin(tl), -x * np.sin(tl) + y * np.cos(tl)
    bend = 0.06 * yr**2  # a crescent, bowed away from the basin's centre
    ell = np.sqrt(((xr - bend) / rm["ax"]) ** 2 + (yr / rm["ay"]) ** 2)
    ell = np.where((p @ c) > 0, ell, 9)
    knobs = soft_ridged(n[7], p * 22 + warp, 3)
    remnant = smoothstep(1.15, 0.45, ell + 0.35 * fbm(n[8], p * 18, 4)) * (0.35 + 0.65 * smoothstep(0.35, 0.7, knobs))
    h = h + 0.12 * remnant

    # Craters: old and weathered (soft, low rims, shallow), a power law of sizes, at every
    # latitude (the poles are the bean's tips and get seen).
    k = m["craters"]
    z = rng.uniform(np.sin(np.radians(-82)), np.sin(np.radians(82)), k)
    clat = list(np.degrees(np.arcsin(z)))
    clon = list(rng.uniform(-180, 180, k))
    crad = list(0.35 + 4.5 * rng.uniform(0, 1, k) ** 3)
    # Eye anchors (the smaller twin): a handful of larger craters, spread out, off the basin.
    na = m["anchors"]
    while na > 0:
        la = float(np.degrees(np.arcsin(rng.uniform(-0.85, 0.85))))
        lo = float(rng.uniform(-180, 180))
        if np.degrees(np.arccos(np.clip(unit(la, lo) @ unit(*BREAK), -1, 1))) < R * 1.3:
            continue
        if any(np.degrees(np.arccos(np.clip(unit(la, lo) @ unit(a, b), -1, 1))) < 30 for a, b in zip(clat[k:], clon[k:])):
            continue
        clat.append(la)
        clon.append(lo)
        crad.append(float(rng.uniform(2.6, 6.0)))
        na -= 1
    crat = np.zeros(g.lat.shape, np.float32)
    rimc = np.zeros(g.lat.shape, np.float32)
    cfloor = np.zeros(g.lat.shape, np.float32)  # dust-filled floors of the large craters
    acrat = np.zeros(g.lat.shape, np.float32)  # their sharper relief, added to the height map
    streak = np.zeros(g.lat.shape, np.float32)  # downwind tails
    for i, (la, lo, r) in enumerate(zip(clat, clon, crad)):
        reach = r * 9 + 1
        sub = rows_near(g, la, reach)
        cc, ce, cn = frame(la, lo)
        ps = p[sub]
        d = np.degrees(np.arccos(np.clip(ps @ cc, -1, 1)))
        t = d / r
        wob = 1 + 0.12 * fbm(n[9], ps * (40 / max(r, 0.6)) + la, 3)
        tw = t * wob
        depth = 0.05 + 0.01 * r if i < k else 0.13 + 0.018 * r
        crat[sub] += (-(1 - np.minimum(tw, 1) ** 2) * (tw < 1) * 0.6 + 0.15 * np.exp(-(((tw - 1) / 0.4) ** 2))) * depth
        rimc[sub] = np.maximum(rimc[sub], np.exp(-(((tw - 1) / 0.4) ** 2)))
        if i >= k:
            cfloor[sub] = np.maximum(cfloor[sub], smoothstep(1.1, 0.1, tw))
            # Flat dust floor, a steep wall, a low soft rim: enough slope to shade at disc scale.
            acrat[sub] += -smoothstep(1.0, 0.7, tw) + 0.3 * np.exp(-(((tw - 1.05) / 0.2) ** 2))
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
    # crisp, at every latitude.
    k = m["small_craters"]
    z = rng.uniform(np.sin(np.radians(-86)), np.sin(np.radians(86)), k)
    for la, lo, r in zip(np.degrees(np.arcsin(z)), rng.uniform(-180, 180, k), 0.1 + 0.3 * rng.uniform(0, 1, k) ** 2):
        sub = rows_near(g, la, r * 2 + 0.2)
        t = np.degrees(np.arccos(np.clip(p[sub] @ unit(la, lo), -1, 1))) / r
        near = t < 2
        tn = t[near]
        crat[sub][near] += (-(1 - np.minimum(tn, 1) ** 2) * (tn < 1) * 0.6 + 0.15 * np.exp(-(((tn - 1) / 0.35) ** 2))) * 0.05
        rimc[sub][near] = np.maximum(rimc[sub][near], 0.6 * np.exp(-(((tn - 1) / 0.35) ** 2)))
    # The basin floor is dust-smoothed: craters there are faint.
    h = h + crat * (1 - 0.7 * floor)
    rimc = rimc * (1 - 0.8 * floor)
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

    # Charred ground: one large-scale field. Distance from the break, warped strongly so the
    # edge wanders 15-25° (fbm is only ±0.17), plus a low-frequency field of its own so a few
    # big provinces reach out from it; finer noise only along the edges. The basin floor is
    # dust-filled since (as on Mars), so the char rings it rather than covering it.
    lowf = fbm_iso(n[10], p * 1.6 + warp * 0.6 + 5, 4) + 0.6 * fbm_iso(n[9], p * 3.5 + warp + 13, 3)
    far = fbm_iso(n[11], p * 1.4 + warp * 0.8 + 41, 4)
    cap = d0 + m["cap_warp"] * lowf
    edge = fbm(n[7], p * 5 + warp * 1.5, 5)
    burn_raw = -cap / m["cap_scale"] + m["char_far"] * far + 0.6 * edge + 0.15 * drift - 1.2 * floor
    burn_f = rank(burn_raw)
    thr = 1 - m["burned"]
    # Wide, graded edges, and darker the deeper into the burn.
    deep = smoothstep(thr, 1.0, burn_f)
    burned = smoothstep(thr - 0.2, thr + 0.14, burn_f) * (0.6 + 0.4 * deep)
    burned = burned * (0.85 + 0.15 * smoothstep(-0.3, 0.3, drift))  # dust drifts over it in streaks
    # Around the living waters the ground has had water and life since; clear of char.
    for la, lo, r in m["waters"]:
        burned = burned * smoothstep(3 + 3 * r, 7 + 8 * r, angular_distance(g, la, lo) + 2.5 * fine)
    if m["farms"]:  # Whidmore farms where the ground isn't charred
        f = m["farms"]
        burned = burned * smoothstep(4, 9, angular_distance(g, f["lat"], f["lon"]) + 2.5 * fine)

    # Bright dust provinces (Mars's butterscotch: Arabia, Tharsis): low-frequency, leaning to
    # the low ground, never on the char.
    dust_f = rank(fbm_iso(n[5], p * 1.3 + warp * 0.9 + 19, 5) + 0.15 * edge)  # no relief term: its fine valleys cut dark threads
    bright = smoothstep(1 - m["bright"] - 0.12, 1 - m["bright"] + 0.08, dust_f) * (1 - burned)

    # Red sand seas: in the low ground, downwind (the drift field), never on the ranges.
    sand_f = rank(fbm_iso(n[1], pw * 2.2 + warp * 1.3 + 9, 6) - 0.9 * e - 0.6 * rmask + 0.2 * fbm(n[2], pw * 14 + warp, 4))
    sand = smoothstep(1 - m["sand"] - 0.14, 1 - m["sand"] + 0.12, sand_f) * (1 - 0.8 * burned) * (1 - floor)
    sand = sand * (0.7 + 0.3 * smoothstep(-0.4, 0.4, drift))  # thinning in streaks, not a flat fill

    # No claypans or salt: drawn small they came out as ragged pale decals, and white pans
    # are Janus's signature. The low ground is dust and red sand instead.

    # Texture contrast, damped on the dust-smoothed basin floor.
    calm = (1 - 0.75 * floor)[..., None]

    # Base: stony rust plains, darker and browner up on the high ground (gibber and rock).
    tone = rank(fbm(n[2], p * 4 + warp * 1.4, 6)) * 0.5 + 0.5 * e
    rgb = ramp(
        tone,
        [
            (0.0, (0.70, 0.49, 0.35)),  # dusty lowland
            (0.4, (0.62, 0.42, 0.29)),  # rust plains
            (0.75, (0.52, 0.34, 0.24)),  # stony upland
            (1.0, (0.43, 0.28, 0.20)),  # old rock
        ],
    )
    rgb = rgb * (1 + 0.16 * fine[..., None] * calm)
    # The ranges: dark iron-red rock, crests catching light, gullies shaded.
    rock = np.array([0.42, 0.26, 0.18], np.float32) * (0.75 + 0.55 * ridges[..., None])
    rgb = rgb * (1 - 0.7 * rmask[..., None]) + rock * 0.7 * rmask[..., None]
    # Bright butterscotch dust (luminance about 0.6).
    bdust = np.array([0.87, 0.63, 0.45], np.float32) * (0.96 + 0.06 * drift[..., None])
    rgb = rgb * (1 - 0.9 * bright[..., None]) + bdust * 0.9 * bright[..., None]
    # The basin floor: smooth, bright, low-contrast fine dust (Hellas).
    dust = np.array([0.78, 0.58, 0.44], np.float32) * (0.97 + 0.04 * drift[..., None])
    fl = 0.8 * floor[..., None]
    rgb = rgb * (1 - fl) + dust * fl
    # Red sand: redder than the plains, with faint wind streaking.
    sand_c = np.array([0.74, 0.46, 0.29], np.float32) * (0.93 + 0.12 * drift[..., None])
    rgb = rgb * (1 - 0.85 * sand[..., None]) + sand_c * 0.85 * sand[..., None]
    # Charred ground: warm brown-black, darkest deepest in the burn, varied at a broad scale.
    ctone = np.clip(0.55 * (1 - deep) + 0.45 * rank(fbm(n[3], p * 3.5 + warp, 5)), 0, 1)
    char = ramp(ctone, m["char"])
    rgb = rgb * (1 - 0.92 * burned[..., None]) + char * 0.92 * burned[..., None]
    # The large craters' floors: dust laid in them, pale on dark ground, so they stand out.
    cf = (cfloor * (0.25 + 0.35 * burned))[..., None]
    rgb = rgb * (1 - cf) + dust * 0.95 * cf
    # Crater rims barely paler; wind streaks pale on dark ground (dust laid in the lee) and
    # dark on pale ground (dust scoured away).
    rgb = rgb * (1 + 0.04 * rimc[..., None])
    # (Which way is set by the smooth burn field: a threshold on brightness flipped the sign
    # inside a tail and cut ragged patches out of it.)
    sgn = (2 * smoothstep(0.15, 0.6, burned) - 1)[..., None]
    rgb = rgb * (1 + 0.24 * sgn * streak[..., None] * calm)
    # The remnant: old dark melt, half dusted over.
    melt = np.array([0.17, 0.13, 0.11], np.float32)
    rmt = 0.6 * remnant * (0.7 + 0.3 * smoothstep(0.2, -0.2, drift))
    rgb = rgb * (1 - 0.8 * rmt[..., None]) + melt * 0.8 * rmt[..., None]

    # Living waters: a small round dark lake in a hollow, a graded olive fringe of life around
    # it (an oasis seen from orbit: a soft dark spot, not a line).
    water = np.zeros(g.lat.shape, np.float32)
    green = np.zeros(g.lat.shape, np.float32)
    for la, lo, r in m["waters"]:
        sub = rows_near(g, la, r * 5 + 1)
        ps = p[sub]
        d = angular_distance(g, la, lo)[sub]
        jag = r * 0.12 * fbm(n[4], ps * (25 / r) + lo, 4)
        lob = r * 0.15 * fbm(n[5], ps * (6 / r) + la, 3)  # a little out of round
        water[sub] = np.maximum(water[sub], smoothstep(0.6 * r, 0.2 * r, d + jag + lob))
        patches = smoothstep(-0.3, 0.3, fbm(n[6], ps * (20 / r) + lo, 3))
        fringe = smoothstep(3.4 * r, 0.5 * r, d + 4 * jag + 2 * lob)
        green[sub] = np.maximum(green[sub], fringe * (0.6 + 0.4 * patches) * (0.5 + 0.5 * smoothstep(2.2 * r, 0.7 * r, d)))
    # Whidmore's farms: a few small centre-pivot circles, pale olive, some fallow.
    pivots = np.zeros(g.lat.shape, np.float32)
    fallow = np.zeros(g.lat.shape, np.float32)
    if m["farms"]:
        f = m["farms"]
        for i in range(f["n"]):
            s = rng.uniform(-1, 1)
            la = f["lat"] + s * f["spread"][0] * 0.6 + rng.normal(0, 0.6)
            lo = f["lon"] + s * f["spread"][1] + rng.normal(0, 0.8)
            r = rng.uniform(0.1, 0.2)
            sub = rows_near(g, la, r * 2 + 0.5)
            d = angular_distance(g, la, lo)[sub]
            disc = smoothstep(r, r * 0.75, d)
            if rng.uniform() < 0.6:
                pivots[sub] = np.maximum(pivots[sub], disc * rng.uniform(0.5, 0.8))
            else:
                fallow[sub] = np.maximum(fallow[sub], disc)
    veg = np.array([0.30, 0.29, 0.17], np.float32)
    rgb = rgb * (1 - 0.7 * green[..., None]) + veg * 0.7 * green[..., None]
    rgb = rgb * (1 - pivots[..., None]) + np.array([0.40, 0.38, 0.22], np.float32) * pivots[..., None]
    rgb = rgb * (1 - 0.4 * fallow[..., None]) + np.array([0.56, 0.42, 0.30], np.float32) * 0.4 * fallow[..., None]
    rgb = rgb * (1 - water[..., None]) + np.array([0.06, 0.08, 0.08], np.float32) * water[..., None]
    rgb = rgb * (1 + (0.05 * grain[..., None] + 0.1 * gibber[..., None]) * calm * (1 - water[..., None]))
    print(f"  {slug}: colour {time.time() - t0:.1f}s")

    # --- Lights. ---------------------------------------------------------------------------
    lights = np.zeros(g.lat.shape, np.float32)
    glint = np.random.default_rng(m["seed"] + 1).random(g.lat.shape).astype(np.float32)

    def town(la, lo, r, b, n_roads):
        """A soft bright core, street lights thinning outward, and a road or two as dotted
        lines (no ring of spokes: that reads as a reticle)."""
        sub = rows_near(g, la, 4.5 * r + 0.5)
        d = angular_distance(g, la, lo)[sub]
        t = d / r
        _, te, tn = frame(la, lo)
        a = np.arctan2(p[sub] @ tn, p[sub] @ te)
        core = np.exp(-((t / 0.35) ** 2))
        streets = (glint[sub] > 0.35 + 0.55 * t) * smoothstep(1.3, 0.2, t)
        roads = np.zeros_like(d)
        for bearing in rng.uniform(0, 2 * np.pi, n_roads):
            perp = np.abs(d * np.sin(a - bearing))
            along = d * np.cos(a - bearing)
            roads = np.maximum(roads, smoothstep(0.04, 0.015, perp) * (along > 0) * smoothstep(3.0 * r, 0.8 * r, d) * (glint[sub] > 0.7))
        lights[sub] += b * (0.7 * core + 0.4 * streets + 0.25 * roads)

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
    # Height from the relief itself, not its rank: ranking stretched the flat basin floor's
    # tiny differences into steps that shaded as cliffs.
    lo_, hi_ = np.percentile(h, [0.5, 99.5])
    hn = np.clip((h - lo_) / (hi_ - lo_), 0, 1)
    height = np.clip(hn * (1 - water) + 0.25 * acrat + 0.01 * pivots + 0.006 * gibber * calm[..., 0], 0, 1)
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

"""Cloud layers with structure at every scale, for any planet with weather.

A single smooth noise field cut at a threshold makes soft blobs. Real cloud seen from orbit has:
- weather systems: bands and cyclones that decide where cloud gathers;
- clumps: cumulus popcorn and cells, rounded and bunched together;
- feathered edges, where the cloud breaks up into fragments as it thins;
- wisps: thin streaks drawn out along the wind;
- uneven thickness inside, so the tops catch light on one side and shade on the other.

make_clouds returns the alpha (how much each texel is covered) and a thickness field that the
caller turns into a normal map, which shades the tops in the app.
"""

from __future__ import annotations

import numpy as np

from gonhirrim import storm_coords, tangent_basis
from planetgen import Noise3, fbm, smoothstep, unit


def rank(x: np.ndarray) -> np.ndarray:
    u = np.empty(x.size, np.float32)
    u[np.argsort(x, axis=None)] = np.linspace(0, 1, x.size, dtype=np.float32)
    return u.reshape(x.shape)


def billow(noise: Noise3, p: np.ndarray, octaves: int) -> np.ndarray:
    """Puffy, rounded lumps (0..1): fbm of |noise|, inverted so the lumps are the high parts."""
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for i in range(octaves):
        total = total + amp * (1 - np.abs(noise(p * freq + i * 13.7)))
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return total / norm


def spiral(p: np.ndarray, s: dict, scale: float = 1.0) -> np.ndarray:
    """Wind points about a storm's centre. Turning that falls off with distance alone shears
    cloud into rings; adding a turn that grows with log(1/distance), as air spirals inward,
    bends features into arms that wind toward the eye."""
    d, c = storm_coords(p, s)
    sign = np.sign(s["swirl"])
    ang = scale * (s["swirl"] * np.exp(-(d**2) * 1.4) - sign * s.get("inflow", 1.0) * np.log(d + 0.1) * np.exp(-(d**2) * 0.8))
    cos, sin = np.cos(ang)[..., None], np.sin(ang)[..., None]
    k = c[None, None, :]
    return p * cos + np.cross(k, p) * sin + k * (p @ c)[..., None] * (1 - cos)


def arc_distance(p: np.ndarray, a: tuple[float, float], b: tuple[float, float]):
    """Angular distance (radians) from points to the great-circle arc a→b, and how far along it
    (0 at a, 1 at b) each point lies."""
    ua, ub = unit(*a), unit(*b)
    length = np.arccos(np.clip(ua @ ub, -1, 1))
    nrm = np.cross(ua, ub)
    nrm = nrm / np.linalg.norm(nrm)
    off = np.arcsin(np.clip(np.abs(p @ nrm), 0, 1))
    from_a = np.arccos(np.clip(p @ ua, -1, 1))
    from_b = np.arccos(np.clip(p @ ub, -1, 1))
    inside = (from_a <= length) & (from_b <= length)
    dist = np.where(inside, off, np.minimum(from_a, from_b))
    return dist, np.clip(from_a / length, 0, 1)


def zones(lat: np.ndarray) -> np.ndarray:
    """Earth-like circulation: a cloudy band at the equator, clearer subtropics (the calm
    high-pressure belts near 25°), and stormy mid-latitudes."""
    a = np.abs(lat)
    return 0.25 * np.exp(-((lat / 7) ** 2)) - 0.2 * np.exp(-(((a - 25) / 8) ** 2)) + 0.15 * np.exp(-(((a - 50) / 10) ** 2))


def make_clouds(g, seed: int, cover: float, storms: list[dict], veil: tuple[float, float] = (0.0, 0.0), zoning: float = 0.0, log=print):
    """Cloud alpha (0..1) and thickness for a planet. `cover` is roughly the share under thick cloud;
    `veil` the (min, max) alpha of a thin overcast everywhere; `zoning` how strongly cloud follows
    the latitude zones.

    Each storm: lat, lon, ax, ay (its extent, degrees), swirl (turn at the centre, radians:
    + anticlockwise), and optionally inflow (how tightly the arms wind), strength (how much
    cloud it gathers), eye (how clear its centre is), face (direction of its cloud shield, radians)
    and front: the (lat, lon) the trailing cold front reaches."""
    n = [Noise3(seed * 7 + i) for i in range(8)]
    lat = np.degrees(g.lat)
    # The big field takes the storms' full twist, which makes the spiral arms; the small-scale
    # texture only half, or it winds too tightly around each centre.
    q = g.xyz
    for s in storms:
        q = spiral(q, s)
    qh = g.xyz
    for s in storms:
        qh = spiral(qh, s, 0.5)
    # Winds shear everything along latitude: the same points, squashed toward the pole axis.
    qz = q * np.array([1.0, 1.0, 2.6], np.float32)
    warp = np.stack([fbm(n[0], q * 2.5 + 3, 4), fbm(n[1], q * 2.5 + 9, 4), fbm(n[2], q * 2.5 + 17, 4)], -1)

    # Weather systems: where cloud gathers at all.
    raw = fbm(n[3], qz * 3.2 + warp * 1.6, octaves=6) + zoning * zones(lat) / 0.25
    rough = fbm(n[6], q * 12 + warp * 2, 4)
    for s in storms:
        # A comma, not a pinwheel: the cloud shield wraps one side, a dry slot cuts the other.
        d, _ = storm_coords(q, s)
        c, east, north = tangent_basis(s["lat"], s["lon"])
        side = 0.5 + 0.5 * np.cos(np.arctan2(q @ north, q @ east) - s.get("face", 0.0))
        k = s.get("strength", 1.0)
        raw = raw + k * (0.22 * np.exp(-(d**2) * 1.8) * (0.3 + 0.7 * side) - 0.15 * np.exp(-(d**2) * 4) * (1 - side))
        raw = raw - 0.4 * s.get("eye", 1.0) * np.exp(-((d / 0.06) ** 2))
        if "front" in s:
            # The trailing front: a long band, ragged along its length, thinning toward its end.
            dist, along = arc_distance(q, (s["lat"], s["lon"]), s["front"])
            band = np.exp(-((dist / np.radians(2.2 + 1.5 * along)) ** 2)) * (1 - 0.6 * along)
            raw = raw + 0.5 * k * band * (0.7 + 0.6 * rough)
    systems = rank(raw)
    log("  clouds: systems")
    # Clumps at two sizes, bent by the same winds so cells line up in streets and spirals.
    qm = qh * np.array([1.0, 1.0, 1.4], np.float32)  # small cloud is only a little sheared
    clump = billow(n[4], qm * 14 + warp * 4, 4)
    fine = billow(n[5], qm * 55 + warp * 6, 3)
    pop = billow(n[0], qm * 80 + warp * 8, 2)
    log("  clouds: clumps")
    # Wisps: long thin filaments along the wind, strongest where cloud is thin.
    streak = 1 - np.abs(fbm(n[6], q * np.array([6.0, 6.0, 28.0], np.float32) + warp * 3, 4) * 2)
    streak = smoothstep(0.55, 0.95, streak)
    log("  clouds: wisps")

    # Density: the systems decide the broad shape; the clumps carve its edges into fragments,
    # so the boundary breaks up instead of fading smoothly.
    edge = 1 - cover
    # Steep at the large scale, so systems have definite edges; the fine terms feather them.
    fray = fbm(n[7], qm * 120 + warp * 6, 3)
    density = (systems - edge) * 3.5 + 0.55 * (clump - 0.55) + 0.4 * (fine - 0.55) + 0.5 * fray
    thick = smoothstep(-0.12, 0.4, density) ** 0.8
    # Uneven tops: thickest in the clump cores, never a flat sheet.
    thick = thick * (0.68 + 0.32 * smoothstep(0.3, 0.85, clump * 0.6 + fine * 0.4))
    # Around the systems' fringes and across the clear gaps: wisps along the wind, and small
    # popcorn cumulus.
    fringe = smoothstep(edge - 0.4, edge, systems) * (1 - thick)
    wisps = 0.7 * streak * fringe * (0.6 + 0.4 * fine)
    popcorn = 0.75 * smoothstep(0.8, 0.92, pop) * smoothstep(0.45, 0.75, fine) * fringe
    alpha = np.maximum(thick, np.maximum(wisps, popcorn))
    if veil[1] > 0:
        haze = veil[0] + (veil[1] - veil[0]) * smoothstep(0.2, 0.8, rank(fbm(n[7], qz * 2 + warp, 5)))
        haze = haze * (0.75 + 0.5 * (fine - 0.5))  # mottled, not a flat film
        alpha = haze + (1 - haze) * alpha
    thickness = thick * (0.75 + 0.25 * clump) + 0.3 * wisps + 0.3 * popcorn
    return np.clip(alpha, 0, 1).astype(np.float32), thickness.astype(np.float32)

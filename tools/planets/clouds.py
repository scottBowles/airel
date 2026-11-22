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

from gonhirrim import swirl
from planetgen import Noise3, fbm, smoothstep


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


def make_clouds(g, seed: int, cover: float, storms: list[dict], veil: tuple[float, float] = (0.0, 0.0), belts: float = 0.0, log=print):
    """Cloud alpha (0..1) and thickness for a planet. `cover` is roughly the share under thick cloud;
    `veil` the (min, max) alpha of a thin overcast everywhere; `belts` how strongly cloud gathers
    in bands either side of the equator."""
    n = [Noise3(seed * 7 + i) for i in range(8)]
    lat = np.degrees(g.lat)
    q = g.xyz
    for s in storms:
        q = swirl(q, s)
    # Winds shear everything along latitude: the same points, squashed toward the pole axis.
    qz = q * np.array([1.0, 1.0, 2.6], np.float32)
    warp = np.stack([fbm(n[0], q * 2.5 + 3, 4), fbm(n[1], q * 2.5 + 9, 4), fbm(n[2], q * 2.5 + 17, 4)], -1)

    # Weather systems: where cloud gathers at all.
    systems = rank(fbm(n[3], qz * 3.2 + warp * 1.6, octaves=6) + belts * np.cos(np.radians(lat) * 5))
    log("  clouds: systems")
    # Clumps at two sizes, bent by the same winds so cells line up in streets and spirals.
    qm = q * np.array([1.0, 1.0, 1.4], np.float32)  # small cloud is only a little sheared
    clump = billow(n[4], qm * 14 + warp * 4, 4)
    fine = billow(n[5], qm * 55 + warp * 6, 3)
    pop = billow(n[0], qm * 150 + warp * 8, 2)
    log("  clouds: clumps")
    # Wisps: long thin filaments along the wind, strongest where cloud is thin.
    streak = 1 - np.abs(fbm(n[6], q * np.array([9.0, 9.0, 40.0], np.float32) + warp * 3, 4) * 2)
    streak = smoothstep(0.55, 0.95, streak)
    log("  clouds: wisps")

    # Density: the systems decide the broad shape; the clumps carve its edges into fragments,
    # so the boundary breaks up instead of fading smoothly.
    edge = 1 - cover
    density = (systems - edge) * 2.2 + 0.6 * (clump - 0.55) + 0.35 * (fine - 0.55)
    thick = smoothstep(-0.2, 0.55, density) ** 0.8
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

"""Shared helpers for generating planet texture maps from a feature spec.

Everything works on an equirectangular (lat/long) grid: column = longitude from -180° (left)
to +180° (right), row = latitude from +90° (top) to -90° (bottom). Noise is sampled on the
unit sphere in 3D, so maps have no seam at ±180° and no stretching at the poles.

Features are placed by latitude/longitude in degrees, so the same numbers place both the
terrain and the place pins in the app.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


# --- Grid -----------------------------------------------------------------------------------


@dataclass
class Grid:
    width: int
    lat: np.ndarray  # radians, shape (H, W)
    lon: np.ndarray
    xyz: np.ndarray  # unit vectors, shape (H, W, 3)

    @property
    def height(self) -> int:
        return self.width // 2


def make_grid(width: int) -> Grid:
    h = width // 2
    lon = (np.arange(width) + 0.5) / width * 2 * np.pi - np.pi
    lat = np.pi / 2 - (np.arange(h) + 0.5) / h * np.pi
    lon, lat = np.meshgrid(lon, lat)
    xyz = np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], axis=-1)
    return Grid(width, lat.astype(np.float32), lon.astype(np.float32), xyz.astype(np.float32))


def unit(lat_deg: float, lon_deg: float) -> np.ndarray:
    la, lo = math.radians(lat_deg), math.radians(lon_deg)
    return np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)], np.float32)


def angular_distance(g: Grid, lat_deg: float, lon_deg: float) -> np.ndarray:
    """Great-circle distance in degrees from every texel to a point."""
    d = np.clip(g.xyz @ unit(lat_deg, lon_deg), -1, 1)
    return np.degrees(np.arccos(d))


def segment_distance(g: Grid, a: tuple[float, float], b: tuple[float, float]) -> np.ndarray:
    """Distance in degrees from every texel to the great-circle arc a→b (each (lat, lon))."""
    pa, pb = unit(*a), unit(*b)
    n = np.cross(pa, pb)
    n /= np.linalg.norm(n)
    # Closest point on the full great circle, then clamp to the arc's ends.
    off = np.degrees(np.arcsin(np.clip(g.xyz @ n, -1, 1)))
    proj = g.xyz - (g.xyz @ n)[..., None] * n
    proj /= np.linalg.norm(proj, axis=-1, keepdims=True) + 1e-9
    arc = math.acos(float(np.clip(pa @ pb, -1, 1)))
    ang_a = np.arccos(np.clip(proj @ pa, -1, 1))
    ang_b = np.arccos(np.clip(proj @ pb, -1, 1))
    on_arc = (ang_a <= arc + 1e-6) & (ang_b <= arc + 1e-6)
    da = np.degrees(np.arccos(np.clip(g.xyz @ pa, -1, 1)))
    db = np.degrees(np.arccos(np.clip(g.xyz @ pb, -1, 1)))
    return np.where(on_arc, np.abs(off), np.minimum(da, db))


# --- Noise ----------------------------------------------------------------------------------


class Noise3:
    """Seeded 3D gradient (Perlin) noise, vectorised over numpy arrays. Range about -1..1."""

    def __init__(self, seed: int):
        rng = np.random.default_rng(seed)
        self.perm = np.tile(rng.permutation(256), 2).astype(np.int32)
        g = rng.normal(size=(256, 3)).astype(np.float32)
        self.grad = g / np.linalg.norm(g, axis=1, keepdims=True)

    def __call__(self, p: np.ndarray) -> np.ndarray:
        pi = np.floor(p).astype(np.int32)
        pf = (p - pi).astype(np.float32)
        pi &= 255
        u = pf * pf * pf * (pf * (pf * 6 - 15) + 10)
        perm, grad = self.perm, self.grad
        out = 0.0
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    h = perm[perm[perm[pi[..., 0] + dx] + pi[..., 1] + dy] + pi[..., 2] + dz]
                    d = pf - np.array([dx, dy, dz], np.float32)
                    dot = np.einsum("...i,...i->...", grad[h], d)
                    w = (u[..., 0] if dx else 1 - u[..., 0]) * (u[..., 1] if dy else 1 - u[..., 1]) * (
                        u[..., 2] if dz else 1 - u[..., 2]
                    )
                    out = out + w * dot
        return out * 1.6


def fbm(noise: Noise3, p: np.ndarray, octaves: int = 6, lacunarity: float = 2.0, gain: float = 0.5) -> np.ndarray:
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for i in range(octaves):
        total = total + amp * noise(p * freq + i * 17.31)
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / norm


def ridged(noise: Noise3, p: np.ndarray, octaves: int = 5) -> np.ndarray:
    """Sharp-crested ridges, 0..1: good for mountain ranges and lava cracks."""
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for i in range(octaves):
        total = total + amp * (1 - np.abs(noise(p * freq + i * 7.77))) ** 2
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return total / norm


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# --- Output ---------------------------------------------------------------------------------


def normal_map(height: np.ndarray, strength: float) -> np.ndarray:
    """Tangent-space normal map (OpenGL / glTF: +X east, +Y north) from an equirect height map
    (height in planet radii)."""
    h, w = height.shape
    lat = np.pi / 2 - (np.arange(h) + 0.5) / h * np.pi
    dlon = 2 * np.pi / w
    dlat = np.pi / h
    east = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) / (2 * dlon)
    east /= np.maximum(np.cos(lat), 0.05)[:, None]
    up = np.vstack([height[:1], height[:-1]])
    down = np.vstack([height[1:], height[-1:]])
    north = (up - down) / (2 * dlat)
    n = np.stack([-east * strength, -north * strength, np.ones_like(height)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n * 0.5 + 0.5


def save_rgb(path: Path, rgb: np.ndarray, quality: int = 90) -> None:
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8))
    img.save(path, quality=quality, method=6)


def save_gray(path: Path, x: np.ndarray, quality: int = 90) -> None:
    img = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), mode="L")
    img.save(path, quality=quality, method=6)


def write_pins(path: Path, body: str, pins: list[dict]) -> None:
    path.write_text(json.dumps({"body": body, "pins": pins}, indent=2) + "\n")

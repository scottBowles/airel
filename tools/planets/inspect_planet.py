"""Look at a generated planet the way a reviewer will, without the web app.

    python3 tools/planets/inspect_planet.py web/static/system/janus /tmp/janus-inspect [--sun LAT,LON]

Renders the textures onto a lit sphere (sun-lit albedo with the normal map, clouds, and the
emissive lights on the night side) and writes PNG contact sheets to the output folder:

- `discs.png`: the whole planet from four sides, roughly as the lab shows it, and (for a
  planet with lights and a turning day) the same four sides at night.
- `places.png`: close-ups of each pinned place, at about the closest zoom the app allows
  (one texel ≈ two screen pixels on a retina screen), lit and at night.
- `suspects.png`: the albedo tiles that score worst on a few automatic checks for faults the
  user has caught before, each rendered close up so you can judge them:
  `stripes` (one strong spatial frequency: corduroy, moiré, fingerprints),
  `speckle` (texel-scale noise: TV static), `lines` (thin dark lines: worm tracks, webbing),
  `edges` (hard cut-outs).
- `report.txt`: the scores per check and simple colour statistics.

The renderer is an approximation of the app (Lambert lighting, no tone mapping, no
atmosphere glow), good enough to spot pattern problems. Judge final colour in the app.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load(path: Path, mode: str = "RGB") -> np.ndarray | None:
    if not path.exists():
        return None
    return np.asarray(Image.open(path).convert(mode), np.float32) / 255


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def sample(tex: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Bilinear lookup in an equirectangular map (left edge 180° W, top the north pole)."""
    h, w = tex.shape[:2]
    x = (lon + 180) / 360 * w - 0.5
    y = (90 - lat) / 180 * h - 0.5
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx = (x - x0)[..., None] if tex.ndim == 3 else x - x0
    fy = (y - y0)[..., None] if tex.ndim == 3 else y - y0
    x0 %= w
    x1 = (x0 + 1) % w
    y0c = np.clip(y0, 0, h - 1)
    y1c = np.clip(y0 + 1, 0, h - 1)
    a = tex[y0c, x0] * (1 - fx) + tex[y0c, x1] * fx
    b = tex[y1c, x0] * (1 - fx) + tex[y1c, x1] * fx
    return a * (1 - fy) + b * fy


class Planet:
    def __init__(self, src: Path):
        self.albedo = srgb_to_lin(load(src / "albedo.webp"))
        em = load(src / "emissive.webp")
        self.emissive = srgb_to_lin(em) if em is not None else None
        self.normal = load(src / "normal.webp")
        self.clouds = load(src / "clouds.webp", "L")
        pins = src / "pins.json"
        self.pins = json.loads(pins.read_text())["pins"] if pins.exists() else []

    def render(self, centre, half_width, size, sun, night_only=False, glow=1.2, cloud_opacity=0.7):
        """Orthographic view of the unit sphere looking at `centre` (lat, lon); `half_width` is
        half the view's width in sphere radii (1.05 shows the whole disc)."""
        c = unit(*centre)
        east = np.cross([0, 0, 1], c) if abs(c[2]) < 0.999 else np.array([0.0, 1.0, 0.0])
        east /= np.linalg.norm(east)
        north = np.cross(c, east)
        s = np.linspace(-half_width, half_width, size)
        u, v = np.meshgrid(s, -s)
        r2 = u * u + v * v
        inside = r2 < 1
        z = np.sqrt(np.clip(1 - r2, 0, 1))
        p = u[..., None] * east + v[..., None] * north + z[..., None] * c
        lat = np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1)))
        lon = np.degrees(np.arctan2(p[..., 1], p[..., 0]))
        sdir = unit(*sun)
        n = p
        if self.normal is not None:
            t = sample(self.normal, lat, lon) * 2 - 1
            lo, la = np.radians(lon), np.radians(lat)
            e_loc = np.stack([-np.sin(lo), np.cos(lo), np.zeros_like(lo)], -1)
            n_loc = np.stack([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)], -1)
            n = t[..., :1] * e_loc + t[..., 1:2] * n_loc + t[..., 2:3] * p
            n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
        sunward = p @ sdir
        diffuse = np.clip(n @ sdir, 0, 1) * np.clip(sunward * 8 + 0.5, 0, 1)
        col = sample(self.albedo, lat, lon)
        if self.clouds is not None and cloud_opacity > 0:
            a = (sample(self.clouds, lat, lon) * cloud_opacity)[..., None]
            col = col * (1 - a) + np.array([0.75, 0.75, 0.76]) * a
        light = 0.04 + 2.2 * diffuse[..., None]
        out = np.zeros(col.shape) if night_only else col * light
        if self.emissive is not None:
            night = np.clip(0.5 - sunward * 6, 0, 1)[..., None]
            out = out + glow * sample(self.emissive, lat, lon) * night
        out = lin_to_srgb(out / (1 + out * 0.15))  # gentle roll-off instead of a hard clip
        out[~inside] = 0.02
        return Image.fromarray((out * 255).astype(np.uint8))


def label(im: Image.Image, text: str) -> Image.Image:
    d = ImageDraw.Draw(im)
    d.text((8, 6), text, fill=(255, 255, 255), font=ImageFont.truetype(FONT, 15), stroke_width=2, stroke_fill=(0, 0, 0))
    return im


def sheet(images: list[Image.Image], cols: int) -> Image.Image:
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    out = Image.new("RGB", (cols * w, rows * h), (20, 20, 20))
    for i, im in enumerate(images):
        out.paste(im, ((i % cols) * w, (i // cols) * h))
    return out


def blur(x: np.ndarray, r: float) -> np.ndarray:
    """Separable Gaussian blur (σ = r texels), wrapping east–west."""
    k = np.arange(-int(3 * r + 1), int(3 * r + 1) + 1)
    wts = np.exp(-0.5 * (k / r) ** 2)
    wts /= wts.sum()
    out = sum(wt * np.roll(x, s, axis=1) for s, wt in zip(k, wts))
    pad = np.pad(out, ((len(k) // 2, len(k) // 2), (0, 0)), mode="edge")
    return sum(wt * pad[i : i + x.shape[0]] for i, wt in enumerate(wts))


def tile_scores(albedo: np.ndarray, tile: int = 128):
    """Score square tiles of the albedo (below 70° latitude) on each automatic check."""
    lum = albedo.mean(-1) if albedo.ndim == 3 else albedo
    lum = lin_to_srgb(lum)
    h, w = lum.shape
    band = lum - blur(lum, 4.0)  # keep only pattern-scale detail, not broad shading
    fine = lum - blur(lum, 1.0)
    dark_line = np.clip(blur(lum, 3.0) - blur(lum, 0.8), 0, None)
    gy, gx = np.gradient(blur(lum, 0.6))
    grad = np.hypot(gx, gy)
    win = np.outer(np.hanning(tile), np.hanning(tile))
    rows = []
    for y in range(0, h - tile + 1, tile):
        lat = 90 - (y + tile / 2) / h * 180
        if abs(lat) > 70:
            continue
        for x in range(0, w - tile + 1, tile):
            t = lum[y : y + tile, x : x + tile]
            b = band[y : y + tile, x : x + tile]
            sd = b.std()
            f = np.abs(np.fft.fftshift(np.fft.fft2((b - b.mean()) * win))) ** 2
            cy = cx = tile // 2
            f[cy - 3 : cy + 4, cx - 3 : cx + 4] = 0  # drop broad, low-frequency variation
            stripes = f.max() / (f.sum() + 1e-9) * (sd > 0.01)
            rows.append(
                dict(
                    lat=lat,
                    lon=(x + tile / 2) / w * 360 - 180,
                    stripes=float(stripes),
                    speckle=float(fine[y : y + tile, x : x + tile].std()),
                    lines=float((dark_line[y : y + tile, x : x + tile] > 0.035).mean()),
                    edges=float((grad[y : y + tile, x : x + tile] > 0.08).mean()),
                )
            )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--sun", default=None, help="sub-solar LAT,LON for a fixed sun (tidally locked worlds)")
    ap.add_argument("--places", type=int, default=12, help="max pinned places to show")
    ap.add_argument("--suspects", type=int, default=3, help="worst tiles shown per check")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    pl = Planet(a.src)
    fixed = tuple(float(v) for v in a.sun.split(",")) if a.sun else None
    h, w = pl.albedo.shape[:2]
    texel = 360 / w  # degrees per texel
    # Close view: one texel ≈ two pixels of a 512-px image → 256 texels across.
    close_hw = np.radians(256 * texel) / 2

    def sun_for(lat, lon):
        return fixed if fixed else (lat + 20, lon - 50)  # lit from the upper left

    discs = []
    for lon in (-90, 0, 90, 180):
        discs.append(label(pl.render((15, lon), 1.05, 640, sun_for(15, lon)), f"lon {lon}"))
    if pl.emissive is not None and not fixed:
        for lon in (-90, 0, 90, 180):
            discs.append(label(pl.render((15, lon), 1.05, 640, (-15, lon + 180), night_only=True), f"lon {lon}, night"))
    sheet(discs, 4).save(a.out / "discs.png")

    places = []
    for pin in pl.pins[: a.places]:
        la, lo = pin["lat"], pin["lon"]
        day = pl.render((la, lo), close_hw, 512, sun_for(la, lo))
        night = pl.render((la, lo), close_hw, 512, (-la, lo + 180), night_only=True)
        name = pin["name"][:40]
        places += [label(day, f"{name} (lit)"), label(night, f"{name} (night)")]
    if places:
        sheet(places, 4).save(a.out / "places.png")

    scores = tile_scores(pl.albedo)
    lines = []
    suspects = []
    shown = []  # one view per spot, so a single bad area doesn't fill every row
    for key in ("stripes", "speckle", "lines", "edges"):
        vals = np.array([r[key] for r in scores])
        order = np.argsort(-vals)
        lines.append(f"{key:8s} median {np.median(vals):.4f}  p90 {np.percentile(vals, 90):.4f}  max {vals.max():.4f}")
        picked = []
        for i in order:
            r = scores[i]
            if any(abs(r["lat"] - q["lat"]) < 8 and abs(r["lon"] - q["lon"]) < 8 for q in picked + shown):
                continue
            picked.append(r)
            if len(picked) == a.suspects:
                break
        shown += picked
        for r in picked:
            lines.append(f"    {r[key]:.4f} at lat {r['lat']:.1f}, lon {r['lon']:.1f}")
            # Always lit from nearby and without clouds: these views are for judging the albedo.
            im = pl.render((r["lat"], r["lon"]), close_hw, 512, (r["lat"] + 20, r["lon"] - 50), cloud_opacity=0)
            suspects.append(label(im, f"{key} {r[key]:.3f} @ {r['lat']:.0f},{r['lon']:.0f}"))
    sheet(suspects, a.suspects).save(a.out / "suspects.png")

    alb = lin_to_srgb(pl.albedo)
    lines.append("")
    lines.append(f"albedo mean sRGB {np.round(alb.reshape(-1, 3).mean(0), 3).tolist()}")
    lum = alb.mean(-1)
    for lo_, hi_ in ((0, 0.1), (0.1, 0.3), (0.3, 0.6), (0.6, 1.01)):
        lines.append(f"  luminance {lo_:.1f}-{hi_:.1f}: {((lum >= lo_) & (lum < hi_)).mean() * 100:.1f}%")
    if pl.emissive is not None:
        em = lin_to_srgb(pl.emissive).max(-1)
        lines.append(f"emissive lit (>0.05): {(em > 0.05).mean() * 100:.2f}% of the map")
    (a.out / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()

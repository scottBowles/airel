"""Smaller copies of every body's maps, for when the full maps (4096 wide) would use too much GPU
memory:

- far/ (512 wide): the whole-system view, where twenty bodies are on screen at once and each
  covers a few dozen pixels. All twenty take about 75 MB on the GPU.
- mid/ (2048 wide): the body in focus on a phone, where the full set (~270 MB) can crash the page.

    python3 tools/planets/far_maps.py

Writes web/static/system/<slug>/{far,mid}/<map>.webp for each map Planet.svelte loads. Run it
again after rebuilding a body's maps.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2] / "web/static/system"
MAPS = ["albedo", "normal", "roughness", "emissive", "clouds", "clouds-normal", "clouds-glow"]


SIZES = {"far": 512, "mid": 2048}


def main() -> None:
    for body in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        for folder, width in SIZES.items():
            shrink(body, body / folder, width)
        print(body.name)


def shrink(body: Path, out: Path, width: int) -> None:
    out.mkdir(exist_ok=True)
    for name in MAPS:
        src = body / f"{name}.webp"
        if not src.exists():
            continue
        img = Image.open(src)
        img.load()
        if img.width > width:
            img = img.resize((width, width // 2), Image.Resampling.LANCZOS)
        img.save(out / src.name, quality=88, method=6)


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    main()

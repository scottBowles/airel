"""Small copies of every body's maps for the whole-system view, where twenty bodies are on screen
at once and each covers a few dozen pixels. Full maps (4096 wide) for all of them would need
gigabytes of GPU memory; these take about a sixteenth of that.

    python3 tools/planets/far_maps.py [--width 1024]

Writes web/static/system/<slug>/far/<map>.webp for each map Planet.svelte loads. Run it again
after rebuilding a body's maps.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2] / "web/static/system"
MAPS = ["albedo", "normal", "roughness", "emissive", "clouds", "clouds-normal", "clouds-glow"]


def main(width: int) -> None:
    for body in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        out = body / "far"
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
        print(body.name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=1024)
    main(**vars(ap.parse_args()))

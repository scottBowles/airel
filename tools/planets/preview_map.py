"""Flat map preview of a generated planet: albedo + glow, with place pins and labels.

    python3 tools/planets/preview_map.py web/static/system/magmus out.png
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

COLORS = {"lore": (120, 255, 140), "layout": (255, 220, 90), "guess": (255, 120, 220)}


def main(src: Path, dst: Path, width: int = 2048) -> None:
    albedo = np.asarray(Image.open(src / "albedo.webp").convert("RGB"), np.float32) / 255
    emissive = np.asarray(Image.open(src / "emissive.webp").convert("RGB"), np.float32) / 255
    img = np.clip(albedo * 0.9 + emissive * 0.8, 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((width, width // 2), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(11, width // 140))
    for lat in (-60, -30, 0, 30, 60):
        y = (90 - lat) / 180 * im.height
        d.line([(0, y), (im.width, y)], fill=(255, 255, 255, 40), width=1)
    pins = json.loads((src / "pins.json").read_text())["pins"]
    for p in pins:
        x = (p["lon"] + 180) / 360 * im.width
        y = (90 - p["lat"]) / 180 * im.height
        c = COLORS[p["confidence"]]
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=c, outline=(0, 0, 0))
        label = p["name"].split(" — ")[0].split(",")[0]
        d.text((x + 7, y - 7), label, fill=c, font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    y = im.height - 22
    for i, (k, c) in enumerate(COLORS.items()):
        d.text((10 + i * 110, y), f"● {k}", fill=c, font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    im.save(dst)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))

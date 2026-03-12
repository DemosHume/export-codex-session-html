#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1280
HEIGHT = 640


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def draw_gradient(canvas: Image.Image) -> None:
    px = canvas.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        r = int(245 * (1 - t) + 232 * t)
        g = int(239 * (1 - t) + 226 * t)
        b = int(230 * (1 - t) + 214 * t)
        for x in range(WIDTH):
            px[x, y] = (r, g, b)


def rounded_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    assets_dir = repo_root / "assets"
    assets_dir.mkdir(exist_ok=True)
    output_path = assets_dir / "social-preview.png"

    image = Image.new("RGB", (WIDTH, HEIGHT), (245, 239, 230))
    draw_gradient(image)
    draw = ImageDraw.Draw(image)

    title_font = load_font("C:/Windows/Fonts/bahnschrift.ttf", 72)
    subtitle_font = load_font("C:/Windows/Fonts/segoeui.ttf", 28)
    chip_font = load_font("C:/Windows/Fonts/segoeuib.ttf", 22)
    body_font = load_font("C:/Windows/Fonts/segoeui.ttf", 24)
    mono_font = load_font("C:/Windows/Fonts/consola.ttf", 22)

    rounded_box(draw, (52, 48, 1228, 592), radius=36, fill=(255, 252, 246), outline=(214, 201, 185), width=2)
    rounded_box(draw, (92, 108, 636, 518), radius=30, fill=(244, 235, 223))
    rounded_box(draw, (674, 108, 1188, 518), radius=30, fill=(33, 37, 41))

    draw.ellipse((944, 54, 1214, 324), fill=(191, 104, 73))
    draw.ellipse((1012, 12, 1188, 188), fill=(230, 181, 143))

    draw.text((94, 70), "Export Codex", font=title_font, fill=(27, 33, 42))
    draw.text((94, 150), "Session HTML", font=title_font, fill=(27, 33, 42))
    draw.text(
        (96, 238),
        "Turn local Codex Desktop transcripts into\nclean, shareable HTML records.",
        font=subtitle_font,
        fill=(92, 86, 77),
        spacing=8,
    )

    chips = [
        ("CURRENT THREAD", 96, 344, 302),
        ("THREAD ID EXPORT", 320, 344, 552),
        ("BOOTSTRAP FILTER", 96, 392, 364),
        ("HTML OUTPUT", 382, 392, 560),
    ]
    for label, x1, y1, x2 in chips:
        rounded_box(draw, (x1, y1, x2, y1 + 40), radius=18, fill=(255, 252, 246), outline=(196, 128, 93), width=2)
        draw.text((x1 + 16, y1 + 8), label, font=chip_font, fill=(153, 78, 49))

    draw.text((96, 462), "Codex skill for readable transcript export", font=body_font, fill=(92, 86, 77))

    rounded_box(draw, (718, 152, 1144, 454), radius=24, fill=(248, 245, 239))
    rounded_box(draw, (742, 182, 970, 220), radius=14, fill=(240, 227, 214))
    draw.text((760, 190), "Sample Export Session", font=chip_font, fill=(38, 44, 55))
    draw.text((742, 254), "User", font=chip_font, fill=(183, 77, 44))
    draw.text((820, 254), "Export this conversation", font=body_font, fill=(44, 49, 58))
    draw.text((742, 306), "Assistant", font=chip_font, fill=(31, 95, 91))
    draw.text((742, 344), "Transcript exported", font=body_font, fill=(44, 49, 58))
    draw.text((742, 378), "successfully.", font=body_font, fill=(44, 49, 58))
    draw.text((742, 420), "codex-session-2026-03-12-....html", font=mono_font, fill=(92, 86, 77))

    draw.text((718, 500), "github.com/DemosHume/export-codex-session-html", font=mono_font, fill=(229, 214, 194))

    image.save(output_path, format="PNG", optimize=True)
    print(output_path)


if __name__ == "__main__":
    main()

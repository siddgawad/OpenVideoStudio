"""Visual stage: render 1920x1080 motion-graphic slides and the thumbnail
with Pillow. Local, deterministic, zero API keys (D-003).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .model import VisualSpec

W, H = 1920, 1080

THEMES = {
    "dark": {"bg": "#101418", "panel": "#181e25", "fg": "#f2f5f8", "muted": "#9aa7b4"},
    "light": {"bg": "#f5f6f8", "panel": "#ffffff", "fg": "#14181d", "muted": "#5a6672"},
}

_FONT_CANDIDATES = {
    "bold": ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf"],
    "regular": ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf"],
}


def _font(kind: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in _FONT_CANDIDATES[kind]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and draw.textlength(trial, font=font) > max_width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [text]


def render_slide(spec: VisualSpec, theme: str, out: Path,
                 *, scene_number: int | None = None,
                 total_scenes: int | None = None) -> None:
    colors = THEMES.get(theme, THEMES["dark"])
    img = Image.new("RGB", (W, H), colors["bg"])
    draw = ImageDraw.Draw(img)

    # accent bar down the left edge
    draw.rectangle([0, 0, 18, H], fill=spec.accent)

    margin = 140
    max_text_w = W - margin - 120

    # heading (auto-shrinks until it wraps to <=3 lines)
    heading_size = 110
    while heading_size > 48:
        font = _font("bold", heading_size)
        lines = _wrap(draw, spec.heading, font, max_text_w)
        if len(lines) <= 3:
            break
        heading_size -= 10
    font = _font("bold", heading_size)
    lines = _wrap(draw, spec.heading, font, max_text_w)

    y = 200
    for line in lines:
        draw.text((margin, y), line, font=font, fill=colors["fg"])
        y += int(heading_size * 1.18)

    # underline accent
    draw.rectangle([margin, y + 18, margin + 220, y + 30], fill=spec.accent)
    y += 90

    # bullets
    bullet_font = _font("regular", 54)
    for bullet in spec.bullets[:4]:
        draw.ellipse([margin, y + 22, margin + 22, y + 44], fill=spec.accent)
        for line in _wrap(draw, bullet, bullet_font, max_text_w - 70)[:2]:
            draw.text((margin + 58, y), line, font=bullet_font,
                      fill=colors["muted"])
            y += 66
        y += 30

    # scene progress marker, bottom-right
    if scene_number and total_scenes:
        marker = f"{scene_number} / {total_scenes}"
        mfont = _font("regular", 36)
        tw = draw.textlength(marker, font=mfont)
        draw.text((W - 80 - tw, H - 96), marker, font=mfont, fill=colors["muted"])

    tmp = out.with_suffix(".tmp.png")
    img.save(tmp, "PNG")
    tmp.replace(out)


def render_thumbnail(text: str, accent: str, theme: str, out: Path) -> None:
    """1280x720 thumbnail: big centered text on a themed background."""
    tw, th = 1280, 720
    colors = THEMES.get(theme, THEMES["dark"])
    img = Image.new("RGB", (tw, th), colors["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, th - 26, tw, th], fill=accent)

    size = 150
    while size > 60:
        font = _font("bold", size)
        lines = _wrap(draw, text, font, tw - 160)
        if len(lines) <= 3:
            break
        size -= 12
    font = _font("bold", size)
    lines = _wrap(draw, text, font, tw - 160)
    total_h = len(lines) * int(size * 1.15)
    y = (th - total_h) // 2
    for line in lines:
        lw = draw.textlength(line, font=font)
        draw.text(((tw - lw) // 2, y), line, font=font, fill=colors["fg"])
        y += int(size * 1.15)

    tmp = out.with_suffix(".tmp.png")
    img.save(tmp, "PNG")
    tmp.replace(out)

#!/usr/bin/env python3
"""
Generate 1200x630 link-preview (Open Graph) cards.

    python scripts/make_og.py              # site card + one per paper
    python scripts/make_og.py <slug>       # just one paper

Cards are written to:
    papers/<slug>/images/og.png            per paper
    shared/assets/og-default.png           the site card

They are committed alongside the source, and build.py copies them into the site
and points og:image / twitter:image at them.

Why generate rather than reuse the hero: preview images want a 1.91:1 frame and
a legible title, because most surfaces (Slack, LinkedIn, iMessage, Discord) show
the image far more prominently than the text. A 4:3 hero gets cropped badly and
a paper with no hero would have nothing at all.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
SHARED = ROOT / "shared"

sys.path.insert(0, str(Path(__file__).resolve().parent))

W, H = 1200, 630

# cool palette, matching the site's dark theme
BG = (22, 27, 34)
PANEL = (29, 36, 45)
TEXT = (228, 233, 239)
MUTED = (150, 163, 176)
ACCENT = (143, 166, 245)
RULE = (45, 55, 66)

FONT_CANDIDATES = {
    "bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ],
    "regular": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ],
}


def font(kind: str, size: int):
    from PIL import ImageFont
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text: str, fnt, max_w: int, max_lines: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words:
        # ellipsize if we ran out of room
        joined = " ".join(lines)
        if len(joined) < len(text):
            while lines and draw.textlength(lines[-1] + "...", font=fnt) > max_w:
                lines[-1] = lines[-1].rsplit(" ", 1)[0]
            lines[-1] += "..."
    return lines


def card(title: str, subtitle: str, footer: str, hero: Path | None, out: Path) -> None:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    band_w = 0

    # optional hero, as a soft band down the right third
    if hero and hero.exists():
        try:
            h = Image.open(hero).convert("RGB")
            band_w = 430
            ratio = max(band_w / h.width, H / h.height)
            h = h.resize((int(h.width * ratio), int(h.height * ratio)), Image.LANCZOS)
            left = (h.width - band_w) // 2
            top = (h.height - H) // 2
            h = h.crop((left, top, left + band_w, top + H))
            img.paste(h, (W - band_w, 0))
            # fade it into the background so text stays readable
            grad = Image.new("L", (band_w, 1))
            for x in range(band_w):
                grad.putpixel((x, 0), int(255 * min(1.0, (x / band_w) * 1.5)))
            grad = grad.resize((band_w, H))
            img.paste(Image.new("RGB", (band_w, H), BG), (W - band_w, 0),
                      Image.eval(grad, lambda v: 255 - v))
            d = ImageDraw.Draw(img)
        except Exception:
            pass

    pad = 72
    text_w = (W - band_w - 40 - pad) if band_w else (W - 2 * pad)

    # accent rule
    d.rectangle([pad, 92, pad + 74, 98], fill=ACCENT)

    f_title = font("bold", 62)
    f_sub = font("regular", 30)
    f_foot = font("regular", 24)

    y = 140
    for line in wrap(d, title, f_title, text_w, 3):
        d.text((pad, y), line, font=f_title, fill=TEXT)
        y += 74

    if subtitle:
        y += 14
        for line in wrap(d, subtitle, f_sub, text_w, 2):
            d.text((pad, y), line, font=f_sub, fill=MUTED)
            y += 40

    d.line([(pad, H - 118), (pad + text_w, H - 118)], fill=RULE, width=2)
    d.text((pad, H - 96), footer, font=f_foot, fill=MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"  {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:,.0f} KB)")


def main() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.exit("Pillow is not installed.  pip install -r requirements-pdf.txt")

    from build import load_site_config, load_yaml, paper_authors

    cfg = load_site_config()
    site_name = cfg.get("title", "Papers")
    wanted = [a for a in sys.argv[1:] if not a.startswith("-")]

    dirs = [d for d in sorted(PAPERS.iterdir())
            if d.is_dir() and (d / "paper.yaml").exists()
            and (not wanted or d.name in wanted)]

    print(f"rendering {len(dirs) + (0 if wanted else 1)} card(s):")

    for d in dirs:
        meta = load_yaml(d / "paper.yaml")
        authors = paper_authors(meta, cfg)
        names = ", ".join(a.get("name", "") for a in authors)
        date = str(meta.get("date", ""))
        footer = " · ".join(x for x in (names, date, site_name) if x)
        hero = (d / meta["hero"]) if meta.get("hero") else None
        card(meta.get("title", d.name), meta.get("subtitle", ""), footer,
             hero, d / "images" / "og.png")

    if not wanted:
        card(site_name, cfg.get("tagline", ""),
             cfg.get("author_display") or cfg.get("author", ""),
             None, SHARED / "assets" / "og-default.png")


if __name__ == "__main__":
    main()

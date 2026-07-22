#!/usr/bin/env python3
"""
Emit a single self-contained HTML file for a paper, for review or sharing.

Everything (CSS, JS, images) is inlined, so the file renders correctly when
opened directly from disk with no server and no sibling asset folders.

Usage:
    python scripts/make_review.py <slug> [output.html]

Run scripts/build.py first; this reads from site/.
"""
from __future__ import annotations
import base64, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


def main() -> None:
    slug = sys.argv[1] if len(sys.argv) > 1 else "holonic-neural-networks"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / f"{slug}_REVIEW.html"

    paper_dir = SITE / slug
    src = paper_dir / "index.html"
    if not src.exists():
        sys.exit(f"not built: {src} (run scripts/build.py first)")

    html = src.read_text()

    # inline CSS
    css = (SITE / "assets" / "paper.css").read_text()
    html = html.replace(
        '<link rel="stylesheet" href="../assets/paper.css">',
        f"<style>\n{css}\n</style>")

    # inline the paper JS (nav pane + scroll-spy)
    js = (SITE / "assets" / "paper.js").read_text()
    html = html.replace(
        '<script src="../assets/paper.js" defer></script>',
        f"<script>\n{js}\n</script>")

    # inline images as data URIs
    for rel in sorted(set(re.findall(r'src="(images/[^"]+)"', html))):
        data = base64.b64encode((paper_dir / rel).read_bytes()).decode()
        suffix = Path(rel).suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/jpeg"
        html = html.replace(f'src="{rel}"', f"src=\"data:{mime};base64,{data}\"")

    # no lazy loading: images are embedded, and lazy can misfire on file://
    html = html.replace(' loading="lazy"', "")

    # the top bar links to sibling papers, which don't exist in a lone file
    html = re.sub(r'<div class="topbar">.*?</div>\n', "", html, count=1, flags=re.S)

    # "All papers" links have no target in a standalone file
    dead = 'href="#" onclick="return false" style="opacity:.45;cursor:default"'
    html = html.replace('href="../">&larr; All papers</a>',
                        f"{dead}>&larr; All papers</a>")
    html = html.replace('<a class="footer-home" href="../">',
                        f'<a class="footer-home" {dead}>')

    out.write_text(html)
    leftover = html.count('href="../') + html.count('src="../') + html.count('src="images/')
    print(f"wrote {out}  ({len(html)/1024/1024:.2f} MB, external refs: {leftover})")


if __name__ == "__main__":
    main()

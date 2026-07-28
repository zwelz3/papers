#!/usr/bin/env python3
"""
Scaffold a new paper folder.

    python scripts/new_paper.py <slug> [--title "A Title"] [--date YYYY-MM-DD]

Creates papers/<slug>/ with a commented paper.yaml, a stub index.md, and an
empty images/ directory. Refuses to touch an existing folder. For historical
papers, pass --date with the original writing or sharing date; the site sorts
by it and the citation year comes from it.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"

YAML_TMPL = """\
slug: {slug}
title: {title}
subtitle:
description: >
  A sentence or two for the library card and search index.
date: {date}
status: draft            # flip to "published" when it is ready
license: CC-BY-4.0

# Zenodo DOI. Leave blank until minted.
doi: ""

# The primary author from site.yaml is always included first.
authors: []

tags: []

# Where this paper was previously shared or discussed. Bare URLs get a
# label from their domain; use a label/url map to override.
# discussions:
#   - https://www.linkedin.com/posts/...
#   - label: GitHub discussion
#     url: https://github.com/...

# hero: images/hero.jpeg
figures: {{}}
"""

MD_TMPL = """\
*One italic opening paragraph. It becomes the styled dek under the title.*

Opening prose.

## First section

Body text. For the figure-marker syntax and other conventions, see
"Add a new paper" in the README (and INTAKE.md for converted documents).
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--title", default="")
    ap.add_argument("--date", default=str(datetime.date.today()))
    args = ap.parse_args()

    slug = args.slug.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        sys.exit(f"slug '{slug}' must be lowercase words separated by hyphens")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        sys.exit(f"date '{args.date}' must be YYYY-MM-DD")

    dest = PAPERS / slug
    if dest.exists():
        sys.exit(f"{dest} already exists")

    title = args.title or slug.replace("-", " ").title()
    (dest / "images").mkdir(parents=True)
    (dest / "paper.yaml").write_text(YAML_TMPL.format(slug=slug, title=title, date=args.date), encoding="utf-8")

    (dest / "index.md").write_text(MD_TMPL, encoding="utf-8")

    print(f"created papers/{slug}/  (status: draft)")
    print("next: write index.md, drop images, then `python scripts/check.py`")


if __name__ == "__main__":
    main()

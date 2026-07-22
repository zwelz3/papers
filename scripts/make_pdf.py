#!/usr/bin/env python3
"""
Generate a PDF artifact for each paper, written into that paper's folder.

    python scripts/make_pdf.py                    # every paper
    python scripts/make_pdf.py holonic-neural-networks   # just one

The PDF is written to papers/<slug>/<slug>.pdf. Keeping it in the paper folder
(rather than only in site/) means it is version-controlled alongside the source
and is the file you upload to Zenodo to mint a DOI. The next `build.py` run
copies it into site/<slug>/ and links it from the page.

Requires WeasyPrint (see requirements.txt). The layout comes from the
`@media print` rules in shared/css/paper.css, so the PDF drops the nav chrome
and paginates figures and code blocks sensibly.

Workflow for a DOI:
    1. python scripts/make_pdf.py <slug>
    2. upload papers/<slug>/<slug>.pdf to Zenodo, publish, copy the DOI
    3. put it in papers/<slug>/paper.yaml as `doi: 10.5281/zenodo.XXXXXXX`
    4. python scripts/build.py    (the DOI chip and citation block appear)
    5. optionally re-run make_pdf so the PDF itself carries the DOI
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
SITE = ROOT / "site"

sys.path.insert(0, str(Path(__file__).resolve().parent))


def ensure_built() -> None:
    if not (SITE / "index.html").exists():
        print("site/ not built yet; running build.py first...")
        import build
        build.main()


def render(slug: str) -> Path | None:
    try:
        from weasyprint import HTML
    except ImportError:
        sys.exit("WeasyPrint is not installed.  pip install -r requirements.txt")

    src = SITE / slug / "index.html"
    if not src.exists():
        print(f"  ! {slug}: no built page at {src}")
        return None

    out_site = SITE / slug / f"{slug}.pdf"
    t0 = time.time()
    HTML(filename=str(src), base_url=str(src.parent)).write_pdf(str(out_site))

    # keep the canonical copy next to the source, for git and for Zenodo
    out_src = PAPERS / slug / f"{slug}.pdf"
    shutil.copy(out_site, out_src)

    size = out_site.stat().st_size / 1024
    print(f"  {slug}.pdf  ({size:,.0f} KB, {time.time()-t0:.1f}s) -> papers/{slug}/")
    return out_src


def main() -> None:
    ensure_built()
    wanted = [a for a in sys.argv[1:] if not a.startswith("-")]
    slugs = wanted or [d.name for d in sorted(PAPERS.iterdir())
                       if d.is_dir() and (d / "paper.yaml").exists()]

    print(f"rendering {len(slugs)} PDF(s):")
    made = [render(s) for s in slugs]
    made = [m for m in made if m]

    if made:
        print("\nRe-run `python scripts/build.py` to link the PDFs from the pages.")
        print("Upload a PDF to Zenodo, then set `doi:` in that paper's paper.yaml.")


if __name__ == "__main__":
    main()

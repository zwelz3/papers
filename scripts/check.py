#!/usr/bin/env python3
"""
Validate every paper folder before building.

    python scripts/check.py            # errors exit 1, warnings exit 0
    python scripts/check.py --strict   # warnings also exit 1

Run by CI ahead of build.py so a broken paper cannot deploy. Checks, per
paper:

  errors    paper.yaml parses; title/date/description present; date is
            YYYY-MM-DD; slug (if given) matches the directory name; status is
            published|draft; every [[FIGURE X]] marker has a figures: entry;
            every figures: entry points to a file that exists; hero exists if
            declared; index.md exists and is non-empty; malformed figure
            markers; duplicate slugs across papers
  warnings  figures: entries never referenced by a marker; unknown license
            identifier; no italic dek paragraph at the top; tags that differ
            from another paper's tag only by case or hyphenation; missing
            og.png when base_url is set; committed PDF whose recorded source
            hash no longer matches (see make_pdf.py)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import load_yaml, load_site_config, LICENSES, base_url  # noqa: E402
from make_pdf import source_hash, HASH_NAME  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKER_RE = re.compile(r"\[\[FIGURE ([A-Za-z0-9]+):\s*(.*?)\]\]", re.S)
MARKER_LOOSE_RE = re.compile(r"\[\[\s*FIGURE\b[^\]]*(?:\]\]|\])?", re.S)


def norm_tag(t: str) -> str:
    return re.sub(r"[\s_-]+", " ", t.strip().lower())


def check_paper(paper_dir: Path, cfg: dict, errors: list, warnings: list) -> dict:
    slug = paper_dir.name
    pre = f"papers/{slug}"

    yaml_path = paper_dir / "paper.yaml"
    try:
        meta = load_yaml(yaml_path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{pre}/paper.yaml: does not parse ({exc})")
        return {}
    if not isinstance(meta, dict) or not meta:
        errors.append(f"{pre}/paper.yaml: empty or not a mapping")
        return {}

    for field in ("title", "date", "description"):
        if not str(meta.get(field) or "").strip():
            errors.append(f"{pre}/paper.yaml: missing required field '{field}'")

    date = str(meta.get("date") or "")
    if date and not DATE_RE.match(date):
        errors.append(f"{pre}/paper.yaml: date '{date}' is not YYYY-MM-DD")

    declared = meta.get("slug")
    if declared and declared != slug:
        errors.append(f"{pre}/paper.yaml: slug '{declared}' != directory name '{slug}'")

    status = meta.get("status", "published")
    if status not in ("published", "draft"):
        errors.append(f"{pre}/paper.yaml: status '{status}' is not published|draft")

    lic = meta.get("license")
    if isinstance(lic, str) and lic.strip() and lic.strip() not in LICENSES:
        warnings.append(f"{pre}/paper.yaml: license '{lic}' is not a known identifier; "
                        "it will render as bare text with no link")

    md_path = paper_dir / "index.md"
    if not md_path.exists() or not md_path.read_text(encoding="utf-8").strip():
        errors.append(f"{pre}/index.md: missing or empty")
        return meta
    md = md_path.read_text(encoding="utf-8")

    figures = meta.get("figures", {}) or {}
    markers = {m.group(1) for m in MARKER_RE.finditer(md)}
    loose = len(MARKER_LOOSE_RE.findall(md))
    if loose > len(markers):
        errors.append(f"{pre}/index.md: {loose - len(markers)} malformed [[FIGURE ...]] "
                      "marker(s); the required form is [[FIGURE X: caption]]")

    for key in sorted(markers - set(map(str, figures))):
        errors.append(f"{pre}/index.md: [[FIGURE {key}]] has no figures: entry in paper.yaml")
    for key, rel in figures.items():
        if not (paper_dir / str(rel)).exists():
            errors.append(f"{pre}/paper.yaml: figures[{key}] -> '{rel}' does not exist")
        if str(key) not in markers:
            warnings.append(f"{pre}/paper.yaml: figures[{key}] is never referenced by a marker")

    for i, item in enumerate(meta.get("discussions") or []):
        link = item if isinstance(item, str) else (item or {}).get("url", "") if isinstance(item, dict) else ""
        if not str(link).strip().startswith(("http://", "https://")):
            errors.append(f"{pre}/paper.yaml: discussions[{i}] needs an http(s) url "
                          f"(got {str(link)[:40]!r})")

    hero = meta.get("hero")
    if hero and not (paper_dir / str(hero)).exists():
        errors.append(f"{pre}/paper.yaml: hero '{hero}' does not exist")

    first_para = next((p for p in re.split(r"\n\s*\n", md.strip()) if p.strip()), "")
    if not first_para.startswith(("*", "_")):
        warnings.append(f"{pre}/index.md: no italic opening paragraph; the page "
                        "will render without a dek")

    if base_url(cfg) and not (paper_dir / "images" / "og.png").exists():
        warnings.append(f"{pre}: no images/og.png; link previews fall back to nothing "
                        "(run scripts/make_og.py)")

    pdf = paper_dir / f"{slug}.pdf"
    stamp = paper_dir / HASH_NAME
    if pdf.exists() and stamp.exists() and stamp.read_text(encoding="utf-8").strip() != source_hash(paper_dir):
        warnings.append(f"{pre}/{slug}.pdf: source changed since the PDF was rendered "
                        "(re-run scripts/make_pdf.py)")
    return meta


def main() -> None:
    strict = "--strict" in sys.argv
    cfg = load_site_config()
    errors: list[str] = []
    warnings: list[str] = []

    dirs = [d for d in sorted(PAPERS.iterdir())
            if d.is_dir() and (d / "paper.yaml").exists()]
    if not dirs:
        errors.append("papers/: no paper directories found")

    slugs_seen: dict[str, str] = {}
    tag_forms: dict[str, dict[str, list[str]]] = {}
    for d in dirs:
        meta = check_paper(d, cfg, errors, warnings)
        slug = meta.get("slug", d.name) if meta else d.name
        if slug in slugs_seen:
            errors.append(f"duplicate slug '{slug}' ({slugs_seen[slug]} and papers/{d.name})")
        slugs_seen[slug] = f"papers/{d.name}"
        for t in (meta.get("tags", []) or []) if meta else []:
            tag_forms.setdefault(norm_tag(t), {}).setdefault(t, []).append(d.name)

    for forms in tag_forms.values():
        if len(forms) > 1:
            spell = "; ".join(f"'{f}' in {', '.join(sorted(set(ds)))}" for f, ds in forms.items())
            warnings.append(f"tag spelled inconsistently across papers: {spell}")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    n = len(dirs)
    print(f"checked {n} paper(s): {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors or (strict and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Build every paper in papers/<slug>/ into a static site rooted at site/.

Each paper directory contains:
  paper.yaml   metadata (title, subtitle, description, date, tags, hero, figures)
  index.md     the paper body in Markdown, using figure markers:
                 [[FIGURE N: caption text]]
  images/      hero + figure images referenced from paper.yaml

Output:
  site/index.html                      library landing page (search + tag filter)
  site/<slug>/index.html               each paper (with a collapsible nav pane)
  site/<slug>/images/*                 copied image assets
  site/assets/paper.css                shared stylesheet
  site/assets/site.js                  landing-page search/filter behavior

Design goals:
  - Adding a paper = add a papers/<slug>/ dir. No script edits.
  - Images are separate files (not inlined), served from <slug>/images/.
  - One shared CSS + JS, linked (not duplicated) by every page.
"""
from __future__ import annotations
import re, shutil, html, json
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
SHARED = ROOT / "shared"
SITE = ROOT / "site"

# --- site-level config (title, tagline, author links) -----------------------
def _load_site_config() -> dict:
    cfg_path = ROOT / "site.yaml"
    return load_yaml(cfg_path) if cfg_path.exists() else {}


# Inline SVG marks so the footer works offline and inherits the text color.
# Sources: LinkedIn from Font Awesome Free (CC BY 4.0); GitHub and ORCID from
# Simple Icons (CC0). See README for attribution.
ICONS = {
    "linkedin": (
        '<svg viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M416 32L31.9 32C14.3 32 0 46.5 0 64.3L0 447.7C0 465.5 14.3 480 31.9 480L416 480c17.6 0 32-14.5 32-32.3l0-383.4C448 46.5 433.6 32 416 32zM135.4 416l-66.4 0 0-213.8 66.5 0 0 213.8-.1 0zM102.2 96a38.5 38.5 0 1 1 0 77 38.5 38.5 0 1 1 0-77zM384.3 416l-66.4 0 0-104c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9l0 105.8-66.4 0 0-213.8 63.7 0 0 29.2 .9 0c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9l0 117.2z"/></svg>'
    ),
    "github": (
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>'
    ),
    "orcid": (
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z"/></svg>'
    ),
}


# --- content licenses -------------------------------------------------------
# Papers are licensed separately from the build code (see LICENSE-CONTENT.md).
LICENSES = {
    "CC0-1.0":         ("CC0 1.0",           "https://creativecommons.org/publicdomain/zero/1.0/"),
    "CC-BY-4.0":       ("CC BY 4.0",         "https://creativecommons.org/licenses/by/4.0/"),
    "CC-BY-SA-4.0":    ("CC BY-SA 4.0",      "https://creativecommons.org/licenses/by-sa/4.0/"),
    "CC-BY-ND-4.0":    ("CC BY-ND 4.0",      "https://creativecommons.org/licenses/by-nd/4.0/"),
    "CC-BY-NC-4.0":    ("CC BY-NC 4.0",      "https://creativecommons.org/licenses/by-nc/4.0/"),
    "CC-BY-NC-ND-4.0": ("CC BY-NC-ND 4.0",   "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    "ARR":             ("All rights reserved", ""),
}

CC_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" class="cc-mark">'
    '<path fill="currentColor" d="M11.983 0c-3.292 0-6.19 1.217-8.428 3.485C1.25 5.819 0 8.844 0 12c0 3.189 1.217 6.148 3.522 8.45C5.827 22.75 8.822 24 11.983 24c3.16 0 6.222-1.25 8.593-3.583C22.815 18.214 24 15.287 24 12c0-3.255-1.186-6.214-3.458-8.483C18.238 1.217 15.275 0 11.983 0zm.033 2.17c2.7 0 5.103 1.02 6.98 2.893 1.843 1.841 2.83 4.274 2.83 6.937 0 2.696-.954 5.063-2.798 6.872-1.943 1.906-4.444 2.926-7.012 2.926-2.601 0-5.038-1.019-6.914-2.893-1.877-1.875-2.93-4.34-2.93-6.905 0-2.597 1.053-5.063 2.93-6.97 1.844-1.874 4.214-2.86 6.914-2.86zM8.68 8.278C6.723 8.278 5.165 9.66 5.165 12c0 2.38 1.465 3.722 3.581 3.722 1.358 0 2.516-.744 3.155-1.874l-1.491-.758c-.333.798-.839 1.037-1.478 1.037-1.105 0-1.61-.917-1.61-2.126 0-1.21.426-2.127 1.61-2.127.32 0 .96.173 1.332.97l1.597-.838c-.68-1.236-1.837-1.728-3.181-1.728zm6.932 0c-1.957 0-3.514 1.382-3.514 3.722 0 2.38 1.464 3.722 3.58 3.722 1.359 0 2.516-.744 3.155-1.874l-1.49-.758c-.333.798-.84 1.037-1.478 1.037-1.105 0-1.611-.917-1.611-2.126 0-1.21.426-2.127 1.61-2.127.32 0 .96.173 1.332.97l1.597-.838c-.68-1.236-1.837-1.728-3.181-1.728z"/></svg>'
)


def resolve_license(value, cfg: dict):
    """Accept an identifier string, an explicit {name,url} map, or None."""
    if not value:
        value = cfg.get("default_license")
    if not value:
        return None
    if isinstance(value, dict):
        name, url = value.get("name", ""), value.get("url", "")
        return (name, url) if name else None
    key = str(value).strip()
    if key in LICENSES:
        return LICENSES[key]
    return (key, "")  # unknown identifier: show it verbatim, no link


def render_license(entry, author: str, year: str) -> str:
    if not entry:
        return ""
    name, url = entry
    who = html.escape(author) if author else ""
    copy = f"&copy; {year} {who}".strip() if year or who else ""
    is_cc = name.upper().startswith("CC")
    mark = CC_ICON if is_cc else ""
    if url:
        lic = (f'<a href="{url}" rel="license noopener" target="_blank">'
               f"{mark}{html.escape(name)}</a>")
    else:
        lic = html.escape(name)
    sep = ". " if copy else ""
    return f'<p class="footer-license">{copy}{sep}{lic}</p>'


ICON_LABELS = {"linkedin": "LinkedIn", "github": "GitHub", "orcid": "ORCID"}


def render_footer(cfg: dict, home_href: str, license_html: str = "") -> str:
    """Footer with the author's name, icon links, and (on papers) the license."""
    links = cfg.get("links", {}) or {}
    author = cfg.get("author", "")
    icons = []
    for key in ("linkedin", "github", "orcid"):
        url = links.get(key)
        if not url:
            continue
        label = ICON_LABELS[key]
        icons.append(
            f'<a class="icon-link" href="{url}" title="{label}" '
            f'aria-label="{label}" rel="me noopener" target="_blank">'
            f"{ICONS[key]}</a>"
        )
    icon_html = f'<div class="footer-icons">{"".join(icons)}</div>' if icons else ""
    name_html = f'<p class="footer-name">{html.escape(author)}</p>' if author else ""
    home = f'<a class="footer-home" href="{home_href}">All papers</a>' if home_href else ""
    return (
        '<footer class="site-footer">\n'
        f"  {name_html}\n  {icon_html}\n  {license_html}\n  {home}\n"
        "</footer>"
    )



# ---------- tiny YAML reader (avoids a hard PyYAML dependency) ----------
def load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        pass
    data: dict = {}
    lines = path.read_text().splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", raw)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|"):  # folded / literal block
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                if lines[i].strip():
                    block.append(lines[i].strip())
                i += 1
            data[key] = " ".join(block)
            continue
        if val == "":
            # could be a list ("- item") or a nested mapping ("key: val")
            j = i + 1
            items, submap = [], {}
            while j < len(lines) and (lines[j].startswith("  ") or lines[j].startswith("\t")):
                line = lines[j].strip()
                if line.startswith("- "):
                    items.append(line[2:].strip().strip('"'))
                elif ":" in line:
                    sm = re.match(r'^"?([\w-]+)"?:\s*(.*)$', line)
                    if sm:
                        submap[sm.group(1)] = sm.group(2).strip().strip('"')
                j += 1
            data[key] = items if items else submap
            i = j
            continue
        data[key] = val.strip('"')
        i += 1
    return data


# ---------- heading extraction for the nav pane ----------
_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _slug_re.sub("-", text.lower()).strip("-")


def add_heading_ids(body_html: str):
    """Inject id="..." into h2/h3 and return (html, toc) where toc is a list of
    {level, text, id}."""
    toc = []
    seen = set()

    def repl(m):
        level = m.group(1)
        attrs = m.group(2) or ""
        inner = m.group(3)
        text = re.sub(r"<[^>]+>", "", inner).strip()
        base = slugify(text) or "section"
        sid = base
        n = 2
        while sid in seen:
            sid = f"{base}-{n}"
            n += 1
        seen.add(sid)
        toc.append({"level": int(level), "text": text, "id": sid})
        return f'<h{level}{attrs} id="{sid}">{inner}</h{level}>'

    body_html = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body_html, flags=re.S)
    return body_html, toc


# ---------- markdown -> paper HTML ----------
def render_figures(md: str):
    caps: dict[str, str] = {}

    def repl(m):
        num, cap = m.group(1), m.group(2).strip()
        caps[num] = cap
        return f"@@FIGURE_{num}@@"

    md = re.sub(r"\[\[FIGURE (\d+):\s*(.*?)\]\]", repl, md, flags=re.S)
    return md, caps


def build_paper(paper_dir: Path, cfg: dict) -> dict:
    meta = load_yaml(paper_dir / "paper.yaml")
    slug = meta.get("slug", paper_dir.name)
    md_text = (paper_dir / "index.md").read_text()

    figures = meta.get("figures", {}) or {}
    md_text, caps = render_figures(md_text)

    body = markdown.markdown(
        md_text, extensions=["fenced_code", "tables", "sane_lists"]
    )

    # inject heading anchors + collect a table of contents
    body, toc = add_heading_ids(body)

    # figures -> <figure><img src="images/..."><figcaption>
    for num, rel in figures.items():
        cap = caps.get(str(num), "")
        fig = (
            f'<figure class="fig" id="figure-{num}">\n'
            f'  <img src="{rel}" alt="{html.escape(cap, quote=True)}" loading="lazy" />\n'
            f'  <figcaption>Figure {num}. {cap}</figcaption>\n'
            f"</figure>"
        )
        body = body.replace(f"<p>@@FIGURE_{num}@@</p>", fig)
        body = body.replace(f"@@FIGURE_{num}@@", fig)

    # promote first italic paragraph to a dek
    m = re.search(r"(<p>)(<em>.*?</em>)(</p>)", body, re.S)
    if m and m.start() < 400:
        body = body[: m.start()] + '<p class="dek">' + m.group(2)[4:-5] + "</p>" + body[m.end():]

    title = html.escape(meta.get("title", slug))
    subtitle = meta.get("subtitle", "")
    hero = meta.get("hero")
    tags = meta.get("tags", []) or []

    head_html = f"<h1>{title}</h1>\n"
    if hero:
        head_html += (
            '<figure class="hero">\n'
            f'  <img src="{hero}" alt="{html.escape(title, quote=True)} illustration" />\n'
            "</figure>\n"
        )
    if subtitle:
        head_html += f'<p class="subtitle">{html.escape(subtitle)}</p>\n'
    if tags:
        chips = "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in tags
        )
        head_html += f'<div class="tag-row">{chips}</div>\n'

    # ---- collapsible nav pane (table of contents) ----
    toc_items = []
    for h in toc:
        cls = "toc-2" if h["level"] == 2 else "toc-3"
        toc_items.append(
            f'<li class="{cls}"><a href="#{h["id"]}">{html.escape(h["text"])}</a></li>'
        )
    nav_html = NAV_TMPL.format(
        home_href="../", items="\n".join(toc_items), title=title
    )

    lic_entry = resolve_license(meta.get("license"), cfg)
    year = str(meta.get("date", ""))[:4]
    lic_html = render_license(lic_entry, cfg.get("author", ""), year)

    page = PAGE_TMPL.format(
        title=title,
        css_href="../assets/paper.css",
        js_href="../assets/paper.js",
        nav=nav_html,
        body=head_html + body,
        footer=render_footer(cfg, "../", lic_html),
    )

    out_dir = SITE / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page)

    img_src = paper_dir / "images"
    if img_src.is_dir():
        shutil.copytree(img_src, out_dir / "images", dirs_exist_ok=True)

    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "subtitle": subtitle,
        "description": meta.get("description", ""),
        "date": str(meta.get("date", "")),
        "status": meta.get("status", "published"),
        "tags": tags,
        "hero": f"{slug}/{hero}" if hero else "",
    }


# ---------- templates ----------
NAV_TMPL = """<button class="nav-toggle" aria-expanded="false" aria-controls="nav-pane" title="Contents">
  <span class="nav-toggle-bars"></span><span class="nav-toggle-label">Contents</span>
</button>
<nav id="nav-pane" class="nav-pane" aria-label="On this page">
  <a class="nav-home" href="{home_href}">&larr; All papers</a>
  <p class="nav-heading">On this page</p>
  <ul class="toc">
{items}
  </ul>
</nav>"""

PAGE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{css_href}">
</head>
<body class="has-nav">
{nav}
<article class="wrap">
{body}
{footer}
</article>
<script src="{js_href}" defer></script>
</body>
</html>
"""

INDEX_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{site_title}</title>
<link rel="stylesheet" href="assets/paper.css">
</head>
<body class="library">
<article class="wrap">
<header class="lib-header">
  <h1 class="index-head">{site_title}</h1>
  <p class="index-sub">{tagline}</p>
</header>

<div class="lib-controls">
  <div class="search-wrap">
    <input id="search" type="search" placeholder="Search papers..."
           autocomplete="off" aria-label="Search papers" />
  </div>
  <div id="tag-filters" class="tag-filters">{tag_buttons}</div>
</div>

<p id="result-count" class="result-count"></p>
<ul id="paper-list" class="paper-list">
{items}
</ul>
<p id="empty-state" class="empty-state" hidden>No papers match those filters.</p>
{footer}
</article>

<script>window.__PAPERS__ = {papers_json};</script>
<script src="assets/site.js" defer></script>
</body>
</html>
"""


def build_index(entries: list[dict], cfg: dict) -> None:
    entries = sorted(
        entries, key=lambda e: (e["status"] != "published", e["date"]), reverse=True
    )

    # all tags, by frequency then alpha
    tag_counts: dict[str, int] = {}
    for e in entries:
        for t in e["tags"]:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    all_tags = sorted(tag_counts, key=lambda t: (-tag_counts[t], t))

    tag_buttons = "".join(
        f'<button class="tag-btn" data-tag="{html.escape(t)}">{html.escape(t)}'
        f'<span class="tag-count">{tag_counts[t]}</span></button>'
        for t in all_tags
    )

    items = []
    for e in entries:
        sub = f'<p class="paper-sub">{html.escape(e["subtitle"])}</p>' if e["subtitle"] else ""
        desc = f'<p class="paper-desc">{html.escape(e["description"])}</p>' if e["description"] else ""
        draft = "" if e["status"] == "published" else '<span class="badge-draft">draft</span>'
        meta = ""
        if e["date"]:
            meta = f'<p class="paper-meta"><time>{html.escape(e["date"])}</time>{draft}</p>'
        chips = "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in e["tags"]
        )
        thumb = (
            f'<a class="paper-thumb" href="{e["slug"]}/" tabindex="-1" aria-hidden="true">'
            f'<img src="{e["hero"]}" alt="" loading="lazy" /></a>'
            if e["hero"] else ""
        )
        items.append(
            f'<li class="paper-card" data-slug="{e["slug"]}">\n'
            f'  {thumb}\n'
            f'  <div class="paper-body">\n'
            f'    <a class="paper-title" href="{e["slug"]}/">{html.escape(e["title"])}</a>\n'
            f'    {sub}\n    {desc}\n'
            f'    <div class="tag-row">{chips}</div>\n'
            f'    {meta}\n'
            f'  </div>\n'
            f"</li>"
        )

    # data for client-side search
    papers_json = json.dumps([
        {
            "slug": e["slug"],
            "text": " ".join([
                e["title"], e["subtitle"], e["description"], " ".join(e["tags"])
            ]).lower(),
            "tags": e["tags"],
        }
        for e in entries
    ])

    (SITE / "index.html").write_text(
        INDEX_TMPL.format(
            site_title=html.escape(cfg.get("title", "Papers")),
            tagline=html.escape(cfg.get("tagline", "")),
            tag_buttons=tag_buttons,
            items="\n".join(items),
            papers_json=papers_json,
            footer=render_footer(cfg, ""),
        )
    )


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(SHARED / "css" / "paper.css", SITE / "assets" / "paper.css")
    shutil.copy(SHARED / "js" / "site.js", SITE / "assets" / "site.js")
    shutil.copy(SHARED / "js" / "paper.js", SITE / "assets" / "paper.js")
    (SITE / ".nojekyll").write_text("")

    cfg = _load_site_config()

    entries = []
    for paper_dir in sorted(PAPERS.iterdir()):
        if paper_dir.is_dir() and (paper_dir / "paper.yaml").exists():
            entries.append(build_paper(paper_dir, cfg))
            print(f"built: {paper_dir.name}")

    build_index(entries, cfg)
    print(f"index: {len(entries)} paper(s)")
    print(f"output: {SITE}")


if __name__ == "__main__":
    main()

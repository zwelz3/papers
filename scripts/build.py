#!/usr/bin/env python3
"""
Build every paper in papers/<slug>/ into a static site rooted at site/.

Each paper directory contains:
  paper.yaml   metadata (title, subtitle, description, date, tags, authors,
               doi, license, hero, figures)
  index.md     the paper body in Markdown, using figure markers:
                 [[FIGURE N: caption text]]
  images/      hero + figure images referenced from paper.yaml

Output:
  site/index.html                      library landing page (about + search + tags)
  site/<slug>/index.html               each paper (top bar, nav pane, DOI, license)
  site/<slug>/images/*                 copied image assets
  site/<slug>/<slug>.pdf               PDF artifact, if scripts/make_pdf.py has run

Usage:
  python scripts/build.py            # normal build
  python scripts/build.py --dev      # inject the live-reload poller (see serve.py)

Design goals:
  - Adding a paper = add a papers/<slug>/ dir. No script edits.
  - Images stay separate files, served from <slug>/images/.
  - One shared CSS + JS, linked (not duplicated) by every page.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
import time
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons import CC_ICON, ICONS, ICON_LABELS, THEME_TOGGLE  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
SHARED = ROOT / "shared"
SITE = ROOT / "site"

DEV = "--dev" in sys.argv


# --------------------------------------------------------------------------- #
# YAML
# --------------------------------------------------------------------------- #
def load_yaml(path: Path) -> dict:
    """PyYAML when available; otherwise a small parser covering what we use."""
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

        if val == "":  # list, list-of-maps, or nested map
            j = i + 1
            items: list = []
            submap: dict = {}
            cur = None
            while j < len(lines) and (lines[j].startswith("  ") or lines[j].startswith("\t")):
                line = lines[j].strip()
                indent = len(lines[j]) - len(lines[j].lstrip())
                if line.startswith("- "):
                    rest = line[2:].strip()
                    if ":" in rest and not rest.split(":", 1)[1].strip().startswith("//"):
                        cur = {}
                        k2, v2 = rest.split(":", 1)
                        cur[k2.strip()] = v2.strip().strip('"')
                        items.append(cur)
                    else:
                        items.append(rest.strip('"'))
                        cur = None
                elif ":" in line:
                    k2, v2 = line.split(":", 1)
                    k2, v2 = k2.strip().strip('"'), v2.strip().strip('"')
                    if cur is not None and indent >= 4:
                        cur[k2] = v2
                    else:
                        submap[k2] = v2
                j += 1
            data[key] = items if items else submap
            i = j
            continue

        data[key] = val.strip('"')
        i += 1
    return data


def load_site_config() -> dict:
    cfg = ROOT / "site.yaml"
    return load_yaml(cfg) if cfg.exists() else {}


# --------------------------------------------------------------------------- #
# Licenses
# --------------------------------------------------------------------------- #
LICENSES = {
    "CC0-1.0":         ("CC0 1.0",             "https://creativecommons.org/publicdomain/zero/1.0/"),
    "CC-BY-4.0":       ("CC BY 4.0",           "https://creativecommons.org/licenses/by/4.0/"),
    "CC-BY-SA-4.0":    ("CC BY-SA 4.0",        "https://creativecommons.org/licenses/by-sa/4.0/"),
    "CC-BY-ND-4.0":    ("CC BY-ND 4.0",        "https://creativecommons.org/licenses/by-nd/4.0/"),
    "CC-BY-NC-4.0":    ("CC BY-NC 4.0",        "https://creativecommons.org/licenses/by-nc/4.0/"),
    "CC-BY-NC-ND-4.0": ("CC BY-NC-ND 4.0",     "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    "ARR":             ("All rights reserved", ""),
}


def resolve_license(value, cfg: dict):
    if not value:
        value = cfg.get("default_license")
    if not value:
        return None
    if isinstance(value, dict):
        name, url = value.get("name", ""), value.get("url", "")
        return (name, url) if name else None
    key = str(value).strip()
    return LICENSES.get(key, (key, ""))


def render_license(entry, holder: str, year: str) -> str:
    if not entry:
        return ""
    name, url = entry
    who = html.escape(holder) if holder else ""
    copy = f"&copy; {year} {who}".strip() if (year or who) else ""
    mark = CC_ICON if name.upper().startswith("CC") else ""
    lic = (f'<a href="{url}" rel="license noopener" target="_blank">{mark}'
           f"{html.escape(name)}</a>") if url else html.escape(name)
    sep = ". " if copy else ""
    return f'<p class="footer-license">{copy}{sep}{lic}</p>'


# --------------------------------------------------------------------------- #
# Authors
# --------------------------------------------------------------------------- #
def normalize_author(a) -> dict:
    """Accept a bare name or a mapping with name/orcid/affiliation."""
    if isinstance(a, str):
        return {"name": a}
    return {k: v for k, v in (a or {}).items() if v}


def paper_authors(meta: dict, cfg: dict) -> list[dict]:
    """The site author is always the primary author and is always present."""
    primary = normalize_author({
        "name": cfg.get("author_display") or cfg.get("author", ""),
        "orcid": (cfg.get("links", {}) or {}).get("orcid", ""),
        "affiliation": cfg.get("author_affiliation", ""),
    })
    others = [normalize_author(a) for a in (meta.get("authors") or [])]

    # A paper may redundantly list the primary author, under the display name
    # or the plain one, with or without an honorific. Drop any such repeat.
    aliases = set()
    for form in (cfg.get("author_display", ""), cfg.get("author", ""),
                 primary.get("name", "")):
        if form:
            aliases.add(form.strip().lower())
            aliases.add(cite_name(form).strip().lower())
    others = [a for a in others
              if a.get("name", "").strip().lower() not in aliases
              and cite_name(a.get("name", "")).strip().lower() not in aliases]
    return ([primary] if primary.get("name") else []) + others


def render_authors(authors: list[dict]) -> str:
    if not authors:
        return ""
    parts = []
    for a in authors:
        raw = a.get("name", "")
        name = html.escape(raw)
        if a.get("orcid"):
            name += (f'<a class="orcid-inline" href="{a["orcid"]}" target="_blank" '
                     f'rel="noopener" title="ORCID" aria-label="ORCID for {name}">'
                     f"{ICONS['orcid']}</a>")
        if a.get("affiliation"):
            name += f'<span class="author-aff">{html.escape(a["affiliation"])}</span>'
        parts.append(f'<span class="author">{name}</span>')
    return f'<div class="author-row">{"".join(parts)}</div>\n'


# --------------------------------------------------------------------------- #
# DOI
# --------------------------------------------------------------------------- #
def doi_url(doi: str) -> str:
    doi = (doi or "").strip()
    if not doi:
        return ""
    return doi if doi.startswith("http") else "https://doi.org/" + doi.removeprefix("doi:").strip()


def doi_display(doi: str) -> str:
    return (doi or "").strip().replace("https://doi.org/", "").removeprefix("doi:").strip()


def render_doi(doi: str) -> str:
    if not doi:
        return ""
    return (f'<a class="doi-chip" href="{doi_url(doi)}" target="_blank" rel="noopener" '
            f'title="View on doi.org">DOI<span>{html.escape(doi_display(doi))}</span></a>')


HONORIFIC = re.compile(r"^(?:Dr|Prof|Mr|Ms|Mrs)\.?\s+", re.I)


def cite_name(name: str) -> str:
    """Citations drop honorifics; bylines keep them."""
    return HONORIFIC.sub("", name or "").strip()


def render_cite_block(meta: dict, entry: dict, pdf_href: str) -> str:
    """A 'cite this' box. Only rendered once the paper has a DOI."""
    doi = entry["doi"]
    if not doi:
        return ""
    authors = entry["authors"]
    names = ", ".join(cite_name(a.get("name", "")) for a in authors)
    year = entry["date"][:4]
    title = entry["title"]
    plain = f"{names} ({year}). {title}. {doi_url(doi)}"
    last = cite_name(authors[0].get("name", "x")).split()[-1].lower() if authors else "x"
    bibtex = (f"@misc{{{last}{year},\n"
              f"  author = {{{' and '.join(cite_name(a.get('name','')) for a in authors)}}},\n"
              f"  title  = {{{title}}},\n"
              f"  year   = {{{year}}},\n"
              f"  doi    = {{{doi_display(doi)}}},\n"
              f"  url    = {{{doi_url(doi)}}}\n}}")
    pdf_link = f'<a class="cite-pdf" href="{pdf_href}" download>Download PDF</a>' if pdf_href else ""
    return ('<details class="cite-box">\n  <summary>Cite this paper</summary>\n'
            f'  <p class="cite-plain">{html.escape(plain)}</p>\n'
            f'  <pre class="cite-bib"><code>{html.escape(bibtex)}</code></pre>\n'
            f"  {pdf_link}\n</details>\n")


# --------------------------------------------------------------------------- #
# Markdown helpers
# --------------------------------------------------------------------------- #
_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _slug_re.sub("-", text.lower()).strip("-")


def add_heading_ids(body_html: str):
    toc, seen = [], set()

    def repl(m):
        level, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        text = re.sub(r"<[^>]+>", "", inner).strip()
        base = slugify(text) or "section"
        sid, n = base, 2
        while sid in seen:
            sid, n = f"{base}-{n}", n + 1
        seen.add(sid)
        toc.append({"level": int(level), "text": text, "id": sid})
        return f'<h{level}{attrs} id="{sid}">{inner}</h{level}>'

    return re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body_html, flags=re.S), toc


def render_figures(md: str):
    caps: dict[str, str] = {}

    def repl(m):
        caps[m.group(1)] = m.group(2).strip()
        return f"@@FIGURE_{m.group(1)}@@"

    return re.sub(r"\[\[FIGURE ([A-Za-z0-9]+):\s*(.*?)\]\]", repl, md, flags=re.S), caps


# --------------------------------------------------------------------------- #
# Shared chrome
# --------------------------------------------------------------------------- #
def render_topbar(entries: list[dict], current_slug: str, home_href: str) -> str:
    """Always-visible bar: home link plus a dropdown listing every paper.

    Reachable without opening the contents pane.
    """
    items = []
    for e in entries:
        cls = "tb-item active" if e["slug"] == current_slug else "tb-item"
        cur = ' aria-current="page"' if e["slug"] == current_slug else ""
        sub = (f'<span class="tb-item-sub">{html.escape(e["subtitle"])}</span>'
               if e.get("subtitle") else "")
        items.append(f'<li><a class="{cls}" href="{home_href}{e["slug"]}/"{cur}>'
                     f'<span class="tb-item-title">{html.escape(e["title"])}</span>'
                     f"{sub}</a></li>")
    return ('<div class="topbar">\n'
            f'  <a class="tb-home" href="{home_href}">Papers</a>\n'
            '  <details class="tb-papers">\n'
            f'    <summary>All papers <span class="tb-count">{len(entries)}</span></summary>\n'
            f'    <ul class="tb-list">{"".join(items)}</ul>\n'
            "  </details>\n" + THEME_TOGGLE + "\n</div>")


def render_footer(cfg: dict, home_href: str, license_html: str = "") -> str:
    links = cfg.get("links", {}) or {}
    author = cfg.get("author_display") or cfg.get("author", "")
    icons = []
    for key in ("linkedin", "github", "orcid"):
        url = links.get(key)
        if not url:
            continue
        label = ICON_LABELS[key]
        icons.append(f'<a class="icon-link" href="{url}" title="{label}" aria-label="{label}" '
                     f'rel="me noopener" target="_blank">{ICONS[key]}</a>')
    icon_html = f'<div class="footer-icons">{"".join(icons)}</div>' if icons else ""
    name_html = f'<p class="footer-name">{html.escape(author)}</p>' if author else ""
    home = f'<a class="footer-home" href="{home_href}">All papers</a>' if home_href else ""
    return ('<footer class="site-footer">\n'
            f"  {name_html}\n  {icon_html}\n  {license_html}\n  {home}\n</footer>")


# Set the theme before first paint so there is no flash of the wrong one.
THEME_BOOT = """<script>
(function(){var t;try{t=localStorage.getItem("theme");}catch(e){}
if(!t){t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}
document.documentElement.setAttribute("data-theme",t);})();
</script>"""


DEV_SNIPPET = """
<script>
(function(){ /* live-reload poller, injected by build.py --dev */
  var current = null;
  setInterval(function () {
    fetch('/__buildid', {cache: 'no-store'})
      .then(function (r) { return r.text(); })
      .then(function (id) {
        if (current === null) { current = id; return; }
        if (id !== current) { location.reload(); }
      })
      .catch(function () {});
  }, 700);
})();
</script>
"""


# --------------------------------------------------------------------------- #
# Templates
# --------------------------------------------------------------------------- #
NAV_TMPL = """<button class="nav-toggle" aria-expanded="false" aria-controls="nav-pane" title="Contents">
  <span class="nav-toggle-bars"></span><span class="nav-toggle-label">Contents</span>
</button>
<nav id="nav-pane" class="nav-pane" aria-label="On this page">
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
{theme_boot}
<title>{title}</title>
<meta name="description" content="{description}">
{meta_tags}<link rel="stylesheet" href="../assets/paper.css">
</head>
<body class="has-nav">
{topbar}
{nav}
<article class="wrap">
{body}
{footer}
</article>
<script src="../assets/paper.js" defer></script>
{dev}
</body>
</html>
"""

INDEX_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{theme_boot}
<title>{site_title}</title>
<meta name="description" content="{tagline}">
<link rel="stylesheet" href="assets/paper.css">
</head>
<body class="library">
<article class="wrap">
<header class="lib-header">
  <h1 class="index-head">{site_title}</h1>
  <p class="index-sub">{tagline}</p>
  {theme_toggle}
</header>

{about}

<div class="lib-controls">
  <div class="search-wrap">
    <input id="search" type="search" placeholder="Search papers..."
           autocomplete="off" aria-label="Search papers" />
  </div>
  <div class="row-2">
    <div id="tag-filters" class="tag-filters">{tag_buttons}</div>
    <div class="sort-wrap">
      <label for="sort">Sort</label>
      <select id="sort" aria-label="Sort papers">
        <option value="date-desc">Newest first</option>
        <option value="date-asc">Oldest first</option>
        <option value="title-asc">Title A&ndash;Z</option>
        <option value="title-desc">Title Z&ndash;A</option>
      </select>
    </div>
  </div>
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
{dev}
</body>
</html>
"""


def render_about(cfg: dict) -> str:
    bio = cfg.get("author_bio", "")
    if not bio:
        return ""
    name = cfg.get("author_display") or cfg.get("author", "")
    role = cfg.get("author_role", "")
    portrait = cfg.get("author_portrait", "")
    img = (f'<img class="about-portrait" src="{portrait}" alt="{html.escape(name)}" />'
           if portrait else "")
    role_html = f'<p class="about-role">{html.escape(role)}</p>' if role else ""
    paras = "".join(f"<p>{html.escape(p.strip())}</p>"
                    for p in re.split(r"\n+", bio) if p.strip())
    return ('<section class="about">\n'
            f"  {img}\n"
            '  <div class="about-body">\n'
            f'    <h2 class="about-name">{html.escape(name)}</h2>\n'
            f"    {role_html}\n    {paras}\n  </div>\n</section>")


# --------------------------------------------------------------------------- #
# Paper build
# --------------------------------------------------------------------------- #
def collect_meta(paper_dir: Path, cfg: dict) -> dict:
    meta = load_yaml(paper_dir / "paper.yaml")
    slug = meta.get("slug", paper_dir.name)
    hero = meta.get("hero")
    return {
        "dir": paper_dir,
        "meta": meta,
        "slug": slug,
        "title": meta.get("title", slug),
        "subtitle": meta.get("subtitle", ""),
        "description": meta.get("description", ""),
        "date": str(meta.get("date", "")),
        "status": meta.get("status", "published"),
        "tags": meta.get("tags", []) or [],
        "doi": meta.get("doi", ""),
        "authors": paper_authors(meta, cfg),
        "hero": f"{slug}/{hero}" if hero else "",
    }


def build_paper(entry: dict, cfg: dict, all_entries: list[dict]) -> None:
    paper_dir, meta, slug = entry["dir"], entry["meta"], entry["slug"]
    md_text = (paper_dir / "index.md").read_text()

    figures = meta.get("figures", {}) or {}
    md_text, caps = render_figures(md_text)
    body = markdown.markdown(md_text, extensions=["fenced_code", "tables", "sane_lists"])
    body, toc = add_heading_ids(body)

    for num, rel in figures.items():
        cap = caps.get(str(num), "")
        src = paper_dir / rel
        if str(rel).lower().endswith(".svg") and src.exists():
            # inline it: an <img>-embedded SVG cannot see the page's theme
            # variables, so it would not follow the light/dark toggle
            inner = src.read_text()
            inner = re.sub(r"<\?xml.*?\?>", "", inner, flags=re.S).strip()
            media = f'  <div class="fig-svg">{inner}</div>\n'
        else:
            media = f'  <img src="{rel}" alt="{html.escape(cap, quote=True)}" />\n'
        fig = (f'<figure class="fig" id="figure-{num}">\n{media}'
               f"  <figcaption>Figure {num}. {cap}</figcaption>\n</figure>")
        body = body.replace(f"<p>@@FIGURE_{num}@@</p>", fig).replace(f"@@FIGURE_{num}@@", fig)

    m = re.search(r"(<p>)(<em>.*?</em>)(</p>)", body, re.S)
    if m and m.start() < 400:
        body = body[: m.start()] + '<p class="dek">' + m.group(2)[4:-5] + "</p>" + body[m.end():]

    title = html.escape(entry["title"])
    head = f"<h1>{title}</h1>\n"
    if meta.get("hero"):
        head += ('<figure class="hero">\n'
                 f'  <img src="{meta["hero"]}" alt="{title} illustration" />\n</figure>\n')
    if entry["subtitle"]:
        head += f'<p class="subtitle">{html.escape(entry["subtitle"])}</p>\n'
    head += render_authors(entry["authors"])

    pdf_name = f"{slug}.pdf"
    has_pdf = (paper_dir / pdf_name).exists()
    bits = []
    if entry["date"]:
        bits.append(f'<time class="paper-date">{html.escape(entry["date"])}</time>')
    if entry["doi"]:
        bits.append(render_doi(entry["doi"]))
    if has_pdf:
        bits.append(f'<a class="pdf-chip" href="{pdf_name}" download>PDF</a>')
    if bits:
        head += f'<div class="paper-meta-row">{"".join(bits)}</div>\n'
    if entry["tags"]:
        chips = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in entry["tags"])
        head += f'<div class="tag-row">{chips}</div>\n'
    head += render_cite_block(meta, entry, pdf_name if has_pdf else "")

    toc_items = "\n".join(
        f'<li class="toc-{h["level"]}"><a href="#{h["id"]}">{html.escape(h["text"])}</a></li>'
        for h in toc)

    lic_html = render_license(resolve_license(meta.get("license"), cfg),
                              cfg.get("author", ""), entry["date"][:4])

    meta_tags = f'<meta name="citation_title" content="{title}">\n'
    for a in entry["authors"]:
        meta_tags += (f'<meta name="citation_author" '
                      f'content="{html.escape(cite_name(a.get("name","")))}">\n')
    if entry["date"]:
        meta_tags += f'<meta name="citation_publication_date" content="{entry["date"]}">\n'
    if entry["doi"]:
        meta_tags += f'<meta name="citation_doi" content="{doi_display(entry["doi"])}">\n'
    if has_pdf:
        meta_tags += f'<meta name="citation_pdf_url" content="{pdf_name}">\n'

    page = PAGE_TMPL.format(
        theme_boot=THEME_BOOT,
        title=title,
        description=html.escape(entry["description"][:180], quote=True),
        meta_tags=meta_tags,
        topbar=render_topbar(all_entries, slug, "../"),
        nav=NAV_TMPL.format(items=toc_items),
        body=head + body,
        footer=render_footer(cfg, "../", lic_html),
        dev=DEV_SNIPPET if DEV else "",
    )

    out_dir = SITE / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page)

    if (paper_dir / "images").is_dir():
        shutil.copytree(paper_dir / "images", out_dir / "images", dirs_exist_ok=True)
    if has_pdf:
        shutil.copy(paper_dir / pdf_name, out_dir / pdf_name)


# --------------------------------------------------------------------------- #
# Landing page
# --------------------------------------------------------------------------- #
def build_index(entries: list[dict], cfg: dict) -> None:
    tag_counts: dict[str, int] = {}
    for e in entries:
        for t in e["tags"]:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    all_tags = sorted(tag_counts, key=lambda t: (-tag_counts[t], t))
    tag_buttons = "".join(
        f'<button class="tag-btn" data-tag="{html.escape(t)}">{html.escape(t)}'
        f'<span class="tag-count">{tag_counts[t]}</span></button>' for t in all_tags)

    items = []
    for e in entries:
        sub = f'<p class="paper-sub">{html.escape(e["subtitle"])}</p>' if e["subtitle"] else ""
        desc = f'<p class="paper-desc">{html.escape(e["description"])}</p>' if e["description"] else ""
        who = ", ".join(a.get("name", "") for a in e["authors"])
        who_html = f'<p class="paper-authors">{html.escape(who)}</p>' if who else ""
        bits = []
        if e["date"]:
            bits.append(f"<time>{html.escape(e['date'])}</time>")
        if e["status"] != "published":
            bits.append('<span class="badge-draft">draft</span>')
        if e["doi"]:
            bits.append(render_doi(e["doi"]))
        meta_html = f'<p class="paper-meta">{"".join(bits)}</p>' if bits else ""
        chips = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in e["tags"])
        thumb = (f'<a class="paper-thumb" href="{e["slug"]}/" tabindex="-1" aria-hidden="true">'
                 f'<img src="{e["hero"]}" alt="" loading="lazy" /></a>' if e["hero"] else "")
        items.append(f'<li class="paper-card" data-slug="{e["slug"]}">\n  {thumb}\n'
                     f'  <div class="paper-body">\n'
                     f'    <a class="paper-title" href="{e["slug"]}/">{html.escape(e["title"])}</a>\n'
                     f"    {sub}\n    {who_html}\n    {desc}\n"
                     f'    <div class="tag-row">{chips}</div>\n    {meta_html}\n'
                     f"  </div>\n</li>")

    papers_json = json.dumps([
        {"slug": e["slug"],
         "text": " ".join([e["title"], e["subtitle"], e["description"], " ".join(e["tags"]),
                           " ".join(a.get("name", "") for a in e["authors"])]).lower(),
         "tags": e["tags"],
         "title": e["title"],
         "date": e["date"]} for e in entries])

    (SITE / "index.html").write_text(INDEX_TMPL.format(
        theme_boot=THEME_BOOT,
        site_title=html.escape(cfg.get("title", "Papers")),
        tagline=html.escape(cfg.get("tagline", "")),
        about=render_about(cfg),
        tag_buttons=tag_buttons,
        items="\n".join(items),
        papers_json=papers_json,
        theme_toggle=THEME_TOGGLE,
        footer=render_footer(cfg, "", ""),
        dev=DEV_SNIPPET if DEV else "",
    ))


# --------------------------------------------------------------------------- #
def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(SHARED / "css" / "paper.css", SITE / "assets" / "paper.css")
    shutil.copy(SHARED / "js" / "site.js", SITE / "assets" / "site.js")
    shutil.copy(SHARED / "js" / "paper.js", SITE / "assets" / "paper.js")
    (SITE / ".nojekyll").write_text("")

    cfg = load_site_config()
    entries = [collect_meta(d, cfg) for d in sorted(PAPERS.iterdir())
               if d.is_dir() and (d / "paper.yaml").exists()]
    entries.sort(key=lambda e: (e["status"] != "published", e["date"]), reverse=True)

    for e in entries:
        build_paper(e, cfg, entries)
        extra = f"  doi:{doi_display(e['doi'])}" if e["doi"] else ""
        print(f"built: {e['slug']}{extra}")

    build_index(entries, cfg)
    (SITE / "__buildid").write_text(str(time.time()))
    print(f"index: {len(entries)} paper(s){'  [dev]' if DEV else ''}")
    print(f"output: {SITE}")


if __name__ == "__main__":
    main()

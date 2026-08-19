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
import urllib.parse
from pathlib import Path

import markdown

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required.  pip install -r requirements.txt")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons import CC_ICON, ICONS, ICON_LABELS, THEME_TOGGLE  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
SHARED = ROOT / "shared"
SITE = ROOT / "site"

DEV = "--dev" in sys.argv

# Cache-busting token for static assets (css/js). Recomputed every build so a
# rebuilt stylesheet is never masked by a stale browser cache. Reused as the
# dev-reload __buildid so the two always agree.
ASSET_V = str(time.time())


# --------------------------------------------------------------------------- #
# YAML
# --------------------------------------------------------------------------- #
def load_yaml(path: Path) -> dict:
    """Parse a YAML file. PyYAML is a required dependency; the build must
    see the same parse everywhere, so there is deliberately no fallback.
    """
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


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


# Friendly labels for common places a paper gets shared. Anything else
# falls back to its bare hostname.
KNOWN_SITES = {
    "github.com": "GitHub", "gist.github.com": "GitHub",
    "linkedin.com": "LinkedIn", "substack.com": "Substack",
    "medium.com": "Medium", "x.com": "X", "twitter.com": "X",
    "reddit.com": "Reddit", "news.ycombinator.com": "Hacker News",
    "youtube.com": "YouTube", "bsky.app": "Bluesky",
    "mastodon.social": "Mastodon", "researchgate.net": "ResearchGate",
}


def normalize_discussions(raw) -> list:
    """paper.yaml `discussions:` entries -> [{label, url}, ...].

    Each entry may be a bare URL string, or a {label, url} map when the
    site name alone isn't descriptive enough.
    """
    out = []
    for item in raw or []:
        if isinstance(item, str):
            label, link = "", item.strip()
        elif isinstance(item, dict):
            label, link = str(item.get("label") or "").strip(), str(item.get("url") or "").strip()
        else:
            continue
        if not link:
            continue
        if not label:
            host = urllib.parse.urlsplit(link).netloc.lower().removeprefix("www.")
            base = ".".join(host.rsplit(".", 2)[-2:]) if host.count(".") > 1 else host
            label = KNOWN_SITES.get(host) or KNOWN_SITES.get(base) or host
        out.append({"label": label, "url": link})
    return out


def render_discussions(discussions: list) -> str:
    if not discussions:
        return ""
    links = ", ".join(
        f'<a href="{html.escape(d["url"], quote=True)}" target="_blank" '
        f'rel="noopener">{html.escape(d["label"])}</a>' for d in discussions)
    return f'<p class="discuss-row">Previously discussed on {links}</p>\n'


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
# URLs, link previews, structured data
# --------------------------------------------------------------------------- #
def base_url(cfg: dict) -> str:
    b = (cfg.get("base_url") or "").strip()
    return (b if b.endswith("/") else b + "/") if b else ""


def abs_url(cfg: dict, rel: str) -> str:
    b = base_url(cfg)
    return (b + rel.lstrip("/")) if b else rel


def meta_tag(name: str, content: str, prop: bool = False) -> str:
    if not content:
        return ""
    key = "property" if prop else "name"
    return f'<meta {key}="{name}" content="{html.escape(str(content), quote=True)}">\n'


def render_social(cfg: dict, *, title: str, description: str, url: str,
                  image: str, kind: str = "website", published: str = "",
                  authors: list[dict] | None = None,
                  tags: list[str] | None = None) -> str:
    """Open Graph + Twitter card tags, so shared links preview properly."""
    site_name = cfg.get("title", "")
    out = ""
    out += meta_tag("og:type", "article" if kind == "article" else "website", prop=True)
    out += meta_tag("og:title", title, prop=True)
    out += meta_tag("og:description", description, prop=True)
    out += meta_tag("og:url", url, prop=True)
    out += meta_tag("og:site_name", site_name, prop=True)
    out += meta_tag("og:locale", "en_US", prop=True)
    if image:
        out += meta_tag("og:image", image, prop=True)
        out += meta_tag("og:image:width", "1200", prop=True)
        out += meta_tag("og:image:height", "630", prop=True)
        out += meta_tag("og:image:alt", title, prop=True)
    if kind == "article":
        out += meta_tag("article:published_time", published, prop=True)
        for a in (authors or []):
            out += meta_tag("article:author", a.get("name", ""), prop=True)
        for t in (tags or []):
            out += meta_tag("article:tag", t, prop=True)
    out += meta_tag("twitter:card", "summary_large_image")
    out += meta_tag("twitter:title", title)
    out += meta_tag("twitter:description", description)
    if image:
        out += meta_tag("twitter:image", image)
        out += meta_tag("twitter:image:alt", title)
    handle = (cfg.get("links", {}) or {}).get("twitter_handle", "")
    if handle:
        out += meta_tag("twitter:creator", handle)
        out += meta_tag("twitter:site", handle)
    return out


def person_node(cfg: dict) -> dict:
    links = cfg.get("links", {}) or {}
    same = [v for k, v in links.items() if str(v).startswith("http")]
    node = {"@type": "Person",
            "name": cite_name(cfg.get("author_display") or cfg.get("author", ""))}
    if cfg.get("author_affiliation"):
        node["affiliation"] = {"@type": "Organization",
                               "name": cfg["author_affiliation"]}
    if cfg.get("author_role"):
        node["jobTitle"] = cfg["author_role"]
    if links.get("orcid"):
        node["identifier"] = links["orcid"]
    if same:
        node["sameAs"] = same
    return node


def jsonld(data: dict) -> str:
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")  # never break out of the script tag
    return f'<script type="application/ld+json">\n{payload}\n</script>\n'


def paper_jsonld(cfg: dict, entry: dict, url: str, image: str,
                 lic: tuple | None) -> str:
    authors = []
    for a in entry["authors"]:
        node = {"@type": "Person", "name": cite_name(a.get("name", ""))}
        if a.get("orcid"):
            node["identifier"] = a["orcid"]
        if a.get("affiliation"):
            node["affiliation"] = {"@type": "Organization", "name": a["affiliation"]}
        authors.append(node)

    data = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": entry["title"],
        "name": entry["title"],
        "description": entry["description"],
        "url": url,
        "author": authors,
        "publisher": person_node(cfg),
        "inLanguage": "en",
        "isAccessibleForFree": True,
    }
    if entry["subtitle"]:
        data["alternativeHeadline"] = entry["subtitle"]
    if entry["date"]:
        data["datePublished"] = entry["date"]
    if entry["tags"]:
        data["keywords"] = ", ".join(entry["tags"])
    if entry.get("discussions"):
        data["discussionUrl"] = [d["url"] for d in entry["discussions"]]
    if image:
        data["image"] = image
    if lic and lic[1]:
        data["license"] = lic[1]
    if entry["doi"]:
        data["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI",
                              "value": doi_display(entry["doi"])}
        data["sameAs"] = doi_url(entry["doi"])
    if base_url(cfg):
        data["isPartOf"] = {"@type": "WebSite", "name": cfg.get("title", ""),
                            "url": base_url(cfg)}
    return jsonld(data)


def index_jsonld(cfg: dict, entries: list[dict]) -> str:
    b = base_url(cfg)
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": cfg.get("title", ""),
        "description": cfg.get("tagline", ""),
        "inLanguage": "en",
        "author": person_node(cfg),
        "publisher": person_node(cfg),
    }
    if b:
        data["url"] = b
        data["hasPart"] = [
            {"@type": "ScholarlyArticle", "headline": e["title"],
             "url": abs_url(cfg, f"{e['slug']}/"),
             "datePublished": e["date"]} for e in entries]
    return jsonld(data)


# --------------------------------------------------------------------------- #
# Markdown helpers
# --------------------------------------------------------------------------- #
_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _slug_re.sub("-", text.lower()).strip("-")


def wrap_wide_blocks(body: str) -> str:
    """Let code blocks and tables grow past the text column when the screen
    has room. The .breakout wrapper is fit-content with min-width 100%, so
    narrow content stays column-width and wide content widens up to the
    viewport before falling back to horizontal scroll.

    Code blocks get an inner .code-scroll element to do that scrolling. It has
    to be a separate box from .breakout: .breakout is the positioning context
    for the copy button, and a scroll container cannot also be that without the
    button sliding away with the code. .code-scroll additionally owns the
    rounded clip and the border/background -- those cannot live on .breakout,
    because an element that both clips and carries a transform (.breakout's
    translateX) leaves a nested scroller unscrollable by touch on iOS."""
    body = re.sub(r'(<table class="codehilitetable">.*?</table>)',
                  r'<div class="breakout code-block">'
                  r'<div class="code-scroll">\1</div></div>', body, flags=re.S)
    body = re.sub(r'(<table>.*?</table>)',
                  r'<div class="breakout table-wrap">\1</div>', body, flags=re.S)
    return body


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
# The contents toggle lives inside the top bar so the two can never overlap.
NAV_TOGGLE = ('<button class="nav-toggle" aria-expanded="false" aria-controls="nav-pane" '
              'title="Contents">\n'
              '  <span class="nav-toggle-bars"></span>'
              '<span class="nav-toggle-label">Contents</span>\n'
              "</button>")


def render_topbar(home_href: str) -> str:
    """Always-visible bar: contents toggle, a link home, and the theme switch."""
    return ('<div class="topbar">\n'
            f'  <a class="tb-home" href="{home_href}">'
            '<span class="tb-home-arrow" aria-hidden="true">&larr;</span> Home</a>\n'
            f"  {NAV_TOGGLE}\n"
            + THEME_TOGGLE + "\n</div>")


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
NAV_TMPL = """<nav id="nav-pane" class="nav-pane" aria-label="On this page">
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
<title>{page_title}</title>
<meta name="description" content="{description}">
{canonical}{meta_tags}<link rel="stylesheet" href="../assets/paper.css?v={asset_v}">
<link rel="stylesheet" href="../assets/highlight.css?v={asset_v}">
</head>
<body class="has-nav">
{topbar}
{nav}
<article class="wrap">
{body}
{footer}
</article>
<script src="../assets/paper.js?v={asset_v}" defer></script>
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
{canonical}{meta_tags}<link rel="stylesheet" href="assets/paper.css?v={asset_v}">
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
  <div class="controls-row">
    <div class="search-wrap">
      <input id="search" type="search" placeholder="Search papers..."
             autocomplete="off" aria-label="Search papers" />
    </div>
    <details id="tag-filter" class="tag-filter">
      <summary aria-label="Filter by tag">Filter<span id="filter-count"
        class="filter-count" hidden>0</span></summary>
      <div class="tag-panel">
        <div class="tag-panel-head">
          <span>Filter by tag</span>
          <button type="button" id="tag-clear" class="tag-clear">Clear</button>
        </div>
        <ul class="tag-list">{tag_options}</ul>
      </div>
    </details>
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
<div id="active-tags" class="active-tags"></div>

<p id="result-count" class="result-count"></p>
<ul id="paper-list" class="paper-list">
{items}
</ul>
<p id="empty-state" class="empty-state" hidden>No papers match those filters.</p>
{footer}
</article>

<script>window.__PAPERS__ = {papers_json};</script>
<script src="assets/site.js?v={asset_v}" defer></script>
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
    # `or` fallbacks throughout: a bare `subtitle:` key parses to None, which
    # must behave like an absent key, not crash the build
    return {
        "dir": paper_dir,
        "meta": meta,
        "slug": slug,
        "title": meta.get("title") or slug,
        "subtitle": meta.get("subtitle") or "",
        "description": meta.get("description") or "",
        "date": str(meta.get("date") or ""),
        "status": meta.get("status") or "published",
        "tags": meta.get("tags") or [],
        "doi": meta.get("doi") or "",
        "discussions": normalize_discussions(meta.get("discussions")),
        "authors": paper_authors(meta, cfg),
        "hero": f"{slug}/{hero}" if hero else "",
    }


def build_paper(entry: dict, cfg: dict, all_entries: list[dict]) -> None:
    paper_dir, meta, slug = entry["dir"], entry["meta"], entry["slug"]
    md_text = (paper_dir / "index.md").read_text(encoding="utf-8")

    figures = meta.get("figures", {}) or {}
    # `figure_theme: light` keeps inlined SVGs on their authored light palette
    # in dark mode instead of inverting them; paper.css keys off .fig-light.
    svg_cls = ("fig-svg fig-light"
               if str(meta.get("figure_theme", "")).lower() == "light" else "fig-svg")
    md_text, caps = render_figures(md_text)
    body = markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "sane_lists", "footnotes", "codehilite"],
        extension_configs={"codehilite": {"guess_lang": False, "linenums": True}})
    body = wrap_wide_blocks(body)
    body, toc = add_heading_ids(body)

    for num, rel in figures.items():
        cap = caps.get(str(num), "")
        src = paper_dir / rel
        if str(rel).lower().endswith(".svg") and src.exists():
            # inline it: an <img>-embedded SVG cannot see the page's theme
            # variables, so it would not follow the light/dark toggle
            inner = src.read_text(encoding="utf-8")
            inner = re.sub(r"<\?xml.*?\?>", "", inner, flags=re.S).strip()
            media = f'  <div class="{svg_cls}">{inner}</div>\n'
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
    head += render_discussions(entry["discussions"])
    head += render_cite_block(meta, entry, pdf_name if has_pdf else "")

    toc_items = "\n".join(
        f'<li class="toc-{h["level"]}"><a href="#{h["id"]}">{html.escape(h["text"])}</a></li>'
        for h in toc)

    lic_entry = resolve_license(meta.get("license"), cfg)
    lic_html = render_license(lic_entry, cfg.get("author", ""), entry["date"][:4])

    url = abs_url(cfg, f"{slug}/")
    og_rel = "images/og.png"
    # a relative og:image is useless to a scraper, so only emit it when absolute
    og_abs = (abs_url(cfg, f"{slug}/{og_rel}")
              if base_url(cfg) and (paper_dir / og_rel).exists() else "")
    desc = entry["description"].strip() or entry["subtitle"]

    meta_tags = meta_tag("robots", "index, follow, max-image-preview:large, "
                                   "max-snippet:-1, max-video-preview:-1")
    if entry["authors"]:
        meta_tags += meta_tag("author", cite_name(entry["authors"][0].get("name", "")))
    meta_tags += render_social(cfg, title=entry["title"], description=desc, url=url,
                               image=og_abs, kind="article", published=entry["date"],
                               authors=entry["authors"], tags=entry["tags"])
    meta_tags += paper_jsonld(cfg, entry, url, og_abs, lic_entry)
    meta_tags += f'<meta name="citation_title" content="{title}">\n'
    for a in entry["authors"]:
        meta_tags += (f'<meta name="citation_author" '
                      f'content="{html.escape(cite_name(a.get("name","")))}">\n')
    if entry["date"]:
        meta_tags += f'<meta name="citation_publication_date" content="{entry["date"]}">\n'
    if entry["doi"]:
        meta_tags += f'<meta name="citation_doi" content="{doi_display(entry["doi"])}">\n'
    if has_pdf:
        # Scholar requires an absolute URL here
        meta_tags += meta_tag("citation_pdf_url", abs_url(cfg, f"{slug}/{pdf_name}"))

    site_name = cfg.get("title", "")
    page = PAGE_TMPL.format(
        theme_boot=THEME_BOOT,
        title=title,
        page_title=html.escape(f"{entry['title']} - {site_name}" if site_name else entry["title"]),
        canonical=(f'<link rel="canonical" href="{url}">\n' if url.startswith("http") else ""),
        description=html.escape(entry["description"][:180], quote=True),
        meta_tags=meta_tags,
        topbar=render_topbar("../"),
        nav=NAV_TMPL.format(items=toc_items),
        body=head + body,
        footer=render_footer(cfg, "../", lic_html),
        dev=DEV_SNIPPET if DEV else "",
        asset_v=ASSET_V,
    )

    out_dir = SITE / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")


    if (paper_dir / "images").is_dir():
        shutil.copytree(paper_dir / "images", out_dir / "images", dirs_exist_ok=True)
    # publish the Markdown source: the cleanest form for machine readers
    shutil.copy(paper_dir / "index.md", out_dir / "index.md")
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
    tag_options = "".join(
        '<li><label class="tag-opt">'
        f'<input type="checkbox" value="{html.escape(t, quote=True)}">'
        f'<span class="tag-opt-name">{html.escape(t)}</span>'
        f'<span class="tag-count">{tag_counts[t]}</span>'
        "</label></li>" for t in all_tags)

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
        if e["hero"]:
            thumb = (f'<a class="paper-thumb" href="{e["slug"]}/" tabindex="-1" aria-hidden="true">'
                     f'<img src="{e["hero"]}" alt="" loading="lazy" /></a>')
        else:
            # no hero: keep the grid column occupied so every card's body
            # aligns; show the title's initial as a quiet monogram
            initial = html.escape((e["title"].strip()[:1] or "?").upper())
            thumb = (f'<a class="paper-thumb paper-thumb-empty" href="{e["slug"]}/" '
                     f'tabindex="-1" aria-hidden="true"><span>{initial}</span></a>')
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

    idx_url = abs_url(cfg, "")
    og_abs = (abs_url(cfg, "assets/og-default.png")
              if base_url(cfg) and (SITE / "assets" / "og-default.png").exists() else "")
    idx_meta = meta_tag("robots", "index, follow, max-image-preview:large, max-snippet:-1")
    idx_meta += meta_tag("author", cite_name(cfg.get("author_display") or cfg.get("author", "")))
    idx_meta += render_social(cfg, title=cfg.get("title", ""),
                              description=cfg.get("tagline", ""), url=idx_url,
                              image=og_abs, kind="website")
    idx_meta += index_jsonld(cfg, entries)

    (SITE / "index.html").write_text(INDEX_TMPL.format(
        theme_boot=THEME_BOOT,
        canonical=(f'<link rel="canonical" href="{idx_url}">\n' if idx_url.startswith("http") else ""),
        meta_tags=idx_meta,
        site_title=html.escape(cfg.get("title", "Papers")),
        tagline=html.escape(cfg.get("tagline", "")),
        about=render_about(cfg),
        tag_options=tag_options,
        items="\n".join(items),
        papers_json=papers_json,
        theme_toggle=THEME_TOGGLE,
        footer=render_footer(cfg, "", ""),
        dev=DEV_SNIPPET if DEV else "",
        asset_v=ASSET_V,
    ), encoding="utf-8")



# --------------------------------------------------------------------------- #
# Crawler-facing files
# --------------------------------------------------------------------------- #
AI_CRAWLERS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",
    "ClaudeBot", "Claude-Web", "anthropic-ai",
    "PerplexityBot", "Perplexity-User",
    "Google-Extended", "Applebot-Extended", "meta-externalagent",
    "Bytespider", "CCBot", "cohere-ai", "Diffbot", "Timpibot",
]


def write_robots(cfg: dict, entries: list[dict]) -> None:
    allow_ai = str(cfg.get("allow_ai_crawlers", True)).lower() not in ("false", "no", "0")
    lines = ["# robots.txt", "", "User-agent: *", "Allow: /", ""]
    if allow_ai:
        lines += [
            "# AI and answer-engine crawlers are welcome. These papers are meant to be",
            "# read and cited; see each paper's stated licence for reuse terms.",
        ]
        for ua in AI_CRAWLERS:
            lines += [f"User-agent: {ua}", "Allow: /", ""]
    else:
        lines += ["# Asking AI crawlers not to train on this content.",
                  "# This is an honoured convention, not an enforcement mechanism."]
        for ua in AI_CRAWLERS:
            lines += [f"User-agent: {ua}", "Disallow: /", ""]
    b = base_url(cfg)
    if b:
        lines += [f"Sitemap: {b}sitemap.xml"]
    (SITE / "robots.txt").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")



def write_sitemap(cfg: dict, entries: list[dict]) -> None:
    b = base_url(cfg)
    if not b:
        return
    urls = [(b, max((e["date"] for e in entries), default=""), "weekly", "1.0")]
    for e in entries:
        urls.append((abs_url(cfg, f"{e['slug']}/"), e["date"], "monthly", "0.8"))
    body = "".join(
        "  <url>\n"
        f"    <loc>{html.escape(loc, quote=True)}</loc>\n"
        + (f"    <lastmod>{lastmod}</lastmod>\n" if lastmod else "")
        + f"    <changefreq>{freq}</changefreq>\n"
        f"    <priority>{prio}</priority>\n"
        "  </url>\n"
        for loc, lastmod, freq, prio in urls)
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}</urlset>\n", encoding="utf-8")


def write_llms_txt(cfg: dict, entries: list[dict]) -> None:
    """An llms.txt index (llmstxt.org): a compact, link-rich map of the site
    for language models, pointing at the markdown source of each paper."""
    b = base_url(cfg)
    name = cfg.get("title", "Papers")
    who = cfg.get("author_display") or cfg.get("author", "")
    out = [f"# {name}", ""]
    if cfg.get("tagline"):
        out += [f"> {cfg['tagline']}", ""]
    if cfg.get("author_bio"):
        out += [" ".join(cfg["author_bio"].split()), ""]
    if who:
        out += [f"Author: {who}", ""]
    out += ["Each paper below links to its rendered page and to its Markdown",
            "source, which is the cleanest form to read programmatically.", "",
            "## Papers", ""]
    for e in entries:
        page = abs_url(cfg, f"{e['slug']}/") if b else f"{e['slug']}/"
        md = abs_url(cfg, f"{e['slug']}/index.md") if b else f"{e['slug']}/index.md"
        desc = " ".join(e["description"].split())
        out.append(f"- [{e['title']}]({page}): {desc}")
        bits = []
        if e["date"]:
            bits.append(f"published {e['date']}")
        if e["authors"]:
            bits.append("by " + ", ".join(cite_name(a.get("name", "")) for a in e["authors"]))
        if e["tags"]:
            bits.append("tags: " + ", ".join(e["tags"]))
        if e["doi"]:
            bits.append(f"doi: {doi_display(e['doi'])}")
        if bits:
            out.append(f"  ({'; '.join(bits)})")
        out.append(f"  Markdown source: {md}")
        pdf = f"{e['slug']}/{e['slug']}.pdf"
        if (SITE / pdf).exists():
            out.append(f"  PDF: {abs_url(cfg, pdf) if b else pdf}")
        out.append("")
    lic = cfg.get("default_license")
    if lic:
        resolved = resolve_license(lic, cfg)
        if resolved:
            out += ["## Licence", "",
                    f"Unless a paper states otherwise, content is licensed {resolved[0]}"
                    + (f" ({resolved[1]})" if resolved[1] else "") + ".", ""]
    (SITE / "llms.txt").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")



# --------------------------------------------------------------------------- #
def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(SHARED / "css" / "paper.css", SITE / "assets" / "paper.css")
    shutil.copy(SHARED / "css" / "highlight.css", SITE / "assets" / "highlight.css")
    shutil.copy(SHARED / "js" / "site.js", SITE / "assets" / "site.js")
    shutil.copy(SHARED / "js" / "paper.js", SITE / "assets" / "paper.js")
    og_default = SHARED / "assets" / "og-default.png"
    if og_default.exists():
        shutil.copy(og_default, SITE / "assets" / "og-default.png")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")


    cfg = load_site_config()
    entries = [collect_meta(d, cfg) for d in sorted(PAPERS.iterdir())
               if d.is_dir() and (d / "paper.yaml").exists()]
    # published first (newest first), then drafts (newest first), as the
    # README promises
    entries.sort(key=lambda e: (e["status"] == "published", e["date"]), reverse=True)

    for e in entries:
        build_paper(e, cfg, entries)
        extra = f"  doi:{doi_display(e['doi'])}" if e["doi"] else ""
        print(f"built: {e['slug']}{extra}")

    build_index(entries, cfg)
    write_robots(cfg, entries)
    write_sitemap(cfg, entries)
    write_llms_txt(cfg, entries)
    (SITE / "__buildid").write_text(ASSET_V, encoding="utf-8")

    print(f"index: {len(entries)} paper(s){'  [dev]' if DEV else ''}")
    print(f"output: {SITE}")


if __name__ == "__main__":
    main()

# Papers

A small static site that hosts long-form technical papers and postmortems, one
directory per paper, built to plain HTML and served by GitHub Pages.

## Structure

```
.
├── papers/                         # one directory per paper
│   └── holonic-neural-networks/
│       ├── paper.yaml              # metadata (title, subtitle, date, tags, images)
│       ├── index.md                # the paper body (Markdown)
│       ├── images/                 # hero + figure images (separate files)
│       │   ├── hero.jpeg
│       │   ├── fig1-holon-anatomy.jpeg
│       │   └── ...
│       ├── diagram-prompts.md      # (optional) how the figures were generated
│       └── hero-prompt.md          # (optional)
├── site.yaml                       # site title, tagline, author, links, default license
├── LICENSE                         # MIT, covers the build code only
├── LICENSE-CONTENT.md              # how the papers themselves are licensed
├── shared/
│   ├── css/paper.css               # one stylesheet, linked by every page
│   └── js/
│       ├── site.js                 # landing-page search + tag filtering
│       └── paper.js                # collapsible nav pane + scroll-spy
├── scripts/
│   ├── build.py                    # discovers papers, builds site/
│   ├── serve.py                    # local server + live rebuild on file change
│   ├── make_pdf.py                 # renders each paper to a PDF artifact
│   └── make_review.py              # single self-contained HTML for review/sharing
├── site/                           # build output (git-ignored, CI-generated)
├── requirements.txt                # core build deps
├── requirements-pdf.txt            # extra deps for PDF generation
└── .github/workflows/deploy.yml    # build + deploy to GitHub Pages
```

## Features

- **Library landing page** with client-side **search** (press `/` to focus),
  **tag filtering** (click tags to narrow; multiple tags use AND), and
  **sorting** (newest, oldest, title A-Z / Z-A). All static, no backend.
- **Light and dark themes** with a toggle in the top bar. The choice is
  remembered; until one is made the site follows the OS preference. The theme is
  set before first paint, so there is no flash of the wrong one.
- **Per-paper nav pane**: a collapsible table of contents built from the paper's
  headings, with scroll-spy that highlights the section you're reading. It
  defaults open on wide screens, overlays on mobile, and remembers its state.
- **Tags** surface on both the landing cards and the paper header.
- **PDF artifact per paper**, generated from the same source and used as the
  file you deposit with Zenodo to mint a DOI.
- **DOI support**: once a paper has a DOI, the page grows a DOI chip, a
  "Cite this paper" block with a plain-text citation and BibTeX, and Google
  Scholar `citation_*` metadata.
- **Multiple authors per paper**, with the site owner always ingested as the
  primary author.
- **Author bio** on the landing page.
- **Live rebuild** while editing locally.
- **Footer with profile links** (LinkedIn, GitHub, ORCID) on every page, driven
  by `site.yaml`, rendered as inline SVG icons so they work offline and follow
  the light/dark theme.

To change the author name or links, edit `site.yaml`; nothing else needs
touching.

Icon attribution: the GitHub and ORCID marks come from
[Simple Icons](https://simpleicons.org) (CC0); the LinkedIn mark comes from
[Font Awesome Free](https://fontawesome.com) (icons licensed CC BY 4.0).

## Build locally

```bash
pip install -r requirements.txt
python scripts/build.py          # one-shot build into site/
```

While writing, use the dev server instead. It watches `papers/`, `shared/`,
`scripts/` and `site.yaml`, rebuilds on any change, and the open tab reloads
itself:

```bash
python scripts/serve.py          # http://localhost:8000
python scripts/serve.py 8080     # or pick a port
```

The reload works through a small poller that `build.py --dev` injects, watching
a `/__buildid` endpoint. No websockets and nothing extra to install. A build
error is printed and the last good site keeps serving.

The build regenerates `site/` from scratch each run:

- `site/index.html` — landing page listing every paper (newest first)
- `site/<slug>/index.html` — each paper
- `site/<slug>/images/*` — image assets, copied (not inlined)
- `site/assets/paper.css` — the shared stylesheet

## Add a new paper

1. Create `papers/<your-slug>/`.
2. Add `paper.yaml` (copy an existing one and edit the fields):
   ```yaml
   slug: your-slug
   title: Your Title
   subtitle: An optional secondary line
   description: >
     A sentence or two for the library card and search index.
   date: 2026-08-01
   status: published        # or "draft" (still listed, badged, sorted after)
   tags:                    # power the landing-page filter + paper header
     - some tag
     - another tag
   hero: images/hero.jpeg   # optional
   figures:
     "1": images/fig1.jpeg
   ```
3. Write `index.md`. Reference figures with a marker that carries its caption:
   ```
   [[FIGURE 1: caption text goes here]]
   ```
   Figure keys may be numeric or alphanumeric (`1`, `2`, `A1`). Map each to a
   file in `paper.yaml` under `figures:`.

   Raster figures (JPEG/PNG) are referenced with `<img>`. **SVG figures are
   inlined into the page** so they inherit the theme variables and follow the
   light/dark toggle, which an `<img>`-embedded SVG cannot do. Keep the original
   hex colours in the SVG file: non-browser renderers (WeasyPrint, for the PDF)
   read those, and dark mode is applied over them by CSS in
   `shared/css/paper.css`.
4. Drop the images in `papers/<your-slug>/images/`.
5. Run `python scripts/build.py`. No script edits needed. The paper is added to
   the library index and its tags to the filter bar automatically.

### `index.md` conventions

- The **first italic paragraph** becomes the styled "dek" (standfirst).
- `## Heading` starts a section (a rule + heading is drawn automatically; do
  **not** add `---` separators, they double up).
- Fenced code blocks (```` ``` ````) render as code; keep the language tag.
- Title and subtitle come from `paper.yaml`, not from the Markdown body.

## PDFs and DOIs

Each paper can carry a PDF artifact and a DOI. The PDF is what you deposit with
Zenodo; Zenodo mints the DOI; the DOI goes back into `paper.yaml`.

```bash
pip install -r requirements-pdf.txt      # WeasyPrint (see file for system libs)
python scripts/make_pdf.py               # every paper
python scripts/make_pdf.py <slug>        # just one
```

The PDF is written to `papers/<slug>/<slug>.pdf` so it sits with the source and
is version-controlled, and `build.py` copies it into the built site and links it
from the page. Layout comes from the `@media print` rules in the shared
stylesheet, so the PDF drops the site chrome, paginates figures and code blocks
without splitting them, and numbers its pages.

Then:

1. Upload `papers/<slug>/<slug>.pdf` to [Zenodo](https://zenodo.org) and publish.
2. Copy the DOI into that paper's `paper.yaml`:
   ```yaml
   doi: 10.5281/zenodo.1234567
   ```
3. Rebuild. The paper page gains a DOI chip, a **Cite this paper** block
   (plain-text citation plus BibTeX), and `citation_*` meta tags that Google
   Scholar reads. The landing card shows the DOI too.
4. Optionally re-run `make_pdf.py` so the PDF itself carries the DOI.

Zenodo can also mint a *concept DOI* that always resolves to the newest version,
plus a version DOI per deposit. If you expect to revise a paper, cite the concept
DOI in `paper.yaml`.

## Authors

The primary author comes from `site.yaml` and is **always** the first author of
every paper; you never repeat it per paper. Co-authors go in `paper.yaml`:

```yaml
authors:
  - Grace Hopper                      # bare name
  - name: Ada Lovelace                # or a map
    affiliation: Analytical Engines Ltd
    orcid: https://orcid.org/0000-0002-1825-0097
```

If a paper redundantly lists the primary author (under either the plain or the
display name, with or without an honorific), the duplicate is dropped.

`author_display` is used for bylines, so it can carry a title ("Dr. Zachary
Welz"), while citations and BibTeX use the plain `author` with honorifics
stripped.

## Licensing

This repository is dual-licensed, which is the usual arrangement when code and
writing live together:

- **Code** (`scripts/`, `shared/`, build config) is under the MIT License. See
  [LICENSE](LICENSE).
- **Papers and figures** (`papers/`) are licensed per paper, via a `license:`
  field in that paper's `paper.yaml`. See [LICENSE-CONTENT.md](LICENSE-CONTENT.md)
  for the recognized identifiers and what each permits.

```yaml
# papers/<slug>/paper.yaml
license: CC-BY-4.0        # or CC0-1.0, CC-BY-SA-4.0, CC-BY-NC-4.0, ARR, ...
```

Omit the field and the paper inherits `default_license` from `site.yaml`. For
anything not in the built-in table, supply it explicitly:

```yaml
license:
  name: Some Custom Terms
  url: https://example.com/terms
```

The license renders in the paper's footer with a copyright line and a link.

## Deploy (GitHub Pages)

1. Push to `main`.
2. In the repo: **Settings → Pages → Build and deployment → Source: GitHub
   Actions**.
3. The workflow builds `site/` and publishes it. Your paper is then at
   `https://<user>.github.io/<repo>/<slug>/`.

### Citing / referencing

Each paper lives at a stable path (`/<slug>/`). For a formal citation with a
DOI, deposit the same `index.md` (or a PDF export) on
[Zenodo](https://zenodo.org) and link the DOI from the paper.

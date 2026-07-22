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
│   └── build.py                    # discovers papers, builds site/
├── site/                           # build output (git-ignored, CI-generated)
├── requirements.txt
└── .github/workflows/deploy.yml    # build + deploy to GitHub Pages
```

## Features

- **Library landing page** with client-side **search** (press `/` to focus) and
  **tag filtering** (click tags to narrow; multiple tags use AND). All static,
  no backend.
- **Per-paper nav pane**: a collapsible table of contents built from the paper's
  headings, with scroll-spy that highlights the section you're reading. It
  defaults open on wide screens, overlays on mobile, and remembers its state.
- **Tags** surface on both the landing cards and the paper header.
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
python scripts/build.py
# open site/index.html, or serve it:
python -m http.server -d site 8000
```

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
   Map each figure number to an image file in `paper.yaml` under `figures:`.
4. Drop the images in `papers/<your-slug>/images/`.
5. Run `python scripts/build.py`. No script edits needed. The paper is added to
   the library index and its tags to the filter bar automatically.

### `index.md` conventions

- The **first italic paragraph** becomes the styled "dek" (standfirst).
- `## Heading` starts a section (a rule + heading is drawn automatically; do
  **not** add `---` separators, they double up).
- Fenced code blocks (```` ``` ````) render as code; keep the language tag.
- Title and subtitle come from `paper.yaml`, not from the Markdown body.

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

# Authoring a paper

Everything a paper needs lives in its own folder:

```
papers/<slug>/
├── paper.yaml     # metadata (this file drives everything below)
├── index.md       # the paper body
├── <slug>.pdf     # optional; written by make_pdf.py, committed for Zenodo
└── images/        # hero, figures, og.png
```

The lifecycle, end to end:

```bash
python scripts/new_paper.py my-paper --title "The Title" [--date YYYY-MM-DD]
# write index.md, drop images, fill paper.yaml
python scripts/check.py          # validates; CI runs this, errors block deploy
python scripts/build.py          # builds site/
python scripts/serve.py          # preview at localhost with live rebuild
python scripts/make_og.py my-paper    # social-preview card -> images/og.png
# flip status: draft -> published, commit, push; CI validates, builds, deploys
python scripts/make_pdf.py my-paper   # when you want a Zenodo deposit
# upload the PDF to Zenodo, paste the minted DOI into paper.yaml, push
```

## The paper.yaml fields

| Field | Required | What it does |
|---|---|---|
| `slug` | no | Defaults to the directory name; if present it must match it (`check.py` errors otherwise). Lowercase words joined by hyphens. |
| `title` | yes | The H1 on the paper page, the card title, `<title>`, citation title. |
| `subtitle` | no | Secondary line under the title on the page and card; JSON-LD `alternativeHeadline`. |
| `description` | yes | The card summary, the search index text, the meta description for social previews, and the text on the OG card. One to three sentences. |
| `date` | yes | `YYYY-MM-DD`. Sorts the library, supplies the citation year and sitemap `lastmod`. For imported historical papers this is the original writing or sharing date, not the date it landed here. |
| `status` | no | `published` (default) or `draft`. Drafts are still listed and indexed but carry a badge and sort after all published papers. |
| `license` | no | One of `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `CC-BY-ND-4.0`, `CC-BY-NC-4.0`, `CC-BY-NC-ND-4.0`, `ARR`. Omitted -> `default_license` from `site.yaml`. An unrecognized string renders as bare text with no link (`check.py` warns). |
| `doi` | no | Leave `""` until Zenodo mints one. Accepts `10.x/...`, `doi:10.x/...`, or a full `https://doi.org/...` URL. Once filled: a DOI chip appears on the card and page, the collapsible "Cite this paper" box appears (plain citation + BibTeX + PDF link), and `citation_doi` is emitted for Google Scholar. |
| `authors` | no | Co-authors only; the primary author from `site.yaml` is always first automatically. Each entry is a bare name or a map with `name` / `orcid` / `affiliation`. |
| `tags` | no | Chips on the card and page, the landing-page filter, the search index, JSON-LD keywords. Reuse the existing vocabulary; `check.py` warns when the same tag is spelled differently across papers. |
| `hero` | no | Path relative to the paper folder (e.g. `images/hero.jpeg`). Renders under the title on the page and as the card thumbnail. Without it the card shows a monogram tile so the layout still aligns. |
| `figures` | no | Map of marker key -> image path, e.g. `"1": images/fig1.jpeg`. Keys are alphanumeric (`1`, `2`, `A1`). Every `[[FIGURE key]]` marker in the body must have an entry and every entry must point to an existing file (`check.py` errors); unreferenced entries warn. |
| `discussions` | no | Where the paper was previously shared. Bare URLs get a friendly label from the domain (GitHub, LinkedIn, Substack, ...); use a `label`/`url` map to override. Renders as "Previously discussed on ..." under the tags and emits schema.org `discussionUrl`. `check.py` errors on non-http(s) entries. |

A complete example:

```yaml
slug: my-paper
title: The Title
subtitle: An optional secondary line
description: >
  A sentence or two for the library card and search index.
date: 2026-08-01
status: draft
license: CC-BY-4.0
doi: ""
authors:
  - name: A. Co-Author
    orcid: https://orcid.org/0000-0000-0000-0000
    affiliation: Somewhere
tags:
  - RDF
  - knowledge graphs
hero: images/hero.jpeg
figures:
  "1": images/fig1-short-name.jpeg
  "A1": images/figA1-appendix.svg
discussions:
  - https://www.linkedin.com/posts/...
  - label: Working group thread
    url: https://example.org/thread/42
```

## The index.md conventions

- **No H1.** The title comes from `paper.yaml`. Top-level sections are `##`,
  subsections `###`; both levels are indexed by the collapsible nav pane.
- **Open with one italic paragraph.** It is detected as the dek and styled
  under the title. Without it the page renders fine but loses the dek
  treatment (`check.py` warns).
- **Figures are markers, not image tags:** `[[FIGURE 1: caption text]]` in the
  body, mapped to a file in `paper.yaml`. Raster figures (JPEG/PNG) render as
  `<img>`; **SVG figures are inlined** so they inherit theme variables and
  follow the light/dark toggle. Keep original hex colours inside the SVG:
  WeasyPrint reads those for the PDF, and dark mode is applied over them by
  CSS.
- **Markdown extras enabled:** pipe tables, fenced code blocks, footnotes
  (`[^1]` syntax), sane lists. No math rendering; if a paper ever needs
  equations, KaTeX has to be wired into the build first.
- Keep images web-sized (a few hundred KB); they are committed to git and
  served as-is.

## Publishing, PDFs, and DOIs

Pushing to `main` runs CI: `check.py` (errors block the deploy), then
`build.py`, then deploy to Pages. Flipping `status: draft` to `published`
and pushing is the whole publish step.

PDFs are generated locally, deliberately (CI does not build them):
`python scripts/make_pdf.py <slug>` writes `papers/<slug>/<slug>.pdf` plus a
`.pdf-source.sha256` stamp. Commit both; the committed PDF is the file you
upload to Zenodo. If the paper's source changes after the PDF was rendered,
`check.py` warns that it is stale. After Zenodo mints the DOI, paste it into
`paper.yaml` and push; the DOI chip and citation box appear on the next
build. Note for Windows: WeasyPrint needs the GTK runtime installed.

## What check.py enforces

Errors (fail CI): missing `title`/`date`/`description`; a date that is not
`YYYY-MM-DD`; `slug` not matching the directory; `status` outside
published/draft; `[[FIGURE]]` markers without a `figures:` entry or malformed
markers; `figures:`/`hero` paths that do not exist; missing or empty
`index.md`; duplicate slugs; `discussions` entries without an http(s) URL.

Warnings (printed, non-blocking; `--strict` promotes them): unreferenced
`figures:` entries; unknown `license` identifiers; no italic dek; tag
spelling drift across papers; missing `images/og.png`; a committed PDF whose
source has changed since it was rendered.

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
│   ├── check.py                    # validates every paper; CI runs it before build
│   ├── new_paper.py                # scaffolds a papers/<slug>/ folder
│   ├── serve.py                    # local server + live rebuild on file change
│   ├── make_pdf.py                 # renders each paper to a PDF artifact
│   ├── make_og.py                  # renders 1200x630 link-preview cards
│   └── make_review.py              # single self-contained HTML for review/sharing
├── site/                           # build output (git-ignored, CI-generated)
├── requirements.txt                # core build deps
├── requirements-pdf.txt            # extra deps for PDF generation
└── .github/workflows/deploy.yml    # build + deploy to GitHub Pages
```

## Features

- **Library landing page** with client-side **search** (press `/` to focus), a
  **tag filter** (a dropdown of checkboxes; several tags combine with AND, and
  applied filters show as dismissible chips), and **sorting** (newest, oldest,
  title A-Z / Z-A). All static, no backend. Only the compact control row is
  sticky; the tag list lives in the dropdown so it never occupies the viewport
  while scrolling.
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
- **Link previews**: Open Graph and Twitter card tags on every page, backed by
  a generated 1200x630 preview image per paper.
- **SEO and machine readability**: canonical URLs, JSON-LD structured data,
  `sitemap.xml`, `robots.txt`, an `llms.txt` index, Google Scholar `citation_*`
  tags, and the Markdown source of each paper published alongside its HTML.
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

`python scripts/new_paper.py <your-slug>` scaffolds the folder;
`python scripts/check.py` validates every paper (figure mappings, files,
metadata) and is run by CI before the build, so a broken paper cannot deploy.

**[AUTHORING.md](AUTHORING.md) is the complete reference**: every
`paper.yaml` field and where it surfaces, the `index.md` conventions (dek,
headings, figure markers, SVG inlining, footnotes), the publish -> PDF ->
Zenodo DOI workflow, and exactly what `check.py` enforces. For converting
existing Word or PDF documents into paper folders, see
[INTAKE.md](INTAKE.md).

The short version:

1. `python scripts/new_paper.py your-slug --title "Your Title"`
2. Fill `paper.yaml` (title, date, description at minimum) and write
   `index.md`: one italic opening paragraph as the dek, sections as `##`,
   figures as `[[FIGURE 1: caption]]` markers mapped under `figures:`.
3. Drop images in `papers/your-slug/images/`, then
   `python scripts/check.py && python scripts/build.py` and preview with
   `python scripts/serve.py`. No script edits needed; the library index and
   tag filter update automatically.
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
from the page. `make_pdf.py` also records a `.pdf-source.sha256` stamp next to
the PDF; if the paper's source changes afterwards, `check.py` warns that the
committed PDF is stale. Layout comes from the `@media print` rules in the shared
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

## Link previews and SEO

Set `base_url` in `site.yaml` first. Absolute URLs are required for preview
images, canonical links, and the sitemap; without it those are skipped.

```bash
pip install -r requirements-pdf.txt
python scripts/make_og.py            # site card + one per paper
python scripts/make_og.py <slug>     # just one
```

Cards are written to `papers/<slug>/images/og.png` and
`shared/assets/og-default.png`, and are committed with the source. They are
generated rather than reusing the hero image because preview surfaces (Slack,
LinkedIn, iMessage, Discord) want a 1.91:1 frame with a legible title; a 4:3
hero crops badly, and a paper with no hero would have no preview at all.

Every build then emits:

| What | Why |
| --- | --- |
| `og:*` / `twitter:*` tags | Rich previews when a link is shared. |
| `<link rel="canonical">` | One authoritative URL per page. |
| JSON-LD (`ScholarlyArticle`, `WebSite`, `Person`) | Structured data for search engines and for models that parse pages. Carries authors, ORCID, DOI, licence, and keywords. |
| `citation_*` meta | Google Scholar indexing. |
| `sitemap.xml` | Crawl coverage. |
| `robots.txt` | Crawl policy, including named AI crawlers. |
| `llms.txt` | A compact index for language models ([llmstxt.org](https://llmstxt.org)), linking each paper's Markdown source. |
| `<slug>/index.md` | The Markdown source, served next to the HTML, so a crawler can read clean prose without stripping markup. |

`allow_ai_crawlers` in `site.yaml` toggles whether named AI and answer-engine
crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended and others) are
allowed or asked to stay out. It defaults to allowing them, on the reasoning
that these papers exist to be read and cited. Note that `robots.txt` is an
honoured convention rather than an enforcement mechanism.

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

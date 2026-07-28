# Bringing historical papers into the repo

This is the workflow for converting existing documents (Word files, PDFs) into
tracked `papers/<slug>/` folders. It assumes the papers are your own
unpublished work, so there are no rights questions; licensing is whatever you
set per paper (the default is `CC-BY-4.0` from `site.yaml`).

For the full `paper.yaml` field reference and `index.md` conventions, see
[AUTHORING.md](AUTHORING.md); everything there applies to imported papers
too. What follows is specific to conversion.

## Conventions for historical papers

- **`date` is the original writing or sharing date**, not the date it landed
  here. The library sorts by it and the citation year comes from it, so an old
  paper should sort as old.
- **Start every import as `status: draft`.** The paper is listed and badged but
  sorts after published work. Flip to `published` after a read-through of the
  converted output; conversion artifacts (broken emphasis, mangled tables,
  lost footnote anchors) are common and a draft badge is cheaper than a bad
  page.
- **Link prior sharing locations.** Papers that were posted or discussed
  somewhere (LinkedIn, GitHub, Substack, a working-group thread) should list
  those URLs in `paper.yaml` under `discussions:`; `check.py` validates them.
- **Reuse existing tags before inventing new ones.** `scripts/check.py` warns
  when the same tag is spelled differently across papers.

## Scaffold first

```bash
python scripts/new_paper.py my-old-paper --title "The Real Title" --date 2019-03-14
```

## Converting a Word document

Pandoc does most of the work:

```bash
pandoc source.docx -t gfm --wrap=none \
       --extract-media=papers/my-old-paper \
       -o papers/my-old-paper/index.md
```

`--extract-media` drops embedded images into `papers/my-old-paper/media/`;
move the keepers into `images/`, name them `figN-short-name.<ext>`, and delete
the rest. Then a cleanup pass on the Markdown:

1. Delete the title (and author/date lines) from the body; `paper.yaml` owns
   those.
2. Demote headings so top-level sections are `##` (the nav pane indexes `##`
   and `###`).
3. Make the opening paragraph a single italic paragraph; it renders as the
   dek.
4. Replace inline image references with `[[FIGURE N: caption]]` markers and
   map each `N` to its file in `paper.yaml` under `figures:`.
5. Footnotes survive pandoc as `[^1]` syntax and now render (the build enables
   the `footnotes` extension).
6. Strip Word artifacts: smart-quote escapes, stray `<span>`s, empty bold
   runs, `---` separators (the build draws section rules itself).

## Converting a PDF-only paper

There is no clean automated path; the text layer loses structure and figures
need extracting by hand. What works:

```bash
pip install pymupdf
python - <<'EOF'
import fitz
doc = fitz.open("source.pdf")
print("\n\n".join(page.get_text() for page in doc))   # text, roughly in order
EOF
```

Extract figures either with `fitz` page-image extraction or by screenshotting
at 2x, then reflow the text into Markdown by hand (or paste the extraction
into a Claude session and have it reconstruct headings, paragraphs, and figure
placement for review). Budget a real proofread; PDF extraction silently drops
hyphenation, columns, and superscripts.

## Validate, build, review

```bash
python scripts/check.py      # figure mappings, files, metadata; CI runs this too
python scripts/build.py
python scripts/serve.py      # read the page
python scripts/make_og.py my-old-paper
python scripts/make_pdf.py my-old-paper    # optional until you want a Zenodo deposit
```

`check.py` fails the build on broken figure mappings, missing files, bad
dates, or slug mismatches, and warns on tag drift and stale PDFs, so a
half-converted paper cannot deploy.

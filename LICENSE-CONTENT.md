# Content license

The **software** in this repository (everything under `scripts/` and `shared/`,
plus the build configuration) is licensed under the MIT License. See
[LICENSE](LICENSE).

The **written papers and their figures** under `papers/` are *not* covered by
that MIT license. Each paper carries its own license, declared in its
`paper.yaml`:

```yaml
license: CC-BY-4.0
```

The build renders that license, with a link, in the footer of the paper's page.
If a paper omits the field, it falls back to the `default_license` in
`site.yaml`.

Copyright in each paper remains with the author named in `site.yaml`.

## Choosing a per-paper license

The build recognizes these identifiers. Anything else can be supplied as an
explicit `{name, url}` pair.

| Identifier         | What it permits                                                        |
| ------------------ | ---------------------------------------------------------------------- |
| `CC0-1.0`          | Public domain dedication. Anyone may do anything, no attribution asked. |
| `CC-BY-4.0`        | Any reuse, including commercial and derivatives, **with credit**.       |
| `CC-BY-SA-4.0`     | As above, but derivatives must carry the same license.                  |
| `CC-BY-ND-4.0`     | Redistribution with credit, but **no derivative works**.                |
| `CC-BY-NC-4.0`     | Credit required, **non-commercial** use only.                           |
| `CC-BY-NC-ND-4.0`  | Credit required, non-commercial, no derivatives. Most restrictive CC.   |
| `ARR`              | All rights reserved. No permissions granted beyond fair use/dealing.    |

Notes worth knowing before picking one:

- Creative Commons licenses are **irrevocable** for copies already distributed.
  You can relicense future versions, but you cannot pull back permissions
  already granted for a version someone has.
- `CC-BY-4.0` is the usual choice for work you want **cited and circulated**,
  and is what most open-access publishers and preprint servers use. It is also
  what Zenodo and similar archives expect if you later mint a DOI.
- The `NC` (non-commercial) and `ND` (no-derivatives) variants are *not*
  considered "open" by the Open Definition, and some aggregators and archives
  will decline them. `NC` in particular is vague in practice: what counts as
  commercial use is not crisply defined.
- Choosing `ARR` still lets people read and link to the paper. It just means you
  have granted no reuse rights in advance.

## A note on the figures

The figures in a paper are generated images. Copyright status of AI-generated
imagery is unsettled in several jurisdictions, and in the United States the
Copyright Office has taken the position that material produced without
sufficient human authorship is not protected. Licensing them alongside the paper
is the common practical approach, but the license may not attach to those images
the way it does to the prose. If that distinction matters for a given paper,
say so explicitly in that paper's text.

This file is a description of intent and is not legal advice.

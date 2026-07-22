# Figure generation and provenance

Figures 1 through 4 are notional diagrams generated deterministically by
`scripts/make_figures.py` (edit the script, rerun, rebuild). They use the
site palette: violet marks the proposal (graph mediation, adversary
independence, crystallized structure), muted rust marks the status quo
(context injection), neutrals do everything else.

Figure 5 and the hero require the image-generation agent. The hero prompt is
in `hero-prompt.md`; the Figure 5 prompt follows.

---

**[FIGURE 5 — generation prompt]**

**What it shows:** Handler crystallization: a repeated traversal becoming permanent structure. A conceptual/atmospheric image, not a boxes-and-arrows diagram (Figures 1-4 already cover the diagrammatic register).

**The message:** Deliberate paths, walked repeatedly under a real signal, harden into structure; afterward the path exists on its own and no longer needs the walker. Change that is earned becomes durable (the paper's metanoia thread made visible).

**Composition:** A field of faint, ghostly candidate paths (thin traced lines through a node field, like desire paths across a landscape or ion trails), most fading. One path is shown in three superimposed or sequential states: first faint and wavering, then reinforced, then fully crystallized as a solid faceted/mineral edge (a literal crystal line) connecting its endpoints. Violet (#534AB7) reserved for the crystallized state; the fading candidates in warm greys. Background in the site's warm off-white family. No text. Editorial-technical illustration style consistent with the hero; landscape orientation around 2:1.

**Relation to text:** Sits in Section 4 immediately after the paragraph defining handler crystallization ("Deliberate traversal becomes structure"). The three states of the featured path should visually echo "earned by repetition under a real signal before it is committed to structure."

**File:** replace `images/fig5-crystallization-placeholder.svg` with the generated raster (update `paper.yaml` `figures: "5"` accordingly).

# Figure generation and provenance

> **Current state.** The committed SVGs are hand-authored, not generated.
> `scripts/make_figures.py` produced the earlier generated versions and is
> superseded; it refuses to run unless passed `--force`. The composition notes
> below still describe each figure's intent. The original PNGs remain in
> `images/` — reverting means pointing `paper.yaml` back at them.

## The figure is the figure, not a section of the paper

Each SVG carries **only the diagram**. No eyebrow, no headline, no standfirst,
no closing sentence. `build.py` already wraps every figure in
`<figcaption>Figure N. …</figcaption>` drawn from the `[[FIGURE N: …]]` marker,
and the body text around it makes the argument. An earlier revision put all of
that inside the SVG, which read as "text section + figure + caption" and, worse,
consumed so much canvas that the diagrams had to be stacked vertically to fit.
Removing the chrome is what buys back both the landscape format and the space
for the spatial composition to work.

## Format and sizing

Figures are **not** given the `.breakout` class in `scripts/build.py`, so they
render inside the article measure — about **764 px** wide. Canvases are
1200 px on a **2:1-ish landscape** aspect (520–640 px tall), which displays at
roughly 0.64× and keeps prominent labels near 14 px on screen.

Landscape is not just a look here: it is what lets each figure keep its spatial
argument — fan-out in Figure 1, convergence in Figure 2, containment in
Figures 3 and 6, left-to-right flow in Figures 4 and 5. Where content will not
fit at a readable size, cut the content rather than the format.

---

## The superseded generator

The earlier versions were generated deterministically by `scripts/make_figures.py`
(edit the script, rerun, rebuild). The script builds on the
`technical-diagram-design` skill's `dsl.py`: real font metrics, the two-pass
type-fit solve, and `check.py` surface validation. It therefore needs the skill
present at `.claude/skills/technical-diagram-design/` and Inter installed as
`~/.fonts/Inter-{400,500,600,700}.ttf`.

```bash
python papers/holonic-graph-composition/scripts/make_figures.py        # SVG
python papers/holonic-graph-composition/scripts/make_figures.py --png  # + PNG
```

SVG is the committed artifact: the site inlines it so it follows the light/dark
toggle, and WeasyPrint reads the same file for the PDF. `--png` writes rasters
alongside it for visual review only — delete them before committing.

## Palette

The figures use the site's figure tokens (`--f-*` in `shared/css/paper.css`) so
the inlined SVG follows the light/dark toggle, extended with the MID and DARK
surface registers the design system needs. Colour is semantic and consistent
across the set:

| Register | Means | Where |
|---|---|---|
| Amber | the status quo and its failure modes | Figures 1–2 |
| Indigo / navy | holonic structure and governance | Figures 3–6 |
| Teal | governed output — projections, downstream consumers | Figures 3, 5, 6 |
| Neutral | everything else | all |

Nothing else is coloured. Each figure carries a legend where it uses more than
two connector types or three surface roles.

---

## Figure 1 — Default graph divergence

**What it shows:** one dataset and one bare-pattern query, evaluated by three
quad stores, returning three different row counts.

**The message:** the SPARQL specification does not fix default-graph semantics,
so "just union the graphs" is not portably available as a default behaviour.

**Composition:** Source → Generated Views (Composition 1). The given — the
query plus the two named graphs it does not mention — is the single dark
PrimaryCard and the diagram's entry point. Three peer store cards sit in one
container beneath it: each carries its configuration, its resulting default
graph, and a result chip. The result chips are where the divergence lands, so
they carry the amber accent; everything else stays neutral. A closing
annotation states the cause rather than restating the picture.

**Relation to text:** Problem 1. The caption's claim is the three different row
counts, so the row counts must be the most findable thing after the query.

---

## Figure 2 — SERVICE variable scoping

**What it shows:** an engine issuing two SERVICE calls, the left endpoint
binding two employees, the right endpoint evaluating independently over 50,000,
and the join degenerating into a 100,000-row cross-product.

**The message:** SPARQL 1.1 says implementations *should* push bindings into a
SERVICE block, not that they must; when they do not, the client pays for the
cross-product and gets no validation, provenance, or governance with it.

**Composition:** convergence into one result (Composition 6, inputs → outcome).
The two endpoints are peers in one container. The binding that fails to cross
is drawn once, as a single amber dashed connector between the endpoints,
labelled with what does not happen — not as an arrow into anything, because
nothing arrives. The cross-product card is the emphasised surface and the
diagram's entry point; the three things it lacks sit inside it as a chip set,
since they are an unordered set of absences.

**Relation to text:** Problem 2. The `SHOULD` is the hinge of the argument and
belongs on the connector it qualifies, not in a floating aside.

---

## Figure 3 — The four-graph holon

**What it shows:** one holon's four named-graph layers — interior, boundary,
projection, context — each with the question it answers and the RDF it holds.

**The message:** a holon is not a bag of triples; it is four graphs with four
distinct jobs, and the boundary is what makes the other three governable.

**Composition:** Layered Architecture (Composition 2), *not* concentric
nesting. The original drew the four layers as four nested rectangles, which is
four surfaces deep — past the three-level depth budget — and spent most of the
canvas on the padding between rings. Four bands inside one holon boundary say
the same thing, hold their content at a readable size, and let each layer carry
its own artifacts. The boundary band takes the accent as the emphasised layer,
since the paper's reframing rests on it; the other three stay neutral.

**Relation to text:** "The Holonic Approach". Each band's descriptor is the
question from the body text, kept verbatim so the figure and the prose agree.

---

## Figure 4 — Portal traversal

**What it shows:** one portal traversal from the HR holon to the Directory
holon: CONSTRUCT translates, SHACL validates, PROV-O records.

**The message:** a graph-to-graph data movement is a governed, three-step
operation with a defined source contract and a defined target contract, not an
opaque copy.

**Composition:** Digital Thread (Composition 5). A single spine runs
left to right through three stage cards; the source and target holons are the
domains at either end, each spanning its end of the thread. The stage set is
the emphasised region — it is what the figure is about — and the portal
definition is shown living in the source holon's boundary, which is where the
paper says it lives.

**Relation to text:** "Portals: Governed Graph-to-Graph Data Flow". This figure
is the zoom-in; Figure 5 is the zoom-out, and the two share the stage
vocabulary so the relationship reads without a caption.

---

## Figure 5 — Three-holon pipeline

**What it shows:** HR (CCO) → Directory (Schema.org) → Analytics, with two
portals, two vocabulary translations, two boundary validations, and a
provenance chain that reaches back to the origin.

**The message:** composition across systems is a sequence of bounded governed
movements, each of which is the operation Figure 4 describes.

**Composition:** Digital Thread (Composition 5) at the scale above Figure 4.
Three holon containers on one unbroken spine, two portal nodes on the spine
between them. Each portal carries the same translate / validate / record
triple as a compact chip set rather than restating it in prose. The provenance
chain is a single dotted connector spanning all three holons beneath the spine
— one relationship drawn once — rather than a per-holon annotation.

**Relation to text:** "Worked Example: Three-Holon Pipeline". Analytics is the
end of the thread and takes the teal output register.

---

## Figure 6 — A VKG wrapped as a holon

**What it shows:** PostgreSQL and an Ontop VKG outside the holon boundary,
supplying a virtual interior; the boundary, projection, and context layers
inside it doing the governance the VKG stack has no native place for.

**The message:** holonic wraps existing infrastructure rather than replacing
it. The interior is virtual; the governance is real.

**Composition:** System Boundary (Composition 3). The external stack sits on
the canvas outside the boundary — deliberate exteriority, so those cards are
uncontained and take MID rather than white. Inside, the four layers reuse
Figure 3's vocabulary exactly, so a reader who has parsed Figure 3 parses this
one for free; only the interior's descriptor changes, to say that it is
populated by query rather than by assertion. The SHACL boundary's role as a
regression test for the R2RML mapping is the claim the section rests on, so it
is the one annotated item.

**Relation to text:** "Federation and Virtualization Still Fit". The context
layer's inventory (endpoint, mapping version, backing store, steward,
classification) is compressed to a chip set: it is a list, and a reader parses
a list as one object.

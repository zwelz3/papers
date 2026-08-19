#!/usr/bin/env python3
"""Generate the SVG figures for "Graph Composition Within the RDF Technologies
Ecosystem: A Holonic Approach".

Built on the technical-diagram-design skill's `dsl.py`, so the figures get real
font metrics, the two-pass type-fit solve, and `check.py` surface validation
rather than hand-placed coordinates.

    python papers/holonic-graph-composition/scripts/make_figures.py [--png]

Requires the skill at .claude/skills/technical-diagram-design/ and Inter at
~/.fonts/Inter-{400,500,600,700}.ttf. Rationale for each figure's composition
is in ../diagram-prompts.md.

Colour is semantic and consistent across the set: amber marks the status quo
and its failure modes (Figures 1-2), indigo/navy marks holonic structure
(Figures 3-6), teal marks governed output. Hexes come from the site's figure
tokens in shared/css/paper.css wherever one exists, so the inlined SVG follows
the light/dark toggle.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SKILL = ROOT / ".claude/skills/technical-diagram-design/scripts"
if not SKILL.exists():                                  # pragma: no cover
    sys.exit(f"technical-diagram-design skill not found at {SKILL}")
sys.path.insert(0, str(SKILL))

from dsl import (C, RATIO, Canvas, Doc, Surfaces, check_content_shape,  # noqa: E402
                 contrast_ratio, lstar, measure, solve, wrap)

OUT = pathlib.Path(__file__).resolve().parent.parent / "images"

# ---------------------------------------------------------------- palette
# Tokens marked (site) already have a dark-mode mapping in shared/css/paper.css;
# the rest were added there alongside this script.
P = dict(
    bg="#FAFBFC",           # canvas
    surface="#fff",         # (site) LIGHT card
    mid="#DDE2EA",          # MID neutral
    mid_blue="#DCE3EE",     # MID, holonic structure
    mid_portal="#C9D6EA",   # MID, the portal: the focal region of figs 4-5
    mid_teal="#D3E5DF",     # MID, governed output
    mid_amber="#ECE0C7",    # MID, the status quo
    mid_deep="#C6CEDD",     # MID at depth: chips and uncontained cards
    chip_blue="#C4D0E4",    # MID at depth, holonic
    chip_teal="#C1D9D1",    # MID at depth, output
    navy="#14233A",         # DARK, one surface per figure
    ink="#141E27",          # (site) primary text
    text="#1f3448",         # (site) primary text, softer
    mut="#54626E",          # (site) secondary text
    mut2="#6b7785",         # (site) micro text
    line="#CAD4DC",         # (site) hairline
    indigo="#3B47A0",       # (site) accent: holonic
    teal="#0E7C86",         # (site) accent: output
    amber="#8a5410",        # (site) accent: status quo
    e_blue="#93A8C4",       # edges, named per (child, parent) pair
    e_neutral="#A6AFBE",
    e_deep="#8B98AE",
    e_amber="#C0A268",
    e_teal="#93BFB2",
    n1="#F2F6FC",           # text on navy
    n2="#B7C7DE",
)

# Cross-figure semantic assignment, stated once.
FLOW, GOVERN, PROV = P["indigo"], P["amber"], P["mut2"]


# ------------------------------------------------------------------ helpers
def head(d, S, cv, eyebrow, title, lead):
    """Title block. Returns the y at which the body starts."""
    M = cv.margin
    d.text(M, M + S["eyebrow"], eyebrow, S["eyebrow"], P["indigo"], 700,
           ls=0.16 * S["eyebrow"])
    ty = M + S["eyebrow"] + S["major"] * 1.45
    d.text(M, ty, title, S["major"], P["ink"], 700, avail=cv.w - 2 * M)
    h = d.wtext(M, ty + S["sub"] * 2.3, lead, S["sub"] * 1.11, P["mut"],
                avail=min(cv.w - 2 * M, cv.w * 0.72))
    return ty + S["sub"] * 2.3 + h + cv.group_gap * 0.85


def finish(d, cv, top, y_end):
    """Declare the body and constrain it to the canvas.

    Without this the solver has no vertical bound: it grows the type until a
    horizontal constraint binds and the body runs off the bottom edge.
    """
    d.fits(cv.h - cv.margin * 0.75 - top, y_end - top)
    d.set_body(cv.margin, top, cv.w - cv.margin, y_end)


def note(d, S, x, y, s, avail, fill=None):
    """A closing annotation. Subordinate: one line, muted, no surface."""
    return d.wtext(x, y, s, S["sub"], fill or P["mut"], avail=avail, maxlines=2)


def head_h(S, w, pad, eyebrow, title, sub):
    """Height a container header occupies, including the gap to what follows.
    Must stay in step with draw_head or the descriptor collides with the first
    card."""
    av = w - 2 * pad
    h = pad
    if eyebrow:
        h += S["eyebrow"] * 1.05
    tl, _ = wrap(title, S["group"], 700, av, 2)
    h += S["group"] * (1.28 + 1.22 * (len(tl) - 1))
    if sub:
        sl, _ = wrap(sub, S["sub"], 400, av, 2)
        h += S["sub"] * (1.15 + 1.34 * (len(sl) - 1))
    return h + S["sub"] * 0.42 + pad * 0.75


def draw_head(d, S, x, y, w, pad, eyebrow, title, sub, accent,
              ink=None, mut=None, anchor="start"):
    """Container header: eyebrow, title, optional descriptor."""
    ink, mut = ink or P["ink"], mut or P["mut"]
    av = w - 2 * pad
    tx = x + pad if anchor == "start" else x + w / 2
    cy = y + pad
    if eyebrow:
        cy += S["eyebrow"] * 1.05
        d.text(tx, cy, eyebrow, S["eyebrow"], accent, 700,
               ls=0.16 * S["eyebrow"], anchor=anchor, avail=av)
    tl, _ = wrap(title, S["group"], 700, av, 2)
    cy += S["group"] * 1.28
    for i, ln in enumerate(tl):
        d.text(tx, cy + i * S["group"] * 1.22, ln, S["group"], ink, 700,
               anchor=anchor, avail=av)
    cy += S["group"] * 1.22 * (len(tl) - 1)
    if sub:
        cy += S["sub"] * 1.15
        sl, _ = wrap(sub, S["sub"], 400, av, 2)
        for i, ln in enumerate(sl):
            d.text(tx, cy + i * S["sub"] * 1.34, ln, S["sub"], mut,
                   anchor=anchor, avail=av)
        cy += S["sub"] * 1.34 * (len(sl) - 1)
    return cy - y + pad * 0.45


# --------------------------------------------------------------------- card
def card_h(S, cards, cw, pad):
    """One height for a peer set, taken from the tallest member."""
    worst = 0.0
    av = cw - 2 * pad
    for c in cards:
        h = pad
        if c.get("eyebrow"):
            h += S["eyebrow"] * 1.45
        tl, _ = wrap(c["title"], S["card"], 700, av, 2)
        h += S["card"] * (1.02 + 1.28 * (len(tl) - 1))
        if c.get("sub"):
            sl, _ = wrap(c["sub"], S["sub"], 400, av, 2)
            h += S["sub"] * (1.35 + 1.34 * (len(sl) - 1))
        for ln in c.get("lines", ()):
            wl, _ = wrap(ln, S["sub"], 500, av, 2)
            h += S["sub"] * (1.30 + 1.34 * (len(wl) - 1))
        if c.get("chip"):
            h += S["chip"] * 2.55
        worst = max(worst, h + pad + S["sub"] * 0.3)
    return worst


def draw_card(d, S, x, y, w, h, c, pad, fill=None, stroke=None, ink=None,
              mut=None, accent=None, chip_fill=None, chip_edge=None,
              chip_ink=None, radius=16, dash=None, sw=1.25, shadow=False):
    fill = fill or P["surface"]
    stroke = stroke or P["e_neutral"]
    ink, mut = ink or P["ink"], mut or P["mut"]
    av = w - 2 * pad
    d.rect(x, y, w, h, r=radius, fill=fill, stroke=stroke, sw=sw, dash=dash,
           filt="card" if shadow else None)
    cy = y + pad
    if c.get("eyebrow"):
        cy += S["eyebrow"] * 0.95
        d.text(x + pad, cy, c["eyebrow"], S["eyebrow"], accent or P["indigo"],
               700, ls=0.15 * S["eyebrow"], avail=av)
        cy += S["eyebrow"] * 0.5
    tl, _ = wrap(c["title"], S["card"], 700, av, 2)
    cy += S["card"] * 1.02
    for i, ln in enumerate(tl):
        d.text(x + pad, cy + i * S["card"] * 1.28, ln, S["card"], ink, 700,
               avail=av)
    cy += S["card"] * 1.28 * (len(tl) - 1)
    if c.get("sub"):
        sl, _ = wrap(c["sub"], S["sub"], 400, av, 2)
        cy += S["sub"] * 1.35
        for i, ln in enumerate(sl):
            d.text(x + pad, cy + i * S["sub"] * 1.34, ln, S["sub"], mut,
                   avail=av)
        cy += S["sub"] * 1.34 * (len(sl) - 1)
    for ln in c.get("lines", ()):
        wl, _ = wrap(ln, S["sub"], 500, av, 2)
        cy += S["sub"] * 1.30
        for i, l2 in enumerate(wl):
            d.text(x + pad, cy + i * S["sub"] * 1.34, l2, S["sub"],
                   c.get("line_ink", mut), 500, avail=av)
        cy += S["sub"] * 1.34 * (len(wl) - 1)
    if c.get("chip"):
        label = c["chip"]
        chh = S["chip"] * 1.85
        chw = measure(label, S["chip"], 700) + S["chip"] * 1.7
        cyy = y + h - pad - chh
        d.rect(x + pad, cyy, chw, chh, r=11, fill=chip_fill or P["mid_deep"],
               stroke=chip_edge or P["e_deep"], sw=1)
        d.text(x + pad + chw / 2, cyy + chh / 2 + S["chip"] * 0.35, label,
               S["chip"], chip_ink or P["ink"], 700, anchor="middle",
               avail=chw - 6)
        d.fits(av, chw)


CHIP_STRETCH = 1.60     # a chip is an atomic surface; it sizes to its label


def chip_row(d, S, x, y, w, labels, fill, edge, ink, gap=None):
    """A set, not a sequence: one row, no arrows, read in any order.

    The row is justified to its measure so the set reads as one object, but a
    chip is atomic and will not stretch past CHIP_STRETCH of its own label.
    Slack beyond that goes to the gaps, and what is left stays as whitespace.
    """
    gap = gap if gap is not None else S["chip"] * 0.85
    h = S["chip"] * 1.9
    n = len(labels)
    nat = [measure(l, S["chip"], 600) + S["chip"] * 1.65 for l in labels]
    total = sum(nat) + gap * (n - 1)
    d.fits(w, total)
    slack = max(0.0, w - total)
    grow = min(slack, sum(nat) * (CHIP_STRETCH - 1)) / n if n else 0
    slack -= grow * n
    if n > 1:
        gap += min(slack / (n - 1), gap * 0.6)
    cx = x
    for l, nw in zip(labels, nat):
        cw = nw + grow
        d.rect(cx, y, cw, h, r=11, fill=fill, stroke=edge, sw=1)
        d.text(cx + cw / 2, y + h / 2 + S["chip"] * 0.35, l, S["chip"], ink,
               600, anchor="middle")
        cx += cw + gap
    return h


def legend(d, S, x, y, entries, ink=None):
    """One declarative row, in the same tokens the body uses. Sized to its
    content: dsl's divides the width evenly, which collides on long labels."""
    ink = ink or P["mut"]
    size = S["eyebrow"]
    cx = x
    for kind, label in entries:
        sw = size * 2.2
        if kind == "flow":
            d.arrow(cx, y, cx + sw, y, color=FLOW, w=2.0)
        elif kind == "blocked":
            dashed(d, cx, y, cx + sw, y, P["amber"], 2.0, "6 4")
        elif kind == "prov":
            d.dotted(cx, y, cx + sw, y)
        else:
            fill, edge = kind
            d.rect(cx, y - size * 0.58, sw, size * 1.2, r=6, fill=fill,
                   stroke=edge, sw=1)
        d.text(cx + sw + size * 0.7, y + size * 0.36, label, size, ink)
        cx += sw + size * 0.7 + measure(label, size, 400) + size * 2.0
    d.fits(d.cv.w - 2 * d.cv.margin, cx - x)
    return size * 1.4


def spine(d, x1, y1, x2, y2, color=None, w=2.4):
    d.add(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke='
          f'"{color or FLOW}" stroke-width="{w}" fill="none" '
          f'stroke-linecap="round"/>')


def dashed(d, x1, y1, x2, y2, color, w=2.0, da="7 5"):
    d.add(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{color}" '
          f'stroke-width="{w}" fill="none" stroke-dasharray="{da}" '
          f'stroke-linecap="round"/>')


# ===================================================================== FIG 1
F1_STORES = [
    dict(title="Fuseki", sub="union mode",
         lines=["tdb2:unionDefaultGraph true",
                "default graph = union of A and B"], chip="8 rows"),
    dict(title="GraphDB", sub="empty by default",
         lines=["no union configured",
                "default graph = empty"], chip="0 rows"),
    dict(title="Stardog", sub="configurable",
         lines=["query.all.graphs = ?",
                "default graph = deployment choice"], chip="0 or 8 rows"),
]


def fig1(cv):
    M, PAD, GAP, GG = cv.margin, cv.pad, cv.card_gap, cv.group_gap

    def build(k):
        S = {r: RATIO[r] * cv.r * k for r in RATIO}
        d = Doc(cv, S)
        d.rect(0, 0, cv.w, cv.h, r=0, fill=P["bg"])
        top = head(d, S, cv, "PROBLEM 1 · DEFAULT GRAPH",
                   "One dataset, one query, three answers",
                   "The same bare triple pattern over the same two named "
                   "graphs, evaluated by three quad stores.")
        usable = cv.w - 2 * M

        # --- the given: the diagram's authoritative source, so it is DARK
        gw = usable * 0.60
        gx = M + (usable - gw) / 2
        gpad = round(PAD * 0.92)
        qh = head_h(S, gw, gpad, "THE GIVEN · IDENTICAL IN ALL THREE",
                    "SELECT * WHERE { ?s ?p ?o }",
                    "A bare triple pattern — no GRAPH clause")
        chh = S["chip"] * 1.9
        gh = qh + chh + gpad
        d.rect(gx, top, gw, gh, r=22, fill=P["navy"], stroke="none",
               filt="band")
        draw_head(d, S, gx, top, gw, gpad,
                  "THE GIVEN · IDENTICAL IN ALL THREE",
                  "SELECT * WHERE { ?s ?p ?o }",
                  "A bare triple pattern — no GRAPH clause",
                  P["n2"], ink=P["n1"], mut=P["n2"], anchor="middle")
        chip_row(d, S, gx + gpad, top + qh, gw - 2 * gpad,
                 ["Graph A · 3 triples", "Graph B · 5 triples"],
                 P["mid_blue"], P["e_blue"], P["ink"])

        # --- one relationship, drawn once: a stub, a spine, three ticks
        cw = (usable - 2 * GAP * 1.6) / 3
        cx = [M + i * (cw + GAP * 1.6) for i in range(3)]
        sp_y = top + gh + GG * 0.52
        row_y = sp_y + GG * 0.48
        spine(d, gx + gw / 2, top + gh, gx + gw / 2, sp_y, FLOW, 2.2)
        spine(d, cx[0] + cw / 2, sp_y, cx[2] + cw / 2, sp_y, FLOW, 2.2)
        for x in cx:
            d.arrow(x + cw / 2, sp_y, x + cw / 2, row_y - 2, color=FLOW, w=2.2)

        ch = card_h(S, F1_STORES, cw, PAD * 0.85)
        for x, c in zip(cx, F1_STORES):
            draw_card(d, S, x, row_y, cw, ch, c, PAD * 0.85,
                      fill=P["surface"], stroke=P["e_neutral"],
                      chip_fill=P["mid_amber"], chip_edge=P["e_amber"],
                      chip_ink=P["amber"], shadow=True)

        ny = row_y + ch + GG * 0.62
        nh = note(d, S, M, ny,
                  "SPARQL 1.1 does not fix default-graph semantics, so the "
                  "same query is portable only when every graph it reads is "
                  "named explicitly.", usable * 0.86)
        finish(d, cv, top, ny + nh)
        return d, S
    return build


# ===================================================================== FIG 2
F2_ENDPOINTS = [
    dict(eyebrow="LEFT OF THE JOIN", title="HR endpoint",
         sub="cco:Person, cco:has_text_value",
         lines=["Binds ?person → 2 employees",
                "Binds ?email for each"]),
    dict(eyebrow="RIGHT OF THE JOIN", title="Directory endpoint",
         sub="schema:Person, schema:email",
         lines=["Evaluates independently",
                "Returns all 50,000 entries"]),
]


def fig2(cv):
    M, PAD, GAP, GG = cv.margin, cv.pad, cv.card_gap, cv.group_gap

    def build(k):
        S = {r: RATIO[r] * cv.r * k for r in RATIO}
        d = Doc(cv, S)
        d.rect(0, 0, cv.w, cv.h, r=0, fill=P["bg"])
        top = head(d, S, cv, "PROBLEM 2 · SERVICE SCOPING",
                   "Bindings that never cross the boundary",
                   "SPARQL 1.1 says an implementation SHOULD push bindings "
                   "into a SERVICE block. When it does not, the join becomes "
                   "a cross-product.")
        usable = cv.w - 2 * M

        # --- the engine: the one authoritative surface
        ew = usable * 0.52
        ex = M + (usable - ew) / 2
        epad = round(PAD * 0.9)
        eh = head_h(S, ew, epad, "ONE FEDERATED QUERY",
                    "SELECT ?person ?name ?dept",
                    "Two SERVICE blocks, evaluated apart") + epad * 0.2
        d.rect(ex, top, ew, eh, r=22, fill=P["navy"], stroke="none",
               filt="band")
        draw_head(d, S, ex, top, ew, epad, "ONE FEDERATED QUERY",
                  "SELECT ?person ?name ?dept",
                  "Two SERVICE blocks, evaluated apart",
                  P["n2"], ink=P["n1"], mut=P["n2"], anchor="middle")

        # --- the two endpoints, peers in one container
        gpad = round(PAD * 0.85)
        gy = top + eh + GG * 0.72
        gut = max(GAP * 3.0, measure("?person not pushed", S["eyebrow"], 700)
                  + S["eyebrow"] * 2.4)
        cw = (usable - 2 * gpad - gut) / 2
        ch = card_h(S, F2_ENDPOINTS, cw, PAD * 0.8)
        gh = ch + 2 * gpad
        d.rect(M, gy, usable, gh, r=24, fill=P["mid"], stroke=P["e_neutral"],
               sw=1.25)
        exs = [M + gpad, M + gpad + cw + gut]
        for x, c in zip(exs, F2_ENDPOINTS):
            draw_card(d, S, x, gy + gpad, cw, ch, c, PAD * 0.8,
                      fill=P["surface"], stroke=P["e_neutral"],
                      accent=P["mut2"], shadow=True)

        # the binding that does not cross: drawn once, in the gutter it fails
        by = gy + gpad + ch * 0.62
        dashed(d, exs[0] + cw + GAP * 0.7, by, exs[1] - GAP * 0.7, by,
               P["amber"], 2.0, "7 5")
        d.text(M + usable / 2, by - S["eyebrow"] * 0.75, "?person not pushed",
               S["eyebrow"], P["amber"], 700, anchor="middle", avail=gut)
        d.text(M + usable / 2, by + S["eyebrow"] * 1.55,
               'the spec says SHOULD', S["eyebrow"], P["mut2"],
               anchor="middle", avail=gut)

        # --- what arrives: the emphasised surface, and a single card
        ry = gy + gh + GG * 0.62
        rw = usable * 0.78
        rx = M + (usable - rw) / 2
        rpad = round(PAD * 0.9)
        rhh = head_h(S, rw, rpad, "WHAT THE CLIENT RECEIVES",
                     "2 × 50,000 = 100,000 candidate rows",
                     "Filtered client-side to the two that matter")
        chh = S["chip"] * 1.9
        rh = rhh + chh + rpad
        for x in exs:
            d.arrow(x + cw / 2, gy + gh, x + cw / 2, ry - 2, color=FLOW,
                    w=2.2)
        d.rect(rx, ry, rw, rh, r=22, fill=P["mid_amber"], stroke=P["e_amber"],
               sw=1.25)
        draw_head(d, S, rx, ry, rw, rpad, "WHAT THE CLIENT RECEIVES",
                  "2 × 50,000 = 100,000 candidate rows",
                  "Filtered client-side to the two that matter",
                  P["amber"], anchor="middle")
        chip_row(d, S, rx + rpad, ry + rhh, rw - 2 * rpad,
                 ["No validation", "No provenance", "No governance"],
                 P["surface"], P["e_amber"], P["amber"])

        ly = ry + rh + GG * 0.58
        lh = legend(d, S, M, ly, [("flow", "Result flow"),
                                  ("blocked", "Binding that is not pushed")])
        finish(d, cv, top, ly + lh)
        return d, S
    return build


# ===================================================================== FIG 3
F3_LAYERS = [
    dict(eyebrow="INTERIOR", title="What is true inside",
         sub="A-Box triples. One holon may hold several interior graphs, "
             "unioned within its own scope.",
         chips=["urn:holon:x/interior/people",
                "urn:holon:x/interior/payroll"]),
    dict(eyebrow="BOUNDARY", title="What is allowed to cross",
         sub="SHACL shapes plus the portal definitions that govern every "
             "inter-holon movement.",
         chips=["sh:NodeShape", "sh:targetClass", "cga:Portal",
                "cga:constructQuery"], focal=True),
    dict(eyebrow="PROJECTION", title="What outsiders are shown",
         sub="A CONSTRUCT-derived or filtered view, never the interior "
             "itself.",
         chips=["CONSTRUCT view", "LPG / visualisation output"], tone="teal"),
    dict(eyebrow="CONTEXT", title="Where it belongs, and what happened",
         sub="PROV-O activities, temporal annotation, membership, "
             "stewardship.",
         chips=["prov:Activity", "prov:wasDerivedFrom",
                "cga:dataClassification"]),
]


def band_h(S, layers, w, pad):
    worst = 0.0
    av = w - 2 * pad
    for l in layers:
        h = pad + S["eyebrow"] * 1.05
        tl, _ = wrap(l["title"], S["card"] * 1.06, 700, av, 2)
        h += S["card"] * 1.06 * (1.14 + 1.26 * (len(tl) - 1))
        sl, _ = wrap(l["sub"], S["sub"], 400, av, 2)
        h += S["sub"] * (1.30 + 1.34 * (len(sl) - 1))
        h += S["chip"] * 1.9 + S["chip"] * 0.95 + pad
        worst = max(worst, h)
    return worst


def draw_band(d, S, x, y, w, h, l, pad):
    tone = l.get("tone")
    accent = {"teal": P["teal"]}.get(tone, P["indigo"] if l.get("focal")
                                     else P["mut2"])
    chip_fill = {"teal": P["chip_teal"]}.get(
        tone, P["chip_blue"] if l.get("focal") else P["mid_deep"])
    chip_edge = {"teal": P["e_teal"]}.get(
        tone, P["e_blue"] if l.get("focal") else P["e_deep"])
    d.rect(x, y, w, h, r=16, fill=P["surface"],
           stroke=P["e_blue"] if l.get("focal") else P["e_neutral"],
           sw=1.5 if l.get("focal") else 1.0, filt="card")
    if l.get("focal"):                       # emphasis by hue, not by register
        d.add(f'<path d="M{x + 1.5:.1f} {y + 16:.1f} V{y + h - 16:.1f}" '
              f'stroke="{P["indigo"]}" stroke-width="3" '
              f'stroke-linecap="round"/>')
    av = w - 2 * pad
    cy = y + pad + S["eyebrow"] * 1.05
    d.text(x + pad, cy, l["eyebrow"], S["eyebrow"], accent, 700,
           ls=0.17 * S["eyebrow"], avail=av)
    ts = S["card"] * 1.06
    tl, _ = wrap(l["title"], ts, 700, av, 2)
    cy += ts * 1.14
    for i, ln in enumerate(tl):
        d.text(x + pad, cy + i * ts * 1.26, ln, ts, P["ink"], 700, avail=av)
    cy += ts * 1.26 * (len(tl) - 1)
    sl, _ = wrap(l["sub"], S["sub"], 400, av, 2)
    cy += S["sub"] * 1.30
    for i, ln in enumerate(sl):
        d.text(x + pad, cy + i * S["sub"] * 1.34, ln, S["sub"], P["mut"],
               avail=av)
    cy += S["sub"] * 1.34 * (len(sl) - 1)
    chip_row(d, S, x + pad, y + h - pad - S["chip"] * 1.9, av, l["chips"],
             chip_fill, chip_edge, P["ink"])


def fig3(cv):
    M, PAD, GAP, GG = cv.margin, cv.pad, cv.card_gap, cv.group_gap

    def build(k):
        S = {r: RATIO[r] * cv.r * k for r in RATIO}
        d = Doc(cv, S)
        d.rect(0, 0, cv.w, cv.h, r=0, fill=P["bg"])
        top = head(d, S, cv, "THE HOLONIC APPROACH",
                   "One holon, four named graphs",
                   "Each layer answers one question, and the boundary is what "
                   "makes the other three governable.")
        usable = cv.w - 2 * M
        gpad = round(PAD * 0.9)
        hh = head_h(S, usable, gpad, "HOLON",
                    "urn:holon:x — a cga:Holon",
                    "One IRI threads through all four layers; each layer is "
                    "an ordinary named graph.")
        bpad = round(PAD * 0.78)
        bw = usable - 2 * gpad
        bh = band_h(S, F3_LAYERS, bw, bpad)
        gh = hh + len(F3_LAYERS) * bh + (len(F3_LAYERS) - 1) * GAP + gpad
        d.rect(M, top, usable, gh, r=26, fill=P["mid"], stroke=P["e_neutral"],
               sw=1.25)
        draw_head(d, S, M, top, usable, gpad, "HOLON",
                  "urn:holon:x — a cga:Holon",
                  "One IRI threads through all four layers; each layer is an "
                  "ordinary named graph.", P["indigo"])
        for i, l in enumerate(F3_LAYERS):
            draw_band(d, S, M + gpad, top + hh + i * (bh + GAP), bw, bh, l,
                      bpad)

        ly = top + gh + GG * 0.55
        lh = legend(d, S, M, ly,
                    [((P["surface"], P["e_neutral"]), "Named-graph layer"),
                     ((P["chip_blue"], P["e_blue"]), "The governing layer"),
                     ((P["chip_teal"], P["e_teal"]), "Governed output")])
        finish(d, cv, top, ly + lh)
        return d, S
    return build


# ===================================================================== FIG 4
F4_SOURCE = dict(
    eyebrow="SOURCE HOLON", title="HR Records", sub="urn:holon:hr",
    cards=[dict(eyebrow="INTERIOR", title="CCO-vocabulary triples",
                sub="cco:Person · cco:DesignativeName · "
                    "cco:OccupationRole"),
           dict(eyebrow="BOUNDARY", title="The portal definition lives here",
                sub="cga:constructQuery — a stored CONSTRUCT")])
F4_TARGET = dict(
    eyebrow="TARGET HOLON", title="Company Directory",
    sub="urn:holon:directory",
    cards=[dict(eyebrow="INTERIOR", title="Schema.org triples, injected",
                sub="schema:Person · schema:name · schema:email"),
           dict(eyebrow="CONTEXT", title="prov:Activity recorded",
                sub="prov:used · prov:generated · "
                    "prov:wasAssociatedWith")])
F4_STAGES = [
    dict(title="Translate", sub="The portal's CONSTRUCT rewrites CCO into "
                                "Schema.org."),
    dict(title="Validate", sub="The target's SHACL shapes accept or reject "
                               "the result."),
    dict(title="Record", sub="A prov:Activity lands in the target's context "
                             "graph."),
]


def fig4(cv):
    M, PAD, GAP, GG = cv.margin, cv.pad, cv.card_gap, cv.group_gap

    def build(k):
        S = {r: RATIO[r] * cv.r * k for r in RATIO}
        d = Doc(cv, S)
        d.rect(0, 0, cv.w, cv.h, r=0, fill=P["bg"])
        top = head(d, S, cv, "PORTALS",
                   "One traversal: translate, validate, record",
                   "A portal is a first-class RDF entity in the source "
                   "holon's boundary graph. Traversing it is three governed "
                   "steps, not a copy.")
        usable = cv.w - 2 * M
        gpad = round(PAD * 0.82)
        cpad = round(PAD * 0.72)

        dw = usable * 0.265                      # the two domain containers
        gut = GG * 0.72
        mw = usable - 2 * dw - 2 * gut           # the stage set between them

        def dom_h(dom, w):
            hh = head_h(S, w, gpad, dom["eyebrow"], dom["title"], dom["sub"])
            ch = card_h(S, dom["cards"], w - 2 * gpad, cpad)
            return hh + 2 * ch + GAP + gpad, hh, ch

        h_s, hh_s, ch_s = dom_h(F4_SOURCE, dw)
        h_t, hh_t, ch_t = dom_h(F4_TARGET, dw)
        hh = max(hh_s, hh_t)
        ch = max(ch_s, ch_t)
        dh = hh + 2 * ch + GAP + gpad            # peers share top and bottom

        spad = round(PAD * 0.82)
        shh = head_h(S, mw, spad, "PORTAL TRAVERSAL",
                     "cga:TransformPortal", None)
        stage_w = mw - 2 * spad
        sch = card_h(S, F4_STAGES, stage_w, cpad)
        need = shh + 3 * sch + 2 * GAP * 1.35 + spad
        mh = max(dh, need)

        # domains
        for x, dom in ((M, F4_SOURCE), (M + dw + gut + mw + gut, F4_TARGET)):
            d.rect(x, top, dw, dh, r=24, fill=P["mid"], stroke=P["e_neutral"],
                   sw=1.25)
            draw_head(d, S, x, top, dw, gpad, dom["eyebrow"], dom["title"],
                      dom["sub"], P["indigo"])
            for i, c in enumerate(dom["cards"]):
                draw_card(d, S, x + gpad, top + hh + i * (ch + GAP),
                          dw - 2 * gpad, ch, c, cpad, accent=P["mut2"],
                          shadow=True)

        # the stage set: the emphasised region, one tier richer
        mx = M + dw + gut
        d.rect(mx, top, mw, mh, r=24, fill=P["mid_portal"], stroke=P["e_blue"],
               sw=1.5)
        draw_head(d, S, mx, top, mw, spad, "PORTAL TRAVERSAL",
                  "cga:TransformPortal", None, P["indigo"], mut=P["text"],
                  anchor="middle")
        gap_s = (mh - shh - spad - 3 * sch) / 2
        sy = []
        for i, c in enumerate(F4_STAGES):
            y = top + shh + i * (sch + gap_s)
            sy.append((y, y + sch))
            draw_card(d, S, mx + spad, y, stage_w, sch, c, cpad,
                      fill=P["surface"], stroke=P["e_blue"], shadow=True)
            d.text(mx + mw - spad - S["chip"] * 0.2,
                   y + cpad + S["chip"] * 1.05, str(i + 1), S["chip"],
                   P["e_blue"], 700, anchor="end")
        for i in range(2):
            d.arrow(mx + mw / 2, sy[i][1], mx + mw / 2, sy[i + 1][0] - 2,
                    color=FLOW, w=2.2)

        # the spine crosses the gutters
        mid_y = top + hh + ch + GAP / 2
        d.arrow(M + dw, mid_y, mx - 2, mid_y, color=FLOW, w=2.4)
        d.arrow(mx + mw, mid_y, M + dw + gut + mw + gut - 2, mid_y,
                color=FLOW, w=2.4)

        ny = top + max(dh, mh) + GG * 0.58
        nh = note(d, S, M, ny,
                  "Each traversal reads only the source holon's interior "
                  "graphs — a small local union, never the enterprise "
                  "graph.", usable * 0.8)
        finish(d, cv, top, ny + nh)
        return d, S
    return build


# ===================================================================== FIG 5
F5_HOLONS = [
    dict(eyebrow="HOLON 1 · CCO", title="HR Records", sub="urn:holon:hr",
         cards=[dict(title="Interior", sub="cco:Person, cco:OccupationRole"),
                dict(title="Boundary", sub="Portal → Directory")]),
    dict(eyebrow="HOLON 2 · SCHEMA.ORG", title="Company Directory",
         sub="urn:holon:directory",
         cards=[dict(title="Interior", sub="schema:Person, schema:email"),
                dict(title="Boundary",
                     sub="PersonShape: name + email required")]),
    dict(eyebrow="HOLON 3 · SCHEMA.ORG", title="Analytics Warehouse",
         sub="urn:holon:analytics", tone="teal",
         cards=[dict(title="Interior", sub="Fully derived, nothing asserted"),
                dict(title="Boundary",
                     sub="AnalyticsShape: name + jobTitle required")]),
]
F5_PORTALS = [
    dict(title="CCO → Schema.org", sub="Vocabulary translation"),
    dict(title="Pass-through", sub="Already translated; forwarded"),
]


def fig5(cv):
    M, PAD, GAP, GG = cv.margin, cv.pad, cv.card_gap, cv.group_gap

    def build(k):
        S = {r: RATIO[r] * cv.r * k for r in RATIO}
        d = Doc(cv, S)
        d.rect(0, 0, cv.w, cv.h, r=0, fill=P["bg"])
        top = head(d, S, cv, "WORKED EXAMPLE",
                   "Two portals, two contracts, one provenance chain",
                   "Employee data reaches Analytics through two governed "
                   "movements. Every step is bounded, validated and recorded.")
        usable = cv.w - 2 * M
        gpad = round(PAD * 0.78)
        cpad = round(PAD * 0.66)

        pw = usable * 0.153                       # portal nodes on the spine
        gut = GAP * 1.25
        hw = (usable - 2 * pw - 4 * gut) / 3

        hh = max(head_h(S, hw, gpad, h["eyebrow"], h["title"], h["sub"])
                 for h in F5_HOLONS)
        ch = max(card_h(S, h["cards"], hw - 2 * gpad, cpad) for h in F5_HOLONS)
        gh = hh + 2 * ch + GAP + gpad

        ppad = round(PAD * 0.6)
        phh = max(head_h(S, pw, ppad, "PORTAL", p["title"], p["sub"])
                  for p in F5_PORTALS)
        stages = ["Translate", "Validate", "Record"]
        stage_h = S["chip"] * 1.85
        ph = phh + 3 * stage_h + 2 * GAP * 0.42 + ppad

        xs, px = [], []
        x = M
        for i in range(3):
            xs.append(x)
            x += hw + gut
            if i < 2:
                px.append(x)
                x += pw + gut

        for hx, h in zip(xs, F5_HOLONS):
            teal = h.get("tone") == "teal"
            d.rect(hx, top, hw, gh, r=22,
                   fill=P["mid_teal"] if teal else P["mid"],
                   stroke=P["e_teal"] if teal else P["e_neutral"], sw=1.25)
            draw_head(d, S, hx, top, hw, gpad, h["eyebrow"], h["title"],
                      h["sub"], P["teal"] if teal else P["indigo"])
            for i, c in enumerate(h["cards"]):
                draw_card(d, S, hx + gpad, top + hh + i * (ch + GAP),
                          hw - 2 * gpad, ch, c, cpad,
                          stroke=P["e_teal"] if teal else P["e_neutral"],
                          shadow=True)

        py = top + (gh - ph) / 2
        mid_y = top + gh / 2
        for pxx, p in zip(px, F5_PORTALS):
            d.rect(pxx, py, pw, ph, r=18, fill=P["mid_portal"],
                   stroke=P["e_blue"], sw=1.5, filt="card")
            draw_head(d, S, pxx, py, pw, ppad, "PORTAL", p["title"], p["sub"],
                      P["indigo"], mut=P["text"], anchor="middle")
            sy = py + phh
            for i, st in enumerate(stages):
                yy = sy + i * (stage_h + GAP * 0.42)
                d.rect(pxx + ppad, yy, pw - 2 * ppad, stage_h, r=10,
                       fill=P["surface"], stroke=P["e_blue"], sw=1)
                d.text(pxx + pw / 2, yy + stage_h / 2 + S["chip"] * 0.35,
                       f"{i + 1}  {st}", S["chip"], P["ink"], 600,
                       anchor="middle", avail=pw - 2 * ppad - 8)
        for i in range(2):
            d.arrow(xs[i] + hw, mid_y, px[i] - 2, mid_y, color=FLOW, w=2.4)
            d.arrow(px[i] + pw, mid_y, xs[i + 1] - 2, mid_y, color=FLOW, w=2.4)

        # one relationship, drawn once: provenance reaches back to the origin
        prov_y = top + gh + GG * 0.42
        for hx in (xs[0] + hw / 2, xs[1] + hw / 2, xs[2] + hw / 2):
            d.dotted(hx, top + gh, hx, prov_y)
        d.dotted(xs[0] + hw / 2, prov_y, xs[2] + hw / 2, prov_y)
        d.text(xs[2] + hw / 2, prov_y + S["eyebrow"] * 1.75,
               "prov:wasDerivedFrom — back to urn:holon:hr",
               S["eyebrow"], P["mut"], anchor="end", avail=usable * 0.6)

        ly = prov_y + S["eyebrow"] * 3.2
        lh = legend(d, S, M, ly,
                    [("flow", "Portal traversal"),
                     ("prov", "Provenance chain"),
                     ((P["mid_teal"], P["e_teal"]), "End of the thread")])
        finish(d, cv, top, ly + lh)
        return d, S
    return build


# ===================================================================== FIG 6
F6_EXTERNAL = [
    dict(eyebrow="RELATIONAL SOURCE", title="PostgreSQL",
         sub="employees · projects · departments"),
    dict(eyebrow="VIRTUALIZATION LAYER", title="Ontop VKG",
         sub="SPARQL → SQL over R2RML mappings v3.2",
         lines=["ontop.internal:8080/sparql"]),
]
F6_LAYERS = [
    dict(eyebrow="INTERIOR · VIRTUAL", title="Populated by query, "
                                                  "not by assertion",
         sub="A materialised snapshot, or a backend that routes SPARQL "
             "straight to the VKG endpoint.",
         chips=["schema:Person", "schema:Organization", "schema:worksFor"]),
    dict(eyebrow="BOUNDARY", title="A SHACL contract for the VKG output",
         sub="Which doubles as a regression test: a PostgreSQL schema change "
             "that breaks the R2RML mapping fails validation here.",
         chips=["VkgEmployeeShape", "VkgOrganizationShape"], focal=True),
    dict(eyebrow="PROJECTION", title="A non-PII subset for consumers",
         sub="Name and department only; no SSN, no salary.",
         chips=["schema:name", "schema:department", "Portal → Analytics"],
         tone="teal"),
    dict(eyebrow="CONTEXT", title="What the infrastructure is, and who owns "
                                  "it",
         sub="The provenance the VKG stack has no native place to record.",
         chips=["endpointUrl", "R2RML v3.2", "pg-prod (v2024.11)",
                "dataSteward", "cga:Internal"]),
]


def fig6(cv):
    M, PAD, GAP, GG = cv.margin, cv.pad, cv.card_gap, cv.group_gap

    def build(k):
        S = {r: RATIO[r] * cv.r * k for r in RATIO}
        d = Doc(cv, S)
        d.rect(0, 0, cv.w, cv.h, r=0, fill=P["bg"])
        top = head(d, S, cv, "FEDERATION AND VIRTUALIZATION",
                   "A virtual knowledge graph, wrapped as a holon",
                   "Holonic does not displace the existing stack. The "
                   "interior stays virtual; the governance layers are real.")
        usable = cv.w - 2 * M
        ew = usable * 0.245
        gut = max(GG * 0.68, measure("CONSTRUCT", S["eyebrow"], 700) * 1.35)
        bw = usable - ew - gut
        gpad = round(PAD * 0.88)
        bpad = round(PAD * 0.72)

        hh = head_h(S, bw, gpad, "HOLON · ENG-VKG",
                    "urn:holon:eng-vkg — a cga:DataHolon",
                    "The wrapper adds the boundary contract, the provenance "
                    "and the classification the VKG lacks natively.")
        lw = bw - 2 * gpad
        lh = band_h(S, F6_LAYERS, lw, bpad)
        gh = hh + 4 * lh + 3 * GAP + gpad

        bx = M + ew + gut
        d.rect(bx, top, bw, gh, r=26, fill=P["mid"], stroke=P["e_neutral"],
               sw=1.25)
        draw_head(d, S, bx, top, bw, gpad, "HOLON · ENG-VKG",
                  "urn:holon:eng-vkg — a cga:DataHolon",
                  "The wrapper adds the boundary contract, the provenance and "
                  "the classification the VKG lacks natively.", P["indigo"])
        for i, l in enumerate(F6_LAYERS):
            draw_band(d, S, bx + gpad, top + hh + i * (lh + GAP), lw, lh, l,
                      bpad)

        # deliberate exteriority: uncontained cards, so they cannot be white.
        # The stack is shorter than the holon; centre it against the boundary
        # rather than leaving a column of dead space beneath it.
        eh = card_h(S, F6_EXTERNAL, ew, PAD * 0.78)
        e_gap = GAP * 2.4
        block = S["eyebrow"] * 1.9 + 2 * eh + e_gap
        ey = top + max(0, (gh - block) / 2) + S["eyebrow"] * 1.9
        d.text(M, ey - S["eyebrow"] * 0.9, "OUTSIDE THE HOLON", S["eyebrow"],
               P["mut2"], 700, ls=0.16 * S["eyebrow"], avail=ew)
        for i, c in enumerate(F6_EXTERNAL):
            y = ey + i * (eh + e_gap)
            draw_card(d, S, M, y, ew, eh, c, PAD * 0.78, fill=P["mid_deep"],
                      stroke=P["e_deep"], accent=P["mut"],
                      mut=P["text"], sw=1.0)
            if i == 0:
                d.arrow(M + ew / 2, y + eh, M + ew / 2, y + eh + e_gap - 2,
                        color=P["mut2"], w=2.2)
                d.text(M + ew / 2 + S["eyebrow"] * 0.6,
                       y + eh + e_gap * 0.5 + S["eyebrow"] * 0.35,
                       "SQL", S["eyebrow"], P["mut2"], avail=ew / 2)
        # the one connector that crosses the boundary, from the VKG that
        # populates the interior into the interior itself
        iy = top + hh + lh / 2
        oy = ey + eh + e_gap + eh / 2
        d.arrow(M + ew, oy, bx - 2, iy, color=FLOW, w=2.4)
        d.text(M + ew + gut / 2, (oy + iy) / 2 - S["eyebrow"] * 0.75,
               "CONSTRUCT", S["eyebrow"], P["indigo"], 700, anchor="middle",
               avail=gut)

        ly = top + gh + GG * 0.52
        lh = legend(d, S, M, ly,
                    [((P["mid_deep"], P["e_deep"]), "External system"),
                     ((P["surface"], P["e_neutral"]), "Named-graph layer"),
                     ((P["chip_blue"], P["e_blue"]), "The governing layer"),
                     ((P["chip_teal"], P["e_teal"]), "Governed output")])
        finish(d, cv, top, ly + lh)
        return d, S
    return build


# ------------------------------------------------------------------ surfaces
def surfaces() -> Surfaces:
    """The surface tree shared by the set, declared for check.py."""
    s = Surfaces()
    s.canvas("canvas", P["bg"])
    s.container("given (dark primary)", P["navy"], "canvas")
    s.emphasis("given (dark primary)")
    s.fill_only("chip on navy", P["mid_blue"], "given (dark primary)",
                glyph=P["ink"])
    s.container("group", P["mid"], "canvas", border=P["e_neutral"],
                weight=1.25, text=P["ink"])
    s.container("portal group", P["mid_portal"], "canvas", border=P["e_blue"],
                weight=1.5, text=P["ink"])
    s.container("stage card", P["surface"], "portal group", border=P["e_blue"],
                weight=1.25, text=P["ink"])
    s.container("output group", P["mid_teal"], "canvas", border=P["e_teal"],
                weight=1.25, text=P["ink"])
    s.container("result (amber)", P["mid_amber"], "canvas", border=P["e_amber"],
                weight=1.25, text=P["ink"])
    s.container("card", P["surface"], "group", border=P["e_neutral"],
                weight=1.25, text=P["ink"])
    s.container("band", P["surface"], "group", border=P["e_blue"], weight=1.5,
                text=P["ink"])
    s.fill_only("chip on band", P["mid_deep"], "band", glyph=P["ink"])
    s.fill_only("chip on band (blue)", P["chip_blue"], "band", glyph=P["ink"])
    s.fill_only("chip on band (teal)", P["chip_teal"], "band", glyph=P["ink"])
    s.container("external card", P["mid_deep"], "canvas", border=P["e_deep"],
                weight=1.0, text=P["ink"])
    s.fill_only("chip on navy well", P["mid_blue"], "given (dark primary)",
                glyph=P["ink"])
    return s


def contrast_report():
    """Text against the surface behind it, per SKILL.md 2.2."""
    pairs = [
        ("mut on canvas", P["mut"], P["bg"]), ("mut on white", P["mut"], P["surface"]),
        ("mut on mid", P["mut"], P["mid"]), ("mut on mid_blue", P["mut"], P["mid_blue"]),
        ("mut on mid_amber", P["mut"], P["mid_amber"]),
        ("mut2 on canvas", P["mut2"], P["bg"]), ("mut2 on mid", P["mut2"], P["mid"]),
        ("mut2 on mid_deep", P["mut2"], P["mid_deep"]),
        ("indigo on mid", P["indigo"], P["mid"]),
        ("indigo on mid_blue", P["indigo"], P["mid_blue"]),
        ("teal on mid_teal", P["teal"], P["mid_teal"]),
        ("amber on mid_amber", P["amber"], P["mid_amber"]),
        ("amber on white", P["amber"], P["surface"]),
        ("n1 on navy", P["n1"], P["navy"]), ("n2 on navy", P["n2"], P["navy"]),
    ]
    bad = []
    for name, fg, bgc in pairs:
        r = contrast_ratio(fg, bgc)
        if r < 4.5:
            bad.append(f"  {name}: {r:.2f}:1")
    for line in bad:
        print("  WARN contrast under 4.5:1" + line)
    return not bad


FIGURES = [
    ("fig1-default-graph-divergence", fig1, (1620, 800)),
    ("fig2-service-scoping", fig2, (1620, 1000)),
    ("fig3-four-graph-holon", fig3, (1520, 1400)),
    ("fig4-portal-traversal", fig4, (1560, 830)),
    ("fig5-three-holon-pipeline", fig5, (1540, 780)),
    ("fig6-vkg-holon", fig6, (1720, 1440)),
]


def main() -> None:
    # SUPERSEDED. The committed SVGs in ../images are hand-authored: they were
    # rebuilt at a canvas sized to the ~764px text column the site actually
    # renders figures in, and figures 4-6 were restructured from side-by-side
    # columns into vertical progressions, which this script does not do.
    # Running it would overwrite that work, so it refuses unless forced.
    png = "--png" in sys.argv
    if not {"--force", "--out"} & set(sys.argv):
        existing = sorted(p.name for p in OUT.glob("fig*.svg"))
        if existing:
            sys.exit(
                "refusing to overwrite the hand-authored figures:\n  "
                + "\n  ".join(existing)
                + "\n\nThis generator is superseded (see ../diagram-prompts.md).\n"
                  "Pass --force to regenerate anyway.")
    surfaces().report()
    contrast_report()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn, (w, h) in FIGURES:
        cv = Canvas(w, h)
        print(f"{name}: {cv}")
        doc, sizes, k = solve(fn(cv), fit="balanced")
        for msg in check_content_shape(cv, doc.body):
            print(f"  NOTE {msg}")
        if doc.body[3] > cv.h - cv.margin * 0.4:
            print(f"  FAIL body runs to y={doc.body[3]:.0f} on a {cv.h}px "
                  f"canvas: grow the canvas or cut content")
        path = OUT / f"{name}.svg"
        path.write_text(doc.svg(), encoding="utf-8")
        print(f"  -> {path.relative_to(ROOT)}")
        if png:
            subprocess.run(
                ["node", str(pathlib.Path(__file__).parent / "render_png.js"),
                 str(OUT / f"{name}.png"), str(path), "1600"],
                check=True, env={**__import__("os").environ,
                                 "RESVG_PATH": "/tmp/fontsetup/node_modules/"
                                               "@resvg/resvg-js"})


if __name__ == "__main__":
    main()

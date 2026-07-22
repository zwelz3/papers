#!/usr/bin/env python3
"""Generate the SVG figures for "Structure Substitutes for Scale".

Figures 1-4 are notional diagrams generated deterministically here so they can
be edited in code and rebuilt at any time. The hero and Figure 5 are visual /
conceptual images that require the image-generation agent; this script emits
labeled placeholders for them so the site build works end to end. Prompts for
the generated images live in hero-prompt.md and diagram-prompts.md.

Run from anywhere:  python papers/structure-substitutes-for-scale/scripts/make_figures.py
Output:             papers/structure-substitutes-for-scale/images/*.svg

Palette follows shared/css/paper.css (light theme). Violet is the site accent
and consistently marks *the proposal* (graph mediation, adversary independence,
crystallized structure); muted rust consistently marks *the status quo*
(context injection). Neutrals do everything else.
"""
from __future__ import annotations

import html
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "images"

INK = "#23221f"
SOFT = "#55534d"
FAINT = "#86847d"
RULE = "#e6e3da"
ACCENT = "#534AB7"        # the proposal
ACCENT_SOFT = "#ece9fb"
RUST = "#A85C3F"          # the status quo
RUST_SOFT = "#f2e4dc"
PANEL = "#ffffff"
PANEL_2 = "#f6f4ee"

FONT = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def svg_open(w: int, h: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'font-family="{FONT}" role="img">\n'
        f'<defs>\n'
        f'<marker id="a-ink" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{SOFT}"/></marker>\n'
        f'<marker id="a-acc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{ACCENT}"/></marker>\n'
        f'<marker id="a-rust" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{RUST}"/></marker>\n'
        f'</defs>\n'
        f'<rect width="{w}" height="{h}" fill="{PANEL}"/>\n'
    )


def box(x, y, w, h, *, fill=PANEL, stroke=INK, sw=1.6, rx=12, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n'
    )


def text(x, y, s, *, size=22, fill=INK, weight=400, anchor="middle", style=""):
    st = f' font-style="{style}"' if style else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{st}>{html.escape(s)}</text>\n'
    )


def line(x1, y1, x2, y2, *, stroke=SOFT, sw=1.8, marker=None, dash=""):
    m = f' marker-end="url(#{marker})"' if marker else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
        f'stroke-width="{sw}"{m}{d}/>\n'
    )


def path(d, *, stroke=SOFT, sw=1.8, marker=None, dash="", fill="none"):
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{m}{da}/>\n'


def dot(x, y, r=7, *, fill=SOFT, stroke="none"):
    s = f' stroke="{stroke}" stroke-width="2"' if stroke != "none" else ""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"{s}/>\n'


# --------------------------------------------------------------------------
# Figure 1: the trialogue
# --------------------------------------------------------------------------
def fig1() -> str:
    s = svg_open(1200, 860)

    # human
    s += box(450, 36, 300, 92, fill=PANEL_2, sw=2)
    s += text(600, 74, "Human", size=26, weight=650)
    s += text(600, 104, "authority · intent · approvals", size=17, fill=SOFT)

    # orchestrator / adversary
    s += box(120, 270, 340, 104, sw=2)
    s += text(290, 308, "Orchestrator  (AI 1)", size=24, weight=650)
    s += text(290, 340, "realizes goals · tasks subagents", size=16.5, fill=SOFT)

    s += box(740, 270, 340, 104, sw=2)
    s += text(910, 308, "Adversary  (AI 2)", size=24, weight=650)
    s += text(910, 340, "malicious · contrarian · perspectival", size=16.5, fill=SOFT)

    # human <-> orchestrator
    s += line(520, 128, 330, 262, marker="a-ink")
    s += text(388, 182, "direction", size=16, fill=SOFT)
    s += line(272, 262, 468, 132, marker="a-ink", sw=1.3, dash="2 5")
    s += text(300, 216, "seeks approval", size=15, fill=FAINT)

    # orchestrator <-> adversary
    s += line(460, 306, 732, 306, marker="a-ink")
    s += line(732, 336, 460, 336, marker="a-ink")
    s += text(596, 296, "positions", size=15, fill=SOFT)
    s += text(596, 360, "challenge", size=15, fill=SOFT)

    # adversary -> human, direct escalation (bypasses orchestrator)
    s += path("M 1000 262 C 1080 170, 950 90, 760 78", stroke=ACCENT, sw=2.6,
              marker="a-acc", dash="7 6")
    s += text(1032, 168, "direct escalation", size=16.5, fill=ACCENT, weight=600)
    s += text(1032, 190, "(bypasses AI 1)", size=14.5, fill=ACCENT)

    # subagents
    for i, x in enumerate((92, 222, 352)):
        s += box(x, 452, 116, 56, fill=PANEL_2, sw=1.3, rx=10)
        s += text(x + 58, 486, f"subagent {chr(97 + i)}", size=15, fill=SOFT)
        s += line(230 + i * 26, 374, x + 58, 446, sw=1.2, marker="a-ink")
    s += text(268, 546, "task + scoped projection", size=15, fill=FAINT)

    for i, x in enumerate((836, 966)):
        s += box(x, 452, 116, 56, fill=PANEL_2, sw=1.3, rx=10)
        s += text(x + 58, 486, f"subagent {chr(100 + i)}", size=15, fill=SOFT)
        s += line(884 + i * 52, 374, x + 58, 446, sw=1.2, marker="a-ink")

    # tool graph
    s += box(330, 596, 540, 226, fill=PANEL_2, sw=2, rx=16)
    s += text(600, 632, "MCP tool graph", size=21, weight=650)
    nodes = [(420, 700), (500, 668), (588, 712), (676, 672), (762, 706),
             (462, 764), (556, 780), (654, 762), (742, 770)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (2, 6), (3, 7), (4, 8),
             (5, 6), (6, 7), (7, 8), (1, 6)]
    for a, b in edges:
        s += line(*nodes[a], *nodes[b], stroke=RULE, sw=2)
    for x, y in nodes:
        s += dot(x, y, 8, fill=FAINT)

    # independent weights
    s += path("M 290 374 C 290 480, 330 560, 408 620", stroke=INK, sw=2.4, marker="a-ink")
    s += text(258, 560, "weights w1", size=17, weight=600, anchor="end")
    s += path("M 910 374 C 910 480, 870 560, 792 620", stroke=ACCENT, sw=2.4, marker="a-acc")
    s += text(944, 560, "independent", size=17, fill=ACCENT, weight=600, anchor="start")
    s += text(944, 582, "weights w2", size=17, fill=ACCENT, weight=600, anchor="start")

    return s + "</svg>\n"


# --------------------------------------------------------------------------
# Figure 2: injection vs graph mediation
# --------------------------------------------------------------------------
def fig2() -> str:
    s = svg_open(1200, 660)

    s += text(310, 52, "Injection (prevailing)", size=23, weight=650, fill=RUST)
    s += text(890, 52, "Graph mediation (proposed)", size=23, weight=650, fill=ACCENT)
    s += line(600, 30, 600, 630, stroke=RULE, sw=2)

    # ---- left: servers dumping into context
    for i in range(6):
        x = 100 + i * 72
        s += dot(x, 96, 9, fill=RUST)
        s += line(x, 108, 180 + i * 52, 158, stroke=RUST, sw=1.3, marker="a-rust")
    s += text(310, 78, "connected servers", size=15, fill=SOFT)

    s += box(70, 166, 480, 420, sw=2, rx=14)
    s += text(310, 198, "model context", size=18, weight=600, fill=SOFT)
    # wall of tool chips
    chip_w, chip_h = 66, 26
    n = 0
    for row in range(9):
        for col in range(6):
            x = 92 + col * (chip_w + 8)
            y = 214 + row * (chip_h + 8)
            s += box(x, y, chip_w, chip_h, fill=RUST_SOFT, stroke=RUST, sw=0.9, rx=6)
            n += 1
    s += text(310, 542, f"{n}+ tool schemas, all-or-nothing", size=15, fill=RUST, style="italic")
    # squeezed task
    s += box(92, 552, 436, 26, fill=PANEL_2, stroke=INK, sw=1.4, rx=6)
    s += text(310, 570, "task (competing for attention)", size=14.5, fill=INK)

    # ---- right: graph -> projection -> clean context
    s += box(660, 88, 480, 250, fill=PANEL_2, sw=2, rx=16)
    s += text(900, 120, "full-resolution graph  (every server)", size=17, weight=600)
    nodes = [(720, 180), (790, 152), (864, 196), (938, 156), (1012, 190),
             (1076, 158), (748, 252), (830, 276), (912, 250), (992, 278),
             (1064, 246), (700, 300), (770, 308), (1096, 300)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 6), (6, 7), (7, 8),
             (8, 9), (9, 10), (2, 8), (3, 9), (6, 11), (6, 12), (10, 13), (1, 7)]
    hot_nodes = {2, 7, 8}
    hot_edges = {(2, 8), (7, 8)}
    for a, b in edges:
        hot = (a, b) in hot_edges or (b, a) in hot_edges
        s += line(*nodes[a], *nodes[b],
                  stroke=ACCENT if hot else RULE, sw=3 if hot else 2)
    for i, (x, y) in enumerate(nodes):
        s += dot(x, y, 9 if i in hot_nodes else 7,
                 fill=ACCENT if i in hot_nodes else FAINT)

    s += path("M 880 338 C 880 372, 880 384, 880 406", stroke=ACCENT, sw=2.6, marker="a-acc")
    s += text(1010, 384, "task-scoped projection", size=16, fill=ACCENT, weight=600)

    s += box(700, 414, 400, 172, sw=2, rx=14)
    s += text(900, 446, "model context", size=18, weight=600, fill=SOFT)
    s += box(724, 462, 352, 56, fill=PANEL_2, stroke=INK, sw=1.4, rx=8)
    s += text(900, 496, "task (room to think)", size=17, fill=INK, weight=600)
    for i in range(3):
        s += box(724 + i * 122, 532, 110, 30, fill=ACCENT_SOFT, stroke=ACCENT, sw=1.1, rx=6)
        s += text(779 + i * 122, 552, f"tool {i + 1}", size=14.5, fill=ACCENT)

    return s + "</svg>\n"


# --------------------------------------------------------------------------
# Figure 3: the preregistered interaction prediction
# --------------------------------------------------------------------------
def fig3() -> str:
    s = svg_open(1200, 640)

    ox, oy = 150, 520          # axis origin
    top, right = 90, 1010
    s += line(ox, oy, ox, top, stroke=INK, sw=2)
    s += line(ox, oy, right, oy, stroke=INK, sw=2)
    s += (f'<text x="70" y="305" font-size="18" fill="{SOFT}" font-weight="600" '
          f'text-anchor="middle" transform="rotate(-90 70 305)">task performance</text>\n')

    x1, x2 = 380, 800
    for x, lab in ((x1, "in-context provisioning"), (x2, "graph-mediated provisioning")):
        s += line(x, oy, x, oy + 10, stroke=INK, sw=2)
        s += text(x, oy + 40, lab, size=18, fill=INK, weight=600)

    def y(v):  # v in 0..1
        return oy - v * (oy - top - 20)

    # gridlines
    for v in (0.25, 0.5, 0.75, 1.0):
        s += line(ox, y(v), right, y(v), stroke=RULE, sw=1.2)

    # frontier
    fy1, fy2 = y(0.82), y(0.86)
    s += line(x1, fy1, x2, fy2, stroke=INK, sw=3)
    s += dot(x1, fy1, 8, fill=INK)
    s += dot(x2, fy2, 8, fill=INK)
    s += text(880, fy2 - 2, "frontier-scale model", size=17, weight=600, anchor="start")

    # sub-1B
    sy1, sy2 = y(0.30), y(0.72)
    s += line(x1, sy1, x2, sy2, stroke=ACCENT, sw=3)
    s += dot(x1, sy1, 8, fill=ACCENT)
    s += dot(x2, sy2, 8, fill=ACCENT)
    s += text(880, sy2 + 8, "sub-billion model", size=17, fill=ACCENT,
              weight=600, anchor="start")

    # gap annotations
    s += line(x1 - 44, fy1, x1 - 44, sy1, stroke=RUST, sw=2, marker="a-rust")
    s += line(x1 - 44, sy1, x1 - 44, fy1, stroke=RUST, sw=2, marker="a-rust")
    s += text(x1 - 62, (fy1 + sy1) / 2 + 6, "large gap", size=16.5, fill=RUST,
              weight=600, anchor="end")

    s += line(x2 + 44, fy2, x2 + 44, sy2, stroke=ACCENT, sw=2, marker="a-acc")
    s += line(x2 + 44, sy2, x2 + 44, fy2, stroke=ACCENT, sw=2, marker="a-acc")
    s += text(x2 + 62, (fy2 + sy2) / 2 - 4, "small gap", size=16.5, fill=ACCENT,
              weight=600, anchor="start")
    s += text(x2 + 62, (fy2 + sy2) / 2 + 18, "(predicted)", size=14.5, fill=ACCENT,
              anchor="start")

    s += text(1010, 62, "schematic of the hypothesis · no data yet", size=15,
              fill=FAINT, style="italic", anchor="end")
    s += text(600, 610, "falsifier: the gap persists undiminished under graph mediation",
              size=15.5, fill=SOFT, style="italic")

    return s + "</svg>\n"


# --------------------------------------------------------------------------
# Figure 4: an MCP server as a holon
# --------------------------------------------------------------------------
def fig4() -> str:
    s = svg_open(1200, 760)

    cx = 400
    # context (outermost)
    s += box(110, 80, 580, 600, fill=PANEL_2, stroke=FAINT, sw=1.8, rx=26)
    s += text(cx, 116, "CONTEXT", size=16, fill=FAINT, weight=700)
    s += text(cx, 140, "registry + concept-graph membership · versions", size=15, fill=SOFT)

    # boundary
    s += box(170, 168, 460, 452, fill=PANEL, stroke=ACCENT, sw=3, rx=20)
    s += text(cx, 202, "BOUNDARY", size=16, fill=ACCENT, weight=700)
    s += text(cx, 226, "what is allowed: access edge weights", size=15, fill=SOFT)
    s += text(cx, 248, "orchestrator writes w1 · adversary holds its own w2", size=14.5,
              fill=ACCENT)

    # interior
    s += box(232, 282, 336, 270, fill=PANEL_2, stroke=INK, sw=2, rx=16)
    s += text(cx, 316, "INTERIOR", size=16, fill=INK, weight=700)
    s += text(cx, 340, "full tool schemas, at full resolution", size=15, fill=SOFT)
    nodes = [(300, 410), (380, 388), (462, 416), (330, 480), (420, 496), (500, 470)]
    edges = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5)]
    for a, b in edges:
        s += line(*nodes[a], *nodes[b], stroke=RULE, sw=2)
    for x, y in nodes:
        s += dot(x, y, 8, fill=FAINT)

    s += text(cx, 656, "one holon = one MCP server", size=16, fill=SOFT, style="italic")

    # projection out to subagent view
    s += path("M 630 380 C 720 380, 740 380, 810 380", stroke=ACCENT, sw=2.6, marker="a-acc")
    s += text(722, 362, "PROJECTION", size=15, fill=ACCENT, weight=700)

    s += box(820, 300, 300, 168, sw=2, rx=14)
    s += text(970, 334, "what a subagent sees", size=17, weight=650)
    for i in range(3):
        s += box(844 + (i % 2) * 130, 352 + (i // 2) * 44, 118, 32,
                 fill=ACCENT_SOFT, stroke=ACCENT, sw=1.1, rx=6)
        s += text(903 + (i % 2) * 130, 373 + (i // 2) * 44, f"tool {i + 1}",
                  size=14.5, fill=ACCENT)
    s += text(970, 448, "task-scoped, nothing more", size=14.5, fill=SOFT, style="italic")

    # portal = crystallized handler
    s += path("M 630 560 C 730 560, 760 580, 826 596", stroke=ACCENT, sw=2.6,
              marker="a-acc", dash="9 6")
    s += box(836, 560, 300, 118, fill=ACCENT_SOFT, stroke=ACCENT, sw=1.6, rx=14)
    s += text(986, 596, "portal", size=17, fill=ACCENT, weight=700)
    s += text(986, 622, "a stored query, carried as RDF:", size=14.5, fill=SOFT)
    s += text(986, 644, "the crystallized-handler primitive", size=14.5, fill=SOFT)

    return s + "</svg>\n"


# --------------------------------------------------------------------------
# Placeholders for the image-generation agent
# --------------------------------------------------------------------------
def placeholder(w, h, title, sub, prompt_file) -> str:
    s = svg_open(w, h)
    s += box(24, 24, w - 48, h - 48, fill=PANEL_2, stroke=FAINT, sw=2,
             rx=18, dash="10 8")
    # quiet lattice motif so the placeholder reads as intentional
    import math
    pts = [(w * 0.5 + math.cos(k * 0.9) * (w * 0.30),
            h * 0.55 + math.sin(k * 1.7) * (h * 0.22)) for k in range(9)]
    for i in range(len(pts) - 1):
        s += line(*pts[i], *pts[i + 1], stroke=ACCENT_SOFT, sw=2.4)
    for x, y in pts:
        s += dot(x, y, 6, fill=ACCENT_SOFT)
    s += text(w / 2, h / 2 - 34, title, size=30, weight=700, fill=SOFT)
    s += text(w / 2, h / 2 + 4, sub, size=19, fill=FAINT)
    s += text(w / 2, h / 2 + 40, f"awaiting image-generation agent · prompt in {prompt_file}",
              size=16.5, fill=ACCENT, style="italic")
    return s + "</svg>\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fig1-trialogue.svg").write_text(fig1())
    (OUT / "fig2-provisioning.svg").write_text(fig2())
    (OUT / "fig3-prediction.svg").write_text(fig3())
    (OUT / "fig4-holon-mapping.svg").write_text(fig4())
    (OUT / "fig5-crystallization-placeholder.svg").write_text(
        placeholder(1200, 620, "Figure 5 · placeholder",
                    "Handler crystallization (conceptual image)",
                    "diagram-prompts.md"))
    (OUT / "hero.svg").write_text(
        placeholder(1200, 800, "Hero image · placeholder",
                    "The crowded doorway (conceptual image)",
                    "hero-prompt.md"))
    for f in sorted(OUT.glob("*.svg")):
        print("wrote:", f.relative_to(OUT.parent))


if __name__ == "__main__":
    main()

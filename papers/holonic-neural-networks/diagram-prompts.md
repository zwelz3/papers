# Diagram generation prompts

Four figures for the Holonic Neural Networks paper. Each prompt states what the figure shows, the message it must land, the composition, and where it sits in the text. Figures 2 and 3 are data plots (line charts over time); Figures 1 and 4 are structural diagrams.

**[FIGURE 1 — generation prompt]**

**What it shows:** A labeled structural cutaway of a single holon, the fundamental unit of the architecture. This is a reference diagram (boxes, labels, containment), not a data plot.

**The message:** A holon is one bounded object with five distinct parts working together: an *interior* (a small graph of nodes and edges representing its knowledge), a *membrane* wrapping the interior (the boundary that admits or rejects incoming signals), *portals* (typed, weighted arrows leaving the holon toward other holons), a *provenance* strip (an append-only log line beneath the holon), and an *energy* level (a small gauge or fill indicating how "hot"/active the holon currently is). The reader should come away understanding that structure and state live in the same object.

**Composition:** A single large rounded-hexagon or rounded-rect "holon" centered in frame. Inside it, a clearly nested inner region labeled *interior* containing 4-5 small connected nodes (a mini knowledge graph). The outer boundary is visually distinct (a thicker or textured ring) and labeled *membrane*. One incoming arrow from the left is labeled *admitted* (passes through the membrane); a second incoming arrow is labeled *rejected* and visibly bounces off / is blocked by the membrane (small X). On the right, two *portal* arrows of visibly different thickness (weight) lead to a faded "another holon." A thin horizontal *provenance* bar sits along the bottom edge. A small *energy* gauge (partial fill) sits in a corner. Warm accent only on the energy gauge and the admitted path; everything else cool/neutral. Clean, generous labels, editorial-technical style.

**Relation to text:** This sits at the end of §2.1, right after the four-graph decomposition (interior / membrane / portals / provenance) and the `Holon`/`Portal` pseudo-structure. Every labeled part must match a field named in that code block, plus the HNN's added `energy`.

---

**[FIGURE 2 — generation prompt]**

**What it shows:** A two-panel line chart of *energy over time* (ticks on the x-axis, holon energy 0 to 1 on the y-axis), contrasting the broken propagation rule with the fixed one. This is a data-plot diagram, not a picture of nodes. The earlier hand-drawn version showed two frozen clusters of colored circles, which did not convey the *temporal dynamics* that are the actual point; this should be trajectories over time.

**The message:** The failure and the fix are both about how energy evolves tick by tick. In the broken model, additive bumps outrun decay, so every holon's energy climbs and pins to a flat ceiling near 1.0 and stays there (all holons saturate, the used-vs-unused signal is destroyed). In the fixed model, energy is applied as a *floor after decay*: a directly-stimulated holon spikes to 1.0, propagation-lit holons settle at progressively lower plateaus (graded by distance), and when input stops, every trace decays smoothly back down. The reader should see "flat pinned ceiling" vs "graded, decaying, alive."

**Composition:** Two side-by-side (or stacked) line charts sharing the same axes. LEFT, labeled *broken: additive bumps*: several energy traces all rising quickly and flattening against a saturation ceiling at ~1.0, indistinguishable from each other. RIGHT, labeled *fixed: floor after decay*: one trace spiking to 1.0 (the directly-injected holon), two or three more settling at successively lower, clearly-separated plateaus (0.7, 0.5, 0.35 range) while input is on, then all of them decaying back toward baseline after an "input stops" marker on the x-axis. Use a subtle vertical guide line marking where stimulation ends. Warm color for the hot/injected trace, cooler colors for the propagation-lit ones. Keep the broken panel's traces a muted warning tone (they've all collapsed together). Minimal, clean, labeled axes ("tick", "energy").

**Relation to text:** Sits at the end of §4 (Energy), right after the `tick()` pseudo-code whose ordering (decay first, then capped floors) is exactly what produces the right-panel behavior. The three failures described in §4.2 (can't decay / can't propagate / wrong-scale gate) are the reasons the left panel looks the way it does.

---

**[FIGURE 3 — generation prompt]**

**What it shows:** A single line chart of *energy over time* (ticks on the x-axis, energy on the y-axis) with two decay curves: one for the slow-decay semantic region and one for the fast-decay episodic region, both starting from the same initial energy and then idling. A data plot, not a picture of regions.

**The message:** Forgetting falls out of physics, not a special routine. Both regions receive the same input (both traces start at the same height). Then the system idles. The episodic trace (decay rate ~0.15/tick) drops steeply toward zero; the semantic trace (decay rate ~0.005/tick) stays nearly flat, barely declining. After a few dozen idle ticks the gap between them is roughly 24x. The reader should see the system "remember" the durable fact and "forget" the ephemeral episode from nothing but a difference in one decay constant.

**Composition:** One clean line chart. Two curves from a shared starting point at the left. Upper curve labeled *semantic (~0.005/tick), durable*: stays high, gently sloping down. Lower curve labeled *episodic (~0.15/tick), fades*: exponential-looking decay toward the baseline. An annotation bracket or callout near the right edge marking the "~24x ratio after idle." Use a cool/blue tone for the persistent semantic curve and a warm/coral tone for the fading episodic curve. Label the x-axis "idle ticks" and y-axis "energy." Understated, editorial-technical.

**Relation to text:** Sits at the end of §6 (Regions), right after the `RegionConfig` / `REGIONS` code block where semantic `decay_rate=0.005` and episodic `decay_rate=0.15` are literally defined. The two curves are those two numbers playing out over time.

---

**[FIGURE 4 — generation prompt]**

**What it shows:** A nested-containment diagram of four homeostatic control loops, drawn as concentric layers from outermost to innermost, each annotated with the *timescale* it runs on. A structural/reference diagram.

**The message:** The system's stability comes from four control loops operating at different rates, each nested inside the next and catching instabilities the outer one lets through. From outside in: (1) *energy budget*, a hard per-tick cap on total activity, scaled to network size; (2) *adaptive arousal gate*, a slow system-level loop that tunes the firing threshold from energy variance; (3) *intrinsic plasticity*, a per-holon BCM sliding threshold that adjusts each holon toward a target firing rate; (4) *weight normalization*, a per-update renormalization of a holon's outgoing portal weights. The reader should grasp both the nesting (each loop contains the next) and the honest subtext: each layer adds its own parameters, so the stabilizers become their own source of complexity.

**Composition:** Four concentric rounded rectangles (or rounded frames), nested. Outermost and largest = *energy budget* with subtitle "hard cap, per tick." Next inward = *adaptive arousal gate*, "system level, slow." Next = *intrinsic plasticity*, "per holon, BCM sliding threshold." Innermost and smallest = *weight normalization*, "per update." Put a small timescale tag on each layer (e.g. a clock icon or the words per-update / per-tick / slow) to reinforce that they run at different rates. A short caption line can note "each loop catches what the one outside it lets through." Use a graded palette from cool (outer) to warm (inner) or four distinct region colors; keep labels large and legible. Clean, calm, technical.

**Relation to text:** Sits at the end of §7.1, right after the `homeostasis()` pseudo-code, whose four blocks (a) weight normalization, (b) BCM plasticity, (c) energy budget, (d) adaptive gate map exactly onto these four layers. The diagram should make the "feedback loops stabilizing feedback loops" point that the following paragraph makes in prose.

---

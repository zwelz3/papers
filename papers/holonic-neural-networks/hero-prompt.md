# Image-generation prompt for the header graphic

## The prompt (paste into an image model)

> A wide editorial header illustration for a technical essay on "holonic neural networks." Conceptual, clean, and restrained, in the visual language of a thoughtful engineering blog rather than sci-fi. Show a **nested hierarchy of rounded hexagonal cells** ("holons"), each cell containing a small graph of nodes and edges inside it, and smaller cells nested inside larger ones, three levels deep. The cells are connected to each other by **a few clean, deliberate curved links** (not a dense tangle), some links drawn as thicker glowing threads and others as thin faint ones, suggesting typed connections of different strength. Use a **warm-to-cool energy gradient across the field**: a handful of cells glow warm (amber and coral) as if active, most sit cool and quiet (deep teal, slate, indigo), so the eye can immediately see "where the activity is." Thin geometric provenance traces run faintly beneath the cells like circuit routing. Composition is calm and horizontal, generous negative space, subtle depth, flat vector aesthetic with a light grain. No text, no labels, no faces, no literal brains, no glowing blue "AI" clichés, no wires-into-a-head imagery. Muted sophisticated palette on a soft off-white (or, for the dark variant, near-black charcoal) background. Aspect ratio 16:6, high detail, crisp edges.

## Negative prompt (if the model supports one)

> text, letters, watermark, human face, literal brain, neurons with axons, glowing blue circuitry cliche, robot, android, dense hairball graph, chaotic wires, lens flare, 3D render chrome, stock-photo hologram, busy background

## Why this composition

The essay's whole thesis is "structure and computation are the same object," so the hero has to *show structure that is also state*:

- **Nested hexagonal cells** carry the holon/holarchy idea (whole-that-is-also-a-part) without a caption. Hexagons read as "cells / units / tiling" and nest cleanly.
- **A graph visible inside each cell** makes the "the interior is itself a graph" point literal, which is the single most distinctive claim of the piece.
- **Few, deliberate, differently-weighted links** encode typed portals with weights, and dodge the "dense neural-net hairball" cliche that would contradict the essay's argument that HNN connections are governed and sparse, not homogeneous and dense.
- **The warm/cool energy gradient** is the energy-dynamics section rendered as an image: you can see at a glance which holons are "hot." That is exactly the property Figure 2 and Figure 3 in the paper are about.
- **Faint provenance traces underneath** nod to the fourth graph layer (PROV-O) without cluttering.
- Explicitly banning brains, faces, and blue-glow circuitry keeps it from sliding into generic "AI art," which would undercut a piece whose tone is sober and self-critical.

## Palette guidance (if you want to hand-tune)

- Cool base: deep teal `#0F6E56`, slate indigo `#3C3489`, muted blue `#185FA5`
- Warm accents (the "hot" holons): amber `#BA7517`, coral `#D85A30`
- Backgrounds: off-white `#FBFAF7` (light) or charcoal `#1A1A18` (dark)
- Keep saturation low overall; let only the few active holons carry saturated warmth.

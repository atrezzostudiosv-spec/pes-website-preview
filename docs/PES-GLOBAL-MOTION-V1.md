# PES — Global Motion System V1.0
Permanent global Design System standard. User approved extension to all existing and future PES pages. No layout changes authorized.

Original resources (unmodified Git blobs):
- motion/ATZ-MOT-001.js — 25be335089dbfcc3e8ebac45305947c9f20a3c2c
- motion/runtime.js — d4fc5105b346c52cf947f53be8a822c98abefaa4
- motion/atrezzo-motion-v1.css — 7fb9ccf2eade5aa061425ca3c10169b3136d5a90
- typography/ATZ-MOT-013.js — e1ab6b3a73e263a5d69c14a46d81fd95cab981d6
- typography/runtime.js — af62d3d0dbf1ed5c513a966ed95f8f27df0f1207
- typography/atrezzo-typography.css — 0aac45dc4c37a785cf9f1bc579f178e4c538cdd9

Reference demos: https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id=ATZ-MOT-001 and https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id=ATZ-MOT-013.

The PES adapter coordinates independently mounted groups and two title segments; the original H2 remains the layout/accessibility source. Entry offsets 0/120/320/440 ms; original character stagger 5 ms and duration 1200 ms; original group stagger 120 ms and duration 700 ms. No new animation formulas. Native scroll, one-shot, static without JS or reduced motion, keyboard focus cancels pending movement. Our Specialty keeps its approved adapter. Other editorial regions opt in using data-pes-editorial and the shared global entry.

## Mandatory development protocol
Every existing and future customer-facing page loads assets/pes-motion-global.css and assets/pes-motion-global.js once (correct relative path). Mark each editorial region data-pes-editorial. Mark exceptions data-pes-motion-off with a documented reason. The system is not a blanket animation of every node.
- One protagonist H1/H2 per region uses MOT-001; original semantic heading is restored, with original typography and line breaks. Longer headings may use group entry. MOT-013 applies to eligible nearby text groups and editorial CTAs, at most three elements per cascade, using original WAAPI effects retargeted onto the unmodified layout. Existing green rules attached to labels appear with their label; Specialty's separate green rule retains its approved sequence. Do not add a new line where the design has none.
- Keep cinematic Hero, ATZ-SEC-004 and SS03 engines unchanged; exclude menus, forms, critical notices, historical job text and long lists. No motion stacking, no new libraries, no pinning, no scroll interception. Keep original brand and content.
- Native scroll entry once, keyboard focus and reduced motion fail open. Content and links work without JS. Test desktop/mobile, exact layout, reverse and fast scroll, focus, reduced motion, no-JS, console and component coexistence. Do not certify production without visual review.

Current rollout: 16 navigable pages. Technical/visual QA tracked separately.

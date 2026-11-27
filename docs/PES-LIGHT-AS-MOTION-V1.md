# PES — Light as Motion V1.0
Approved direction, 2026-11-27: reference the existing Powered by Precision entrance/exit; images emerge from black as the viewport approaches, return to the original composition, and dissolve into the next dark section. Reversible, native scroll, no new library.
 
## Scope
- Hillside / ATZ-SEC-002, Our Services / ATZ-SEC-015 (entire slider, not each slide), The PES Difference / ATZ-SEC-004 (entire handoff), Let's Connect. Independent photo-only gradients, no opacity applied to copy or controls. Existing contrast scrims remain. Contact fixed upper gradient is replaced by the dynamic equivalent while enhanced, and retained for static fallback.
- Powered by Precision / ATZ-SCR-007 remains byte-identical; existing Specialty white interlude and Hero remain unchanged to preserve their approved identity and avoid introducing a black band into a white editorial section. Editorial intros, Featured Brands and footer retain their original text/brand motion and neon. No added blank holds or global veil.
- Entry goes from black at the entering top edge to clear by the time the stage is near the viewport top. Exit begins only near the end of original sticky travel and darkens the lower edge as the stage leaves. Cubic smoothstep with independent per-scene thresholds in the adapter; no additional pinned distance. Existing zooms, wipes, slide changes, typography, content, links and responsive layouts remain.
- Fail open when JS is absent, reduced motion or viewport height below 600px, or the component has not enhanced. Read-only track/stage geometry, one coalesced animation frame, no scroll interception, no vendor or GSAP mutations. No real photograph files edited.
 
## QA
Dedicated Chromium/WebKit workflow: six viewport sizes; forward/hold/exit/reverse gradient state, pointer events, unchanged scene pin geometry at mid-scroll, original CTA/link presence, no overflow, reduced-motion and no-JS fallback; representative screenshots. Existing QA retained, adapting only the expected upper contact gradient in the enhanced state.
 
## Limitations and acceptance
Visual judgment remains pending. Exact transition strengths are an initial calibration; no live-device approval claimed. Earlier Hillside mobile opacity and Services intro timing failures remain separate. Prior Featured Brands QA run 46022519725 passed and Pages run 46022519109 deployed before this change; prior closing run 46022519593 had not finished when inspected.

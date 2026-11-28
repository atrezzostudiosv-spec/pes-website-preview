# PES Services V4 — candidate for visual review
Scope: capabilities index and five existing service routes; no edits to Home, Why Us, global header/footer, project page markup or ATREZZO engines.
Source: data/editorial-v3.json, approved editorial master in repository. All master body paragraphs retained; no new service or performance claim. Power Quality remains educational with its existing technical reference. No additional image claims or external media.
Index: one five-service list, retained original ATZ-SEC-008 scene, dedicated Power Quality and EV editorial panels. Lighting retains original ATZ-SEC-007. Existing images only. Shared typography, black/white transitions, green rules, global motion opt-ins and distinct page imagery. Existing SEO metadata sourced from master, noindex retained.
Generator: scripts/build_services_v4.mjs; Interiors V3 delegates capabilities generation to it. Determinism checked in code before commit; visual and browser QA pending.
Project V4.1: mobile Design Review layout constraints, desktop untouched. Previous browser run failed Laurel Way at 390px; CSS correction candidate, requires rerun.

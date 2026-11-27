# Home 03 — Featured Project / Hillside
ATZ-SEC-002 (Split), original files copied exactly from the ATREZZO library:
- ATZ-SEC-002.html 00863b8d49c85ef9750be0efff111644f98599a2
- ATZ-SEC-002.js 3d858a455561aa7cbb043745cd08013863a03bbf
- ats1.css e8fa7947093452ac1be561b28faacd7319a5b8fc
- ats1-engine.js 3022616065b5101710865b66673f439216d97560
Reference: https://atrezzostudiosv-spec.github.io/atrezzo-repositorio/catalog/preview.html?id=ATZ-SEC-002
PES content, neutral black gradient, Montserrat, green accent and photographic object-position only. Original scroll geometry (210svh desktop; 176svh mobile with minimums), clip, opacity, translation and sticky unchanged. Focus-within reveals link without changing scroll progression; reduced mobile clip correction matches mobile static fallback. Explicit opt-out from global motion. PES-049 original image not retouched. Source photograph depicts construction work. Visual approval pending.

## Mobile text V1.1
Increased mobile coarse-pointer opacity/transform easing from 220ms to 620ms with a gentle cubic-bezier. Same original scroll thresholds and photo movement. Desktop, reduced motion and focus remain unchanged. Dedicated browser QA checks intermediate opacity after a rapid scroll step. Services gesture QA failure is separate; no change to Services in this pass.

## Mobile hold V1.2
Touch/mobile only: extend Hillside track from 176svh (min 1050) to 230svh (min 1200). Scope copy easing to progress .40–.65 (formerly .43–.74); complete composition remains fixed for final 35% of native scroll travel. Existing image collapse formula, 620ms copy easing, desktop, reduced-motion and keyboard preserved. Source ATS1 engine unchanged; destination derivative differs only in copy timing. Mosaic receives only versioned mount readiness import, not a motion change. No lock, timer hold or scroll interception. Tests sample the full visible text during forward/reverse hold and verify original source hash. Physical mobile review pending; rapid native inertia can still traverse a long distance.

## Mobile hold V1.3
User reported V1.2's 35% hold still felt too brief. Increase track from 230svh to 350svh; map the original mobile visual progression to the first 52% of travel so the text finishes near 34% of total travel, leaving about 66% (roughly 1.65 small viewports) as a fully visible, pinned reading interval. Keep 620ms easing and desktop/reduced behavior. No global scroll lock, snap or timer. Test a rapid one-viewport step after the full composition; physical inertia beyond the reserved distance can still exit. Version all affected imports; mosaic engine unchanged.

# PES Home 07–08 — Cinematic closing V1.0
User approved an impactful photograph, native scroll-linked zoom, black left gradient, seamless black footer and thin neon-green separator.
Selection: PES-030.jpg, original Hillside night aerial, 1500 × 1124, inspected visually; unused in prior Home. No editing, retouching, or invented imagery.
Close: preserve contact copy/telephone/contact destination; Montserrat 300/700, green 2px accent. Sticky stage while image scales 1→1.24 desktop / 1→1.16 mobile; 75svh / 65svh travel. Bottom gradient joins black footer. Text and CTA remain stable. No scroll interception; short viewports and reduced motion are static. Footer: approved neon logo, existing navigation, confirmed contact/Instagram links, two-pixel PES-green seam and single 1.9-second light sweep when visible. No pulsing or flicker.
Only Home changes; previous sections and component engines untouched. Original brand crops remain provisional and separate. Footer of internal pages not changed in this pass. Visual validation pending.

## V1.1 — Featured Brands to Let's Connect dissolve (2026-11-27)
Replace the weak desktop upper gradient (missing on mobile) with a common frame-fixed top layer: black 0%, opacity .86 at 12%, .50 at 28%, .15 at 42%, transparent at 52%. Preserve the existing left/bottom layers, image, native sticky zoom, copy, CTA, phone and footer/neon unchanged. The upper fade remains fixed while the photo scales. CSS cache versions bumped; existing QA extended to six normal viewport sizes on Chromium/WebKit, with seam screenshots in Featured Brands QA. Visual approval pending.

### Pre-existing validation issues (out of scope)
- Hillside mobile text QA run 46002969078: opacity progression assertion failed (0.857479, 0.998926, 1.0); no Hillside change.
- Our Services cinematic QA run 46019886349: timeout waiting for pesServicesMotion='playing'; no Services change.
- Previous closing QA run 46019886435 cancelled before completion; do not treat as a pass.

## V1.2 — Approved Los Angeles night photograph (2026-11-27)
User-uploaded `assets/media/pes-connect-los-angeles.webp` (2048 × 1366, 659936 bytes, blob d458fc72f3c9cbb3cac0d2e8a62a360c079efe39) replaces PES-030.jpg in the Home contact scene only. Preserve previous source image, all existing frame crop settings, permanent top gradient, native zoom, text, links and current flat-logo footer. QA checks image decoding and current approved flat footer logo (prior assertion was stale). Hero remains unchanged because the new video was not present on main at inspection. Visual review pending.

## V1.3 — Global footer (2026-11-27)
User approved applying the Home footer to all 16 pages. Share the existing footer CSS and one-shot IntersectionObserver light animation globally; keep all #pes-connect rules and scroll logic scoped to Home. Static HTML replicated from approved footer with depth-aware relative links and aria-current only on exact destination pages; all six navigation links, phone, Instagram, green SVG, three-column desktop / two-column mobile arrangement, 2px green line, 1.9s sweep and reduced-motion fallback retained. No new contact scene on internal pages. Dedicated QA verifies all links, markup, layout, image decoding and animation on Chromium/WebKit across six viewports plus reduced motion and no-JS. Visual approval pending.

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

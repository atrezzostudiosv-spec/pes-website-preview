# PES Responsive Review V1.0
User reported original Handoff behaving differently on iPhone XS and 12 Pro, and white top/bottom strips around Powered by Precision. Previous correction removes Home Handoff's <=820px override, and mosaic V1.5 provides dark backing. Preserve original photographs, layouts and timelines.
- ATZ-SEC-015 original engine stays archived, byte-identical. The PES runtime derivative differs by exactly one media-query line: portrait mobile no longer falls back when Safari crosses 700px. Desktop height rule and reduced-motion preference remain. A compact layout applies below 700px. No modification to movement formulas.
- Shared introduction adapter now cancels only if measured title geometry actually changes during animation; height-only changes do not cancel waiting or playing state.
- Cache version on relevant Home resources and imports, including identical mount-component URLs so only one module instance runs.
- Handoff and mosaic keep original engine. WebKit tests add 375x667, 375x812, 390x844, 430x932 and dynamic height changes; verify active scene, wipe, text, controls, reduced-motion. Native browser chrome and physical devices remain unverified.
- Do not advance to next Home section until user reviews physical phones. Existing provisional hero video and earlier filmstrip QA issue are separate pending items, not certified here.

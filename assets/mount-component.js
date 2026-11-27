// One shared readiness barrier for native ATREZZO components and downstream scroll measurement.
// Dynamic imports must finish before any dependent ScrollTrigger reads document geometry.
export const nativeComponentsReady = (async () => {
  const mounted = [];
  for (const root of document.querySelectorAll("[data-atz-id]:not([data-pes-motion])")) {
    const id = root.dataset.atzId;
    try {
      const { mount } = id === 'ATZ-SEC-002' && root.classList.contains('pes-featured-split')
        ? await import('./pes-hillside-mount.js?v=hold-1')
        : await import(`./vendor/${id}.js`);
      const instance = mount(root);
      // Preserve the original mobile scroll effect in the Home Handoff.
      if (id === "ATZ-SEC-004" && !root.querySelector("#ats2-handoff")) {
        const viewport = matchMedia("(max-width: 820px)");
        const syncViewport = () => instance.setReduced(viewport.matches);
        syncViewport();
        viewport.addEventListener("change", syncViewport);
      }
      mounted.push({id, root, instance});
    } catch (error) {
      // Leave the component's original static fallback intact; do not block other sections.
      console.error("PES native component mount failed:", id, error);
    }
  }
  return mounted;
})();

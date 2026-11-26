const root = document.querySelector("[data-atz-id]");
const id = root.dataset.atzId;
const { mount } = await import(`./vendor/${id}.js`);
const instance = mount(root);

if (id === "ATZ-SEC-004") {
  const viewport = matchMedia("(max-width: 820px)");
  const syncViewport = () => instance.setReduced(viewport.matches);
  syncViewport();
  viewport.addEventListener("change", syncViewport);
}

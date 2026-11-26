// One-shot, local progressive enhancement; no shared motion engine changes.
(() => {
  const section = document.querySelector('.pes-specialty');
  if (!section || !('IntersectionObserver' in window)) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches) return;
  const elements = [...section.querySelectorAll('[data-specialty-reveal]')];
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      if (!reduced.matches && !entry.target.contains(document.activeElement)) {
        entry.target.classList.add('pes-specialty-enter');
      }
    }
  }, {threshold: 0.15});
  elements.forEach(el => observer.observe(el));
  section.addEventListener('focusin', event => {
    const el = event.target.closest('[data-specialty-reveal]');
    if (el) { observer.unobserve(el); el.classList.remove('pes-specialty-enter'); }
  });
  reduced.addEventListener('change', event => {
    if (event.matches) {
      observer.disconnect();
      elements.forEach(el => el.classList.remove('pes-specialty-enter'));
    }
  });
})();

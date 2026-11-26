(() => {
  const story = document.querySelector('[data-project]');
  if (!story) return;
  const fields = Array.from(story.querySelectorAll('[data-note]'));
  const key = 'pes-project-notes:' + story.dataset.project;
  const status = story.querySelector('[role="status"]');
  const values = () => Object.fromEntries(fields.map(field => [field.dataset.note, field.value]));
  try {
    const saved = JSON.parse(localStorage.getItem(key)) || {};
    for (const field of fields) field.value = saved[field.dataset.note] || '';
  } catch { /* Download remains available when browser storage is unavailable. */ }
  for (const field of fields) field.addEventListener('input', () => {
    try { localStorage.setItem(key, JSON.stringify(values())); status.textContent = 'Draft saved in this browser.'; }
    catch { status.textContent = 'Download your notes to keep a copy.'; }
  });
  story.querySelector('[data-download-notes]').addEventListener('click', () => {
    const title = story.querySelector('h1').textContent.trim();
    const sections = Object.entries(values()).map(([label, value]) => label + '\n' + value.trim());
    const text = [title + ' | PES project notes', ...sections].join('\n\n');
    const href = URL.createObjectURL(new Blob([text], {type:'text/plain;charset=utf-8'}));
    const download = document.createElement('a');
    download.href = href;
    download.download = 'PES-' + story.dataset.project + '-notes.txt';
    document.body.append(download);
    download.click();
    download.remove();
    setTimeout(() => URL.revokeObjectURL(href), 1000);
    status.textContent = 'Project notes prepared for download.';
  });
})();

// OpenVisio v33.7 — accès direct aux propriétés avancées. Auteur : Abdelhalim Talbi.
const all = document.getElementById('inspectorExpandAll');
all?.addEventListener('click', () => {
  const toggle = document.getElementById('inspectorFieldsToggle');
  if (toggle?.getAttribute('aria-expanded') === 'false') toggle.click();
  const filter = document.getElementById('inspectorFilter');
  if (filter) { filter.value = 'all'; filter.dispatchEvent(new Event('change', {bubbles:true})); }
  const search = document.getElementById('inspectorFieldSearch');
  if (search && search.value) { search.value=''; search.dispatchEvent(new Event('input', {bubbles:true})); }
  document.getElementById('inspectorContent')?.scrollIntoView({block:'nearest'});
});

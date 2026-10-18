// OpenVisio v38.8 — catégories contextuelles de l’inspecteur. Auteur : Abdelhalim Talbi.
const toolbar = document.getElementById('inspectorCategoryToolbar');
const search = document.getElementById('inspectorFieldSearch');
const mode = document.getElementById('inspectorFilter');
const toggle = document.getElementById('inspectorFieldsToggle');
const storageKey = 'openvisio.inspector.category.v387';
const allowedCategories = new Set(['all','general','appearance','connections','san','resilience']);
function selectCategory(category, persist = true) {
  if (!allowedCategories.has(category)) category = 'all';
  for (const button of toolbar?.querySelectorAll('[data-inspector-category]') || []) {
    button.setAttribute('aria-pressed', String(button.dataset.inspectorCategory === category));
  }
  if (persist) { try { localStorage.setItem(storageKey, category); } catch {} }
  document.dispatchEvent(new Event('openvisio:inspector-refilter'));
}
let initial = 'all';
try { initial = localStorage.getItem(storageKey) || 'all'; } catch {}
if (toolbar?.querySelector(`[data-inspector-category="${initial}"]`)) selectCategory(initial, false);
toolbar?.addEventListener('click', event => {
  const button = event.target.closest('[data-inspector-category]');
  if (!button || !toolbar.contains(button)) return;
  if (toggle?.getAttribute('aria-expanded') === 'false') toggle.click();
  if (search?.value) { search.value = ''; search.dispatchEvent(new Event('input')); }
  if (mode && button.dataset.inspectorCategory !== 'all') {
    mode.value = 'all'; mode.dispatchEvent(new Event('change'));
  }
  selectCategory(button.dataset.inspectorCategory);

});
document.getElementById('inspectorClearFilter')?.addEventListener('click', () => {
  if (search?.value) { search.value = ''; search.dispatchEvent(new Event('input')); }
  if (mode) { mode.value = 'essential'; mode.dispatchEvent(new Event('change')); }
  selectCategory('all');
});
document.getElementById('inspectorSanFields')?.addEventListener('click', () => {
  if (toggle?.getAttribute('aria-expanded') === 'false') toggle.click();
  if (search?.value) { search.value = ''; search.dispatchEvent(new Event('input')); }
  if (mode) { mode.value = 'all'; mode.dispatchEvent(new Event('change')); }
  selectCategory('san');
});

// OpenVisio v38.6 — raccourcis contextuels non destructifs pour l'inspecteur. Auteur : Abdelhalim Talbi.
const search = document.getElementById('inspectorFieldSearch');
const mode = document.getElementById('inspectorFilter');
const san = document.getElementById('inspectorSanFields');
const reset = document.getElementById('inspectorClearFilter');
const content = document.getElementById('inspectorContent');
const toggle = document.getElementById('inspectorFieldsToggle');
function expand() {
  if (toggle?.getAttribute('aria-expanded') === 'false') toggle.click();
}
function notify() { document.dispatchEvent(new Event('openvisio:inspector-refilter')); }
san?.addEventListener('click', () => {
  expand();
  if (mode) { mode.value = 'all'; mode.dispatchEvent(new Event('change', { bubbles: true })); }
  if (search) { search.value = '@san'; search.dispatchEvent(new Event('input', { bubbles: true })); }
  search?.focus();
  content?.scrollIntoView({ block: 'nearest' });
  notify();
});
reset?.addEventListener('click', () => {
  expand();
  if (search) { search.value = ''; search.dispatchEvent(new Event('input', { bubbles: true })); }
  if (mode) { mode.value = 'essential'; mode.dispatchEvent(new Event('change', { bubbles: true })); }
  notify();
});

// OpenVisio v34.9 — filtre unifié SAN (catégorie + recherche), non destructif.
// Auteur : Abdelhalim Talbi.
import { SAN_CATEGORIES, selectCategory } from './topology-groups-v348.js';
export function visibleSanSections(category = 'Tout', query = '', groups = SAN_CATEGORIES) {
  const allowed = selectCategory(category, groups);
  const normalized = String(query ?? '').trim().toLocaleLowerCase('fr');
  return allowed.filter(label => label.toLocaleLowerCase('fr').includes(normalized));
}
export function installSanUnifiedFilter(doc = document) {
  const nav = doc.getElementById('topologyNavigator');
  const bar = doc.getElementById('topologyCategoryBar');
  const search = doc.getElementById('topologyWorkflowSearch');
  if (!nav || !bar || !search || doc.getElementById('topologyUnifiedStatus')) return false;
  const buttons = Array.from(nav.querySelectorAll('button[aria-controls]'));
  const choices = Array.from(bar.querySelectorAll('button[data-category]'));
  const status = doc.createElement('span');
  status.id = 'topologyUnifiedStatus';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  status.className = 'topology-unified-status';
  bar.appendChild(status);
  let current = choices.find(b => b.getAttribute('aria-pressed') === 'true')?.dataset.category || 'Tout';
  const refresh = () => {
    const allowed = new Set(visibleSanSections(current, search.value));
    let count = 0;
    for (const b of buttons) {
      const visible = allowed.has(b.textContent.trim());
      b.hidden = !visible;
      b.setAttribute('aria-hidden', String(!visible));
      if (visible) count++;
    }
    for (const b of choices) b.setAttribute('aria-pressed', String(b.dataset.category === current));
    status.textContent = `${count} analyse(s) disponibles`;
    return count;
  };
  // Capture listeners run before the older, independently registered search handlers.
  // Re-apply after their synchronous handlers to prevent category/search conflicts.
  const schedule = () => queueMicrotask(refresh);
  search.addEventListener('input', schedule);
  search.addEventListener('keydown', e => {
    if (e.key === 'Escape') schedule();
    if (e.key === 'Enter') {
      const first = buttons.find(b => visibleSanSections(current, search.value).includes(b.textContent.trim()));
      if (first) { e.preventDefault(); e.stopImmediatePropagation(); first.click(); }
    }
  }, true);
  for (const choice of choices) choice.addEventListener('click', () => { current = choice.dataset.category; schedule(); });
  refresh();
  return true;
}
if (typeof document !== 'undefined') {
  const boot = () => {
    if (!installSanUnifiedFilter()) document.addEventListener('openvisio:topology-navigator-ready', () => queueMicrotask(() => installSanUnifiedFilter()), {once:true});
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once:true});
  else boot();
}

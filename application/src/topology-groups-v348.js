// OpenVisio v34.8 — catégories de navigation SAN, sans modifier les calculs.
// Auteur : Abdelhalim Talbi.
export const SAN_CATEGORIES = Object.freeze({
  'Tout': ['Comparaison','Zoning','Relations','Chemins','Ports','Applications','Matrice','Chaînes','Accès','Synthèse'],
  'Comparer': ['Comparaison','Relations','Matrice','Synthèse'],
  'Connectivité': ['Zoning','Chemins','Ports','Chaînes','Accès'],
  'Applications': ['Applications','Matrice','Synthèse']
});
export function selectCategory(name, groups = SAN_CATEGORIES) {
  return groups[name] || groups.Tout;
}
export function installSanCategories(doc = document) {
  const nav = doc.getElementById('topologyNavigator');
  if (!nav || doc.getElementById('topologyCategoryBar')) return false;
  const bar = doc.createElement('div');
  bar.id = 'topologyCategoryBar';
  bar.className = 'topology-category-bar';
  bar.setAttribute('role', 'group');
  bar.setAttribute('aria-label', 'Catégories des analyses SAN');
  const buttons = Array.from(nav.querySelectorAll('button[aria-controls]'));
  const search = doc.getElementById('topologyWorkflowSearch');
  const status = doc.createElement('span');
  status.id = 'topologyCategoryStatus';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  let current = 'Tout';
  const choices = [];
  function refresh() {
    const allowed = new Set(selectCategory(current));
    const query = (search?.value || '').trim().toLocaleLowerCase('fr');
    let count = 0;
    for (const b of buttons) {
      const name = b.textContent.trim();
      const visible = allowed.has(name) && name.toLocaleLowerCase('fr').includes(query);
      b.hidden = !visible;
      if (visible) count++;
    }
    for (const b of choices) b.setAttribute('aria-pressed', String(b.dataset.category === current));
    status.textContent = `${count} analyse(s) accessibles`;
  }
  for (const name of Object.keys(SAN_CATEGORIES)) {
    const b = doc.createElement('button');
    b.type = 'button';
    b.textContent = name;
    b.dataset.category = name;
    b.className = 'topology-category-button';
    b.addEventListener('click', () => { current = name; refresh(); });
    choices.push(b);
    bar.appendChild(b);
  }
  bar.appendChild(status);
  nav.prepend(bar);
  // Capture-phase listener: the category filter remains authoritative after the legacy search update.
  search?.addEventListener('input', refresh);
  search?.addEventListener('keydown', e => { if (e.key === 'Escape') queueMicrotask(refresh); });
  refresh();
  return true;
}
if (typeof document !== 'undefined') {
  const boot = () => {
    if (!installSanCategories()) {
      document.addEventListener('openvisio:topology-navigator-ready', () => installSanCategories(), {once:true});
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once:true});
  else boot();
}

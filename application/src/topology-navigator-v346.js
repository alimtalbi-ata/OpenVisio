// OpenVisio v34.6 — navigation contextuelle non destructive du comparateur SAN.
// Les modules de calcul existants restent propriétaires de leurs résultats.
const GROUPS = [
  ['Comparaison', 'topologyDiffSummary'],
  ['Zoning', 'topologyZoningSummary'],
  ['Relations', 'topologyRelationsSummary'],
  ['Chemins', 'topologyImpactSummary'],
  ['Ports', 'topologyPortRows'],
  ['Applications', 'topologyAppRows'],
  ['Matrice', 'topologyMatrixSummary'],
  ['Chaînes', 'topologyChainSection'],
  ['Accès', 'topologyAccessSummary'],
  ['Synthèse', 'topologyEndSummary']
];
export function installTopologyNavigator(doc = document) {
  const dialog = doc.getElementById('topologyDiffDialog');
  if (!dialog || doc.getElementById('topologyNavigator')) return false;
  const nav = doc.createElement('nav');
  nav.id = 'topologyNavigator';
  nav.className = 'topology-navigator';
  nav.setAttribute('aria-label', 'Sections de la comparaison SAN');
  for (const [label, id] of GROUPS) {
    const target = doc.getElementById(id);
    if (!target || !dialog.contains(target)) continue;
    const button = doc.createElement('button');
    button.type = 'button';
    button.className = 'topology-nav-button';
    button.textContent = label;
    button.setAttribute('aria-controls', id);
    button.addEventListener('click', () => {
      nav.querySelectorAll('button').forEach(b => b.setAttribute('aria-current', 'false'));
      button.setAttribute('aria-current', 'true');
      target.scrollIntoView?.({ behavior: 'smooth', block: 'start' });
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus?.({ preventScroll: true });
    });
    nav.appendChild(button);
  }
  if (!nav.children.length) return false;
  dialog.prepend(nav);
  return true;
}
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => installTopologyNavigator(), { once: true });
  else installTopologyNavigator();
}

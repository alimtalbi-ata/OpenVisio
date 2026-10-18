// OpenVisio v34.7 — workflow SAN: navigation accessible et recherche de sections.
// Ne modifie ni les résultats ni les données des diagrammes.
export const SAN_SECTIONS = Object.freeze([
  ['Comparaison', 'topologyDiffSummary'], ['Zoning', 'topologyZoningSummary'],
  ['Relations', 'topologyRelationsSummary'], ['Chemins', 'topologyImpactSummary'],
  ['Ports', 'topologyPortRows'], ['Applications', 'topologyAppRows'],
  ['Matrice', 'topologyMatrixSummary'], ['Chaînes', 'topologyChainSection'],
  ['Accès', 'topologyAccessSummary'], ['Synthèse', 'topologyEndSummary']
]);
export function matchSanSections(query, sections = SAN_SECTIONS) {
  const q = String(query ?? '').trim().toLocaleLowerCase('fr');
  return sections.filter(([label]) => label.toLocaleLowerCase('fr').includes(q));
}
export function installSanWorkflow(doc = document) {
  const dialog = doc.getElementById('topologyDiffDialog');
  const nav = doc.getElementById('topologyNavigator');
  if (!dialog || !nav || doc.getElementById('topologyWorkflowSearch')) return false;
  const label = doc.createElement('label');
  label.className = 'topology-workflow-search';
  label.textContent = 'Rechercher une section SAN '; 
  const search = doc.createElement('input');
  search.id = 'topologyWorkflowSearch';
  search.type = 'search';
  search.placeholder = 'Zoning, chemins, ports…';
  search.setAttribute('aria-label', 'Filtrer les sections du comparateur SAN');
  label.appendChild(search);
  const status = doc.createElement('span');
  status.id = 'topologyWorkflowStatus';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  label.appendChild(status);
  nav.prepend(label);
  const buttons = Array.from(nav.querySelectorAll('button[aria-controls]'));
  const update = () => {
    const matches = new Set(matchSanSections(search.value).map(([name]) => name));
    let count = 0;
    for (const button of buttons) {
      const show = matches.has(button.textContent.trim());
      button.hidden = !show;
      if (show) count++;
    }
    status.textContent = `${count} section(s)`;
  };
  search.addEventListener('input', update);
  search.addEventListener('keydown', event => {
    if (event.key === 'Escape') { search.value = ''; update(); search.blur(); }
    if (event.key === 'Enter') {
      const first = buttons.find(button => !button.hidden);
      if (first) { event.preventDefault(); first.click(); }
    }
  });
  update();
  return true;
}
if (typeof document !== 'undefined') {
  const boot = () => { if (!installSanWorkflow()) {
    // Module ordering is deterministic; retry only when the navigator is installed later.
    document.addEventListener('openvisio:topology-navigator-ready', () => installSanWorkflow(), { once: true });
  }};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
}

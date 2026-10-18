// OpenVisio v35.0 — tableau de bord de synthèse SAN, non destructif.
// Auteur : Abdelhalim Talbi.
export const SAN_SUMMARY_ITEMS = Object.freeze([
  ['Comparaison','topologyDiffSummary'],['Zoning','topologyZoningSummary'],
  ['Relations','topologyRelationsSummary'],['Chemins','topologyImpactSummary'],
  ['Matrice','topologyMatrixSummary'],['Chaînes','topologyChainSummary'],
  ['Accès','topologyAccessSummary'],['Validation','topologyEndSummary']
]);
export function sanitizeSummary(value, limit=220) {
  return String(value ?? '').replace(/\s+/g,' ').trim().slice(0,limit);
}
export function getSanSummary(doc, items=SAN_SUMMARY_ITEMS) {
  return items.map(([name,id]) => ({name,id,summary:sanitizeSummary(doc.getElementById(id)?.textContent || 'Analyse non disponible')}));
}
export function filterSanSummaries(items, query='') {
  const normalized=String(query).trim().toLocaleLowerCase('fr');
  return normalized ? items.filter(item => `${item.name} ${item.summary}`.toLocaleLowerCase('fr').includes(normalized)) : items;
}
export function installSanOverview(doc=document) {
  const dialog=doc.getElementById('topologyDiffDialog');
  const nav=doc.getElementById('topologyNavigator');
  if(!dialog || !nav || doc.getElementById('topologyOverview')) return false;
  const section=doc.createElement('section'); section.id='topologyOverview';
  section.className='topology-overview';section.setAttribute('aria-label','Vue synthétique des analyses SAN');
  const header=doc.createElement('div');header.className='topology-overview-heading';
  const heading=doc.createElement('h3');heading.textContent='Vue synthétique SAN';
  const refresh=doc.createElement('button');refresh.type='button';refresh.textContent='Actualiser les résultats';
  const search=doc.createElement('input');search.type='search';search.placeholder='Filtrer les analyses et résultats…';search.setAttribute('aria-label','Filtrer la synthèse SAN');
  const count=doc.createElement('p');count.setAttribute('role','status');count.setAttribute('aria-live','polite');
  header.append(heading,search,refresh,count);
  const cards=doc.createElement('div');cards.className='topology-overview-grid';
  const render=()=>{
    cards.replaceChildren();
    const matches=filterSanSummaries(getSanSummary(doc),search.value);
    count.textContent=`${matches.length} analyse(s) correspondante(s)`;
    for(const item of matches) {
      const card=doc.createElement('article');card.className='topology-overview-card';
      const title=doc.createElement('h4');title.textContent=item.name;
      const description=doc.createElement('p');description.textContent=item.summary;
      const jump=doc.createElement('button');jump.type='button';jump.textContent='Voir l’analyse';
      jump.setAttribute('aria-label',`Voir l’analyse ${item.name}`);
      const target=doc.getElementById(item.id);
      jump.disabled=!target;
      jump.addEventListener('click',()=>{
        if(!target)return;
        target.scrollIntoView?.({behavior:'smooth',block:'start'});
        if(!target.hasAttribute('tabindex'))target.setAttribute('tabindex','-1');
        target.focus?.({preventScroll:true});
      });
      card.append(title,description,jump);cards.appendChild(card);
    }
  };
  search.addEventListener('input',render);
  search.addEventListener('keydown',event=>{if(event.key==='Escape'){search.value='';render();}});
  refresh.addEventListener('click',render);
  section.append(header,cards);
  nav.insertAdjacentElement('afterend',section);
  // The comparator may be opened later; update summaries whenever its dialog opens.
  dialog.addEventListener('click',e=>{if(e.target?.closest?.('#topologyNavigator'))queueMicrotask(render);});
  dialog.addEventListener('openvisio:topology-updated',render);
  render();return true;
}
if(typeof document!=='undefined') {
  const boot=()=>{
    if(!installSanOverview())document.addEventListener('openvisio:topology-navigator-ready',()=>installSanOverview(),{once:true});
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
}

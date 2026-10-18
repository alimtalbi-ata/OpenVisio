import { analyzeSanRedundancy } from './san-redundancy-v363.js';
export function formatRedundancy(result) {
  const paths = Array.isArray(result?.paths) ? result.paths : [];
  const issues = Array.isArray(result?.issues) ? result.issues : [];
  return { paths: paths.length, healthy: paths.filter(p => p.fabricA && p.fabricB).length,
    errors: issues.filter(i => i.severity === 'error').length, warnings: issues.filter(i => i.severity === 'warning').length };
}
export function mountRedundancyPanel(doc = document) {
  const dialog = doc.getElementById('topologyDiffDialog');
  if (!dialog || doc.getElementById('sanRedundancyPanelV364')) return false;
  const panel=doc.createElement('section'); panel.id='sanRedundancyPanelV364'; panel.className='san-redundancy-panel-v364';
  const heading=doc.createElement('h3');heading.textContent='Diagnostic de redondance SAN A/B';panel.append(heading);
  const help=doc.createElement('p');help.textContent='Analyser le document ouvert ou importer un JSON pour vérifier les chemins A/B. Les boutons Chemin A/B mettent en évidence les équipements et liens traversés ; Localiser montre les extrémités sans modifier le document.';panel.append(help);
  const file=doc.createElement('input');file.type='file';file.accept='.json,application/json';file.setAttribute('aria-label','Diagramme JSON SAN à analyser');panel.append(file);
  const status=doc.createElement('p');status.id='sanRedundancyStatusV364';status.setAttribute('role','status');status.textContent='Aucun diagramme analysé.';panel.append(status);
  const table=doc.createElement('table');const caption=doc.createElement('caption');caption.textContent='Chemins serveur vers baie';table.append(caption);
  const head=doc.createElement('thead');const hr=doc.createElement('tr');for(const title of ['Serveur','Baie','Fabric A','Fabric B','Indépendance','Alternatives','Action']){const th=doc.createElement('th');th.textContent=title;hr.append(th);}head.append(hr);table.append(head);
  const body=doc.createElement('tbody');body.id='sanRedundancyPathsV364';table.append(body);panel.append(table);
  const issues=doc.createElement('ul');issues.id='sanRedundancyIssuesV364';panel.append(issues);
  const focus = (nodeIds, edgeIds=[]) => doc.dispatchEvent(new CustomEvent('openvisio:san-path-overlay', {
    detail: {sharedIds: [], survivingIds: [...new Set(nodeIds.filter(v=>v!==undefined && v!==null))], lostIds: [], edgeIds: [...new Set(edgeIds.filter(v=>v!==undefined && v!==null))]}
  }));
  const addFocusButton = (parent, nodeIds, edgeIds=[]) => {
    const button=doc.createElement('button'); button.type='button'; button.textContent='Localiser';
    button.title='Mettre en évidence les équipements concernés dans le diagramme (sans modification)';
    button.disabled=!nodeIds.some(v=>v!==undefined && v!==null) && !edgeIds.some(v=>v!==undefined && v!==null);
    button.addEventListener('click',()=>focus(nodeIds,edgeIds)); parent.append(button);
  };
  const analyzeDiagram = diagram => {
    body.replaceChildren(); issues.replaceChildren();
    if (!diagram || !Array.isArray(diagram.nodes) || !Array.isArray(diagram.edges)) throw new Error('Format attendu : nodes[] et edges[]');
    const result = analyzeSanRedundancy(diagram), summary = formatRedundancy(result);
    status.textContent = `${summary.healthy}/${summary.paths} chemins redondants ; ${summary.errors} erreur(s), ${summary.warnings} avertissement(s). Données déclaratives.`;
    for (const p of result.paths) {
      const tr=doc.createElement('tr');
      for (const value of [p.hostId,p.arrayId,p.fabricA?'OK':'Absent',p.fabricB?'OK':'Absent',p.independence==='INDEPENDENT'?'Indépendants':p.independence==='SHARED_RISK'?'Point commun':'Incomplet',`A: ${p.resilienceA.alternativeRoutes.length} / B: ${p.resilienceB.alternativeRoutes.length}`]) { const td=doc.createElement('td');td.textContent=String(value);tr.append(td); }
      const action=doc.createElement('td');
      for(const fabric of ['A','B']) {
        const route=p['route'+fabric];const button=doc.createElement('button');button.type='button';
        button.textContent='Chemin '+fabric;button.disabled=!route;
        button.title=route?`${route.nodeIds.length} équipements, ${route.edgeIds.length} liens documentés`:'Aucun chemin documenté pour cette Fabric';
        button.addEventListener('click',()=>{if(route)focus(route.nodeIds,route.edgeIds);});action.append(button);
      }
      if(p.independence==='SHARED_RISK') {
        const shared=doc.createElement('button');shared.type='button';shared.textContent='Points communs';
        shared.title='Mettre en évidence les équipements et liens communs aux chemins A/B';
        shared.addEventListener('click',()=>focus(p.sharedTransitIds,p.sharedEdgeIds));action.append(shared);
      }
      for(const fabric of ['A','B']) {
        const assessment=p['resilience'+fabric];
        const button=doc.createElement('button');button.type='button';button.textContent='Critiques '+fabric;
        button.disabled=!assessment.criticalTransitIds.length&&!assessment.criticalEdgeIds.length;
        button.title='Éléments dont la suppression coupe toutes les routes documentées de cette Fabric';
        button.addEventListener('click',()=>focus(assessment.criticalTransitIds,assessment.criticalEdgeIds));action.append(button);
      }
      if (p.commonCriticalDomains?.length) {
        const domains=doc.createElement('details');const summary=doc.createElement('summary');summary.textContent=`Domaines critiques (${p.commonCriticalDomains.length})`;domains.append(summary);
        for(const domain of p.commonCriticalDomains) {
          const entry=doc.createElement('div');entry.textContent=`${domain.kind} : ${domain.value} `;
          addFocusButton(entry,domain.nodeIds??[],domain.edgeIds??[]);domains.append(entry);
        }
        action.append(domains);
      }
      addFocusButton(action,[p.hostId,p.arrayId]);tr.append(action);body.append(tr);
    }
    for (const issue of result.issues) {const li=doc.createElement('li');li.textContent=[issue.severity,issue.code,issue.nodeId??issue.edgeId??issue.hostId??''].join(' — ');addFocusButton(li,[issue.nodeId,issue.hostId,issue.arrayId,...(issue.nodeIds??[])],[issue.edgeId,...(issue.edgeIds??[])]);issues.append(li);}
  };
  const current=doc.createElement('button');current.type='button';current.id='sanRedundancyCurrentV371';current.textContent='Analyser le diagramme ouvert';current.title='Analyse en lecture seule, sans export ni import';panel.insertBefore(current,file);
  let awaitingSnapshot=false;
  current.addEventListener('click',()=>{
    awaitingSnapshot=true;
    status.textContent='Lecture du diagramme courant…';
    doc.dispatchEvent(new Event('openvisio:san-snapshot-request'));
  });
  doc.addEventListener('openvisio:san-snapshot',event=>{
    if(!awaitingSnapshot)return;
    awaitingSnapshot=false;
    try {analyzeDiagram(event.detail);}catch(error){status.textContent=`Analyse impossible : ${error.message}`;}
  });
  file.addEventListener('change',async()=>{
    try {
      const selected=file.files?.[0];if(!selected){status.textContent='Aucun fichier sélectionné.';return;}
      if(selected.size>10*1024*1024)throw new Error('Fichier supérieur à 10 Mo');
      analyzeDiagram(JSON.parse(await selected.text()));
    }catch(error){status.textContent=`Analyse impossible : ${error.message}`;}
  });
  dialog.append(panel);return true;
}
if (typeof document !== 'undefined') {
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>mountRedundancyPanel(),{once:true});
  else mountRedundancyPanel();
}

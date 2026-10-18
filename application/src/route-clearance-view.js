// OpenVisio v41.42 — modèle de présentation indépendant du DOM.
// Auteur : Abdelhalim Talbi
export function buildRouteClearanceView(diagnostics){
 if(!diagnostics||!Array.isArray(diagnostics.edges))throw new TypeError('Diagnostics géométriques invalides');
 const items=diagnostics.edges.map(edge=>{
  const errors=Number(edge.errors)||0,reviews=Number(edge.reviews)||0;
  const severity=errors>0?'error':reviews>0?'review':'ok';
  const label=severity==='error'?'Erreur de routage':severity==='review'?'Raccordement à examiner':'Route conforme';
  return {edgeId:String(edge.edgeId),severity,label,errors,reviews,issues:structuredClone(edge.issues||[]),action:severity==='ok'?null:'Sélectionner la connexion et examiner ses segments'};
 });
 const order={error:0,review:1,ok:2};
 items.sort((a,b)=>order[a.severity]-order[b.severity]||a.edgeId.localeCompare(b.edgeId));
 return {checked:items.length,errors:items.filter(x=>x.severity==='error').length,reviews:items.filter(x=>x.severity==='review').length,items};
}

// Panneau DOM facultatif : le clic transmet l'identifiant au contrôleur de sélection.
export function renderRouteClearancePanel(container,diagnostics,{onSelect=()=>{},filter="all"}={}){
 if(!["all","error","review"].includes(filter))throw new RangeError("Filtre de gravité invalide");
 if(!container||typeof container.replaceChildren!=='function')throw new TypeError('Conteneur DOM invalide');
 const view=buildRouteClearanceView(diagnostics);
 const doc=container.ownerDocument;
 const header=doc.createElement('h3');header.textContent=`Qualité des routes — ${view.errors} erreur(s), ${view.reviews} à examiner`;
 const list=doc.createElement('ul');
 for(const item of view.items.filter(x=>x.severity!=='ok'&&(filter==="all"||x.severity===filter))){
  const li=doc.createElement('li');const button=doc.createElement('button');
  button.type='button';button.textContent=`${item.edgeId} — ${item.label}`;
  button.setAttribute('aria-label',`Examiner la connexion ${item.edgeId}`);
  button.addEventListener('click',()=>onSelect(item.edgeId));li.append(button);list.append(li);
 }
 if(!list.childNodes.length){const li=doc.createElement('li');li.textContent=filter==='all'?'Aucune anomalie signalée':'Aucune anomalie pour ce filtre';list.append(li);}
 container.replaceChildren(header,list);return view;
}

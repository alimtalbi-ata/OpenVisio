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

// Navigation clavier du panneau : calcul pur, indépendant du DOM.
export function routeDiagnosticFocusIndex(current, key, count){
 if(!Number.isInteger(count)||count<=0)return -1;
 if(key==='Home')return 0;
 if(key==='End')return count-1;
 if(key==='ArrowDown')return (Math.max(-1,current)+1)%count;
 if(key==='ArrowUp')return current<=0?count-1:current-1;
 return -1;
}

// Panneau DOM facultatif : le clic transmet l'identifiant au contrôleur de sélection.
export function renderRouteClearancePanel(container,diagnostics,{onSelect=()=>{},filter="all",search="",selectedEdgeId=null}={}){
 if(!["all","error","review"].includes(filter))throw new RangeError("Filtre de gravité invalide");
 if(!container||typeof container.replaceChildren!=='function')throw new TypeError('Conteneur DOM invalide');
 const view=buildRouteClearanceView(diagnostics);
 const needle=String(search).trim().toLocaleLowerCase();
 const doc=container.ownerDocument;
 const header=doc.createElement('h3');header.textContent=`Qualité des routes — ${view.errors} erreur(s), ${view.reviews} à examiner`;
 const summary=doc.createElement('p');summary.textContent=`${view.checked} connexion(s) contrôlée(s) · ${view.errors} erreur(s) · ${view.reviews} à examiner`;summary.setAttribute('role','status');
 const list=doc.createElement('ul');list.setAttribute('aria-label','Connexions présentant des anomalies');
 const buttons=[];
 for(const item of view.items.filter(x=>x.severity!=='ok'&&(filter==="all"||x.severity===filter)&&(!needle||x.edgeId.toLocaleLowerCase().includes(needle)))){
  const li=doc.createElement('li');const button=doc.createElement('button');
  button.type='button';button.textContent=`${item.edgeId} — ${item.label}`;
  button.setAttribute('aria-label',`Examiner la connexion ${item.edgeId}`);
  if(selectedEdgeId!==null&&String(selectedEdgeId)===item.edgeId){button.setAttribute('aria-current','true');li.setAttribute('data-selected','true');}
  button.addEventListener('click',()=>onSelect(item.edgeId));buttons.push(button);li.append(button);list.append(li);
 }
 if(!list.childNodes.length){const li=doc.createElement('li');li.textContent=needle?'Aucune connexion correspondante':filter==='all'?'Aucune anomalie signalée':'Aucune anomalie pour ce filtre';list.append(li);}
 list.addEventListener('keydown',event=>{
  const index=buttons.indexOf(event.target);
  if(index<0)return;
  const next=routeDiagnosticFocusIndex(index,event.key,buttons.length);
  if(next<0)return;
  event.preventDefault?.();buttons[next].focus?.();
 });
 container.replaceChildren(header,summary,list);return view;
}

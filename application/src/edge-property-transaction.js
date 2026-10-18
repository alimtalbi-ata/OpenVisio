// OpenVisio v20.1 — validation transactionnelle des propriétés de liaison.
// Auteur : Abdelhalim Talbi
export function planEdgeProperty(edge,key,value,nodes){
 if(!edge)throw Error('Connexion introuvable');
 let next=value;
 if(key==='offset'){
  if(String(value).trim()==='')throw Error('Décalage vide');
  next=Number(value);
  if(!Number.isFinite(next))throw Error('Décalage non numérique');
 }
 if(key==='sourceInterface'||key==='targetInterface'){
  const id=key==='sourceInterface'?edge.from:edge.to;
  const node=nodes.find(n=>n.id===id);
  if(!node)throw Error('Équipement introuvable');
  if(value&&!(node.ports||[]).includes(value))throw Error('Interface non déclarée sur l’équipement');
 }
 return {ok:true,key,value:next,changed:JSON.stringify(edge[key])!==JSON.stringify(next)};
}
export function applyEdgeProperty(edge,plan){
 if(!plan?.ok)throw Error('Modification non validée');
 if(plan.changed)edge[plan.key]=plan.value;
 return plan.changed;
}

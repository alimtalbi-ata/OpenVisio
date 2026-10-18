// OpenVisio — Dimensions uniformes — Auteur : Abdelhalim Talbi
export function uniformDimensions(nodes,referenceId,mode){
 if(!['width','height','both'].includes(mode))throw Error('Mode de dimensionnement invalide');
 const ref=nodes.find(n=>n.id===referenceId);if(!ref)return [];
 if(![ref.w,ref.h].every(v=>Number.isFinite(v)&&v>0))throw Error('Dimensions de référence invalides');
 return nodes.filter(n=>n.id!==referenceId).map(n=>{
  if(![n.w,n.h].every(v=>Number.isFinite(v)&&v>0))throw Error('Dimensions de forme invalides');
  return [n,{w:mode==='height'?n.w:ref.w,h:mode==='width'?n.h:ref.h}];
 });
}

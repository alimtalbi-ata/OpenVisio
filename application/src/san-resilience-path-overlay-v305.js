// OpenVisio v30.5 — differentiated, non-destructive SAN scenario overlay. Auteur : Abdelhalim Talbi.
const CLASSES=['san-path-lost','san-path-surviving','san-path-shared','san-path-ambiguous'];
export function normalizePathOverlay(detail={}){
 const clean=xs=>[...new Set((Array.isArray(xs)?xs:[]).filter(x=>typeof x==='string'&&x.trim()))];
 const lost=clean(detail.lostIds),surviving=clean([... (detail.survivingIds||[]),...(detail.edgeIds||[])]),shared=clean(detail.sharedIds),ambiguous=clean(detail.ambiguousIds);
 // A shared dependency is higher risk than an otherwise surviving component.
 const states=new Map();for(const id of surviving)states.set(id,'san-path-surviving');for(const id of lost)states.set(id,'san-path-lost');for(const id of shared)states.set(id,'san-path-shared');for(const id of ambiguous)if(!states.has(id))states.set(id,'san-path-ambiguous');
 return states;
}
export function applyPathOverlay(root,detail={}){
 const states=normalizePathOverlay(detail);let count=0;
 if(!root?.querySelectorAll)return count;
 for(const el of root.querySelectorAll('[data-id], [data-object-id], [data-connection-id]')){
  const id=el.getAttribute('data-connection-id')||el.getAttribute('data-object-id')||el.getAttribute('data-id');
  for(const name of CLASSES)el.classList.remove(name);
  if(states.has(id)){el.classList.add(states.get(id));count++;}
 }
 return count;
}
if(typeof document!=='undefined'){
 let active={};const root=()=>document.getElementById('canvas')||document.querySelector('svg');
 document.addEventListener('openvisio:san-path-overlay',e=>{active=e.detail||{};applyPathOverlay(root(),active);});
 document.addEventListener('openvisio:canvas-painted',()=>applyPathOverlay(root(),active));
 document.addEventListener('openvisio:san-snapshot',()=>{active={};applyPathOverlay(root(),active);});
}

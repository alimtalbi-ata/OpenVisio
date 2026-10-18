// OpenVisio v30.2 — DOM-safe resilience focus. Auteur : Abdelhalim Talbi.
export const normalizeFocusIds=ids=>[...new Set((Array.isArray(ids)?ids:[]).filter(x=>typeof x==='string'&&x.trim()))];
export function applyResilienceFocus(root,ids){
 const selected=new Set(normalizeFocusIds(ids));let count=0;
 if(!root?.querySelectorAll)return count;
 for(const node of root.querySelectorAll('[data-id], [data-object-id], [data-connection-id]')){
  const key=node.getAttribute('data-id')||node.getAttribute('data-object-id')||node.getAttribute('data-connection-id');
  const active=selected.has(key);node.classList.toggle('san-resilience-focused',active);if(active)count++;
 }
 return count;
}
if(typeof document!=='undefined'){
 let active=[];
 const root=()=>document.getElementById('canvas')||document.querySelector('svg');
 document.addEventListener('openvisio:san-resilience-focus',e=>{active=normalizeFocusIds(e.detail?.ids);const count=applyResilienceFocus(root(),active);document.getElementById('sanResStatus')?.replaceChildren(document.createTextNode(`${count} éléments du canvas repérés · vérifiez les identifiants.`));});
 document.addEventListener('openvisio:san-resilience-repaint',()=>applyResilienceFocus(root(),active));
 document.addEventListener('openvisio:san-snapshot',()=>{active=[];applyResilienceFocus(root(),active);});
}

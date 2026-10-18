// OpenVisio — transformations vectorielles. Auteur : Abdelhalim Talbi.
export function normalizeAngle(value){const n=Number(value);if(!Number.isFinite(n))throw new Error('Angle invalide');return ((n%360)+360)%360;}
export function transformNodes(nodes,operation,{degrees=90}={}){
 if(!Array.isArray(nodes))throw new TypeError('Sélection invalide');
 if(!['rotate','flipH','flipV','reset'].includes(operation))throw new Error('Transformation inconnue');
 const angle=operation==='rotate'?normalizeAngle(degrees):0;
 return nodes.map(node=>{
  const n={...node};
  if(operation==='rotate')n.rotation=normalizeAngle((Number(n.rotation)||0)+angle);
  if(operation==='flipH')n.flipH=!Boolean(n.flipH);
  if(operation==='flipV')n.flipV=!Boolean(n.flipV);
  if(operation==='reset'){n.rotation=0;n.flipH=false;n.flipV=false;}
  return n;
 });
}
export function svgNodeTransform(node){
 const x=Number(node.x),y=Number(node.y),w=Number(node.w),h=Number(node.h);
 if(![x,y,w,h].every(Number.isFinite)||w<=0||h<=0)throw new Error('Géométrie invalide');
 const angle=normalizeAngle(node.rotation||0);
 const sx=node.flipH?-1:1,sy=node.flipV?-1:1;
 return `translate(${x} ${y}) translate(${w/2} ${h/2}) rotate(${angle}) scale(${sx} ${sy}) translate(${-w/2} ${-h/2})`;
}

// OpenVisio — Guides magnétiques de dessin — Auteur : Abdelhalim Talbi
// Pure geometry: no DOM or global state.
const bounds=n=>({left:n.x,right:n.x+(n.w||0),cx:n.x+(n.w||0)/2,top:n.y,bottom:n.y+(n.h||0),cy:n.y+(n.h||0)/2});
export function magneticSnap(moving,others,{threshold=7,grid=0}={}){
 if(!moving||!Number.isFinite(moving.x)||!Number.isFinite(moving.y))throw Error('Position invalide');
 const source=bounds(moving), candidates={x:[],y:[]};
 for(const other of others||[]){if(!other||other.id===moving.id||![other.x,other.y].every(Number.isFinite))continue;
  const b=bounds(other);
  for(const a of ['left','cx','right'])for(const c of ['left','cx','right'])candidates.x.push({delta:b[c]-source[a],at:b[c],target:other.id,kind:a+'→'+c});
  for(const a of ['top','cy','bottom'])for(const c of ['top','cy','bottom'])candidates.y.push({delta:b[c]-source[a],at:b[c],target:other.id,kind:a+'→'+c});
 }
 const choose=axis=>candidates[axis].filter(c=>Math.abs(c.delta)<=threshold).sort((a,b)=>Math.abs(a.delta)-Math.abs(b.delta)||String(a.target).localeCompare(String(b.target)))[0];
 const x=choose('x'),y=choose('y');
 const quantize=v=>grid>0?Math.round(v/grid)*grid:v;
 return {x:x?moving.x+x.delta:quantize(moving.x),y:y?moving.y+y.delta:quantize(moving.y),guides:[...(x?[{axis:'x',position:x.at,target:x.target,kind:x.kind}]:[]),...(y?[{axis:'y',position:y.at,target:y.target,kind:y.kind}]:[])]};
}
export function alignToReference(nodes,referenceId,axis){
 if(!['left','right','top','bottom','centerX','centerY'].includes(axis))throw Error('Axe invalide');
 const ref=nodes.find(n=>n.id===referenceId);if(!ref)return false;
 const r=bounds(ref);for(const n of nodes){if(n.id===referenceId)continue;
 if(axis==='left')n.x=r.left;else if(axis==='right')n.x=r.right-(n.w||0);
 else if(axis==='top')n.y=r.top;else if(axis==='bottom')n.y=r.bottom-(n.h||0);
 else if(axis==='centerX')n.x=r.cx-(n.w||0)/2;else n.y=r.cy-(n.h||0)/2;
 n.x=Math.max(0,n.x);n.y=Math.max(0,n.y);
 }return true;
}

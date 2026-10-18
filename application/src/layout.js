// OpenVisio — Auteur : Abdelhalim Talbi
// Mutations géométriques déterministes sur les seuls objets sélectionnés.
export function arrangeNodes(nodes, mode, {grid=0,gap=24}={}) {
 if(!Array.isArray(nodes)||nodes.length<2)return false;
 const snap=v=>grid>0?Math.round(v/grid)*grid:v;
 const sorted=(axis)=>[...nodes].sort((a,b)=>(a[axis]-b[axis])||String(a.id).localeCompare(String(b.id)));
 const width=n=>Math.max(0,Number(n.w)||0), height=n=>Math.max(0,Number(n.h)||0);
 if(mode==='alignLeft'){const x=Math.min(...nodes.map(n=>n.x));nodes.forEach(n=>n.x=snap(x));}
 else if(mode==='alignTop'){const y=Math.min(...nodes.map(n=>n.y));nodes.forEach(n=>n.y=snap(y));}
 else if(mode==='alignCenterX'){const centers=nodes.map(n=>n.x+width(n)/2);const center=(Math.min(...centers)+Math.max(...centers))/2;nodes.forEach(n=>n.x=Math.max(0,snap(center-width(n)/2)));}
 else if(mode==='alignCenterY'){const centers=nodes.map(n=>n.y+height(n)/2);const center=(Math.min(...centers)+Math.max(...centers))/2;nodes.forEach(n=>n.y=Math.max(0,snap(center-height(n)/2)));}
 else if(mode==='distributeX'||mode==='distributeY'){
  if(nodes.length<3)return false;
  const axis=mode==='distributeX'?'x':'y', size=axis==='x'?width:height, arr=sorted(axis);
  const first=arr[0][axis], last=arr.at(-1)[axis]+size(arr.at(-1));
  const total=arr.reduce((sum,n)=>sum+size(n),0);
  const spacing=(last-first-total)/(arr.length-1);
  let cursor=first;
  for(const n of arr){n[axis]=Math.max(0,snap(cursor));cursor+=size(n)+spacing;}
 }
 else if(mode==='distributeSafeX'||mode==='distributeSafeY'){
  // Preserve ordering and starting position; never create overlaps even if
  // the original bounding box is too small for the selected shapes.
  const axis=mode==='distributeSafeX'?'x':'y',size=axis==='x'?width:height,arr=sorted(axis);
  const start=Math.max(0,arr[0][axis]);
  const extent=Math.max(...arr.map(n=>n[axis]+size(n)));
  const occupied=arr.reduce((sum,n)=>sum+size(n),0);
  const desiredGap=Math.max(gap,(extent-start-occupied)/(arr.length-1));
  let cursor=snap(start);
  for(const n of arr){
   const position=Math.max(0,snap(cursor));
   n[axis]=position;
   cursor=position+size(n)+desiredGap;
  }
 }
 else if(mode==='stackX'||mode==='stackY'){
  const axis=mode==='stackX'?'x':'y',size=axis==='x'?width:height,arr=sorted(axis);
  let cursor=Math.min(...arr.map(n=>n[axis]));
  for(const n of arr){n[axis]=Math.max(0,snap(cursor));cursor+=size(n)+gap;}
 }else return false;
 return true;
}

// v40.7 : placement en grille sans chevauchement, déterministe et borné.
// Le calcul est pur : aucun noeud d'entrée n'est modifié.
export function planCollisionFreeGrid(nodes,{columns=0,gap=24,originX=0,originY=0,maxNodes=10000}={}) {
 if(!Array.isArray(nodes)||nodes.length>maxNodes)throw Error('Invalid node count');
 if(![columns,gap,originX,originY].every(Number.isFinite)||gap<0||gap>10000||columns<0||!Number.isInteger(columns))throw Error('Invalid grid options');
 if(nodes.some(n=>!n||![n.x,n.y,n.w,n.h].every(Number.isFinite)||n.w<=0||n.h<=0||n.w>1e6||n.h>1e6))throw Error('Invalid node geometry');
 if(!nodes.length)return [];
 const ids=new Set();for(const n of nodes){const id=String(n.id);if(ids.has(id))throw Error('Duplicate node id');ids.add(id);}
 const count=Math.min(nodes.length,columns||Math.max(1,Math.ceil(Math.sqrt(nodes.length))));
 const widths=Array(count).fill(0),heights=[];
 nodes.forEach((n,i)=>{const col=i%count,row=Math.floor(i/count);widths[col]=Math.max(widths[col],n.w);heights[row]=Math.max(heights[row]||0,n.h);});
 const xs=[],ys=[];let x=originX,y=originY;
 widths.forEach((w,i)=>{xs[i]=x;x+=w+gap;});heights.forEach((h,i)=>{ys[i]=y;y+=h+gap;});
 return nodes.map((n,i)=>({id:n.id,x:xs[i%count],y:ys[Math.floor(i/count)],w:n.w,h:n.h}));
}
export function applyGridPlan(nodes,plan){
 if(!Array.isArray(nodes)||!Array.isArray(plan)||nodes.length!==plan.length)throw Error('Invalid grid plan');
 const positions=new Map(plan.map(p=>[String(p.id),p]));
 if(positions.size!==nodes.length||nodes.some(n=>!positions.has(String(n.id))))throw Error('Grid plan mismatch');
 for(const n of nodes){const p=positions.get(String(n.id));if(!Number.isFinite(p.x)||!Number.isFinite(p.y))throw Error('Invalid plan coordinates');}
 for(const n of nodes){const p=positions.get(String(n.id));n.x=p.x;n.y=p.y;}
 return nodes;
}

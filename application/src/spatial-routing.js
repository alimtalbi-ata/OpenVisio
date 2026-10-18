// OpenVisio v17.2 — analyse spatiale conservative des dépendances du routage.
// Auteur : Abdelhalim Talbi
const bounds=n=>({left:n.x,top:n.y,right:n.x+n.w,bottom:n.y+n.h});
const expanded=(b,p)=>({left:b.left-p,top:b.top-p,right:b.right+p,bottom:b.bottom+p});
const overlap=(a,b)=>a.left<=b.right&&a.right>=b.left&&a.top<=b.bottom&&a.bottom>=b.top;
export function routeBounds(route){
 const points=route?.points;
 if(!Array.isArray(points)||points.length===0)return null;
 let left=Infinity,right=-Infinity,top=Infinity,bottom=-Infinity;
 for(const point of points){
  if(!point||!Number.isFinite(point.x)||!Number.isFinite(point.y))return null;
  if(point.x<left)left=point.x;
  if(point.x>right)right=point.x;
  if(point.y<top)top=point.y;
  if(point.y>bottom)bottom=point.y;
 }
 return {left,top,right,bottom};
}
// Test segment/rectangle rather than only the overall bounding box:
// an L-shaped connection can have a large empty bounding region.
export function routeIntersectsZone(route,zone){
 if(!route?.points?.length)return true;
 const points=route.points;
 const inside=p=>p.x>=zone.left&&p.x<=zone.right&&p.y>=zone.top&&p.y<=zone.bottom;
 if(points.some(inside))return true;
 for(let i=1;i<points.length;i++){
  const a=points[i-1],b=points[i];
  // Liang-Barsky clipping works for diagonal as well as orthogonal segments.
  const dx=b.x-a.x,dy=b.y-a.y;
  const ps=[-dx,dx,-dy,dy],qs=[a.x-zone.left,zone.right-a.x,a.y-zone.top,zone.bottom-a.y];
  let t0=0,t1=1,hit=true;
  for(let j=0;j<4;j++){
   if(ps[j]===0){if(qs[j]<0){hit=false;break;}continue;}
   const t=qs[j]/ps[j];
   if(ps[j]<0)t0=Math.max(t0,t);else t1=Math.min(t1,t);
   if(t0>t1){hit=false;break;}
  }
  if(hit)return true;
 }
 return false;
}
// Index grille réutilisable : construction O(segments), requêtes locales sans balayage global.
// Les Maps de routes sont mutables : un cache par identité devient obsolète après édition.
// Recalcul conservateur par invocation jusqu’à introduction d’un compteur de révision fiable.
export function buildRouteSpatialIndex(routes,{cellSize=128}={}){
 if(!Number.isFinite(cellSize)||cellSize<=0)throw Error('Invalid spatial cell size');
 const cells=new Map(),unknown=new Set();
 for(const [id,route] of routes||[]){
  const b=routeBounds(route);
  if(!b||![b.left,b.right,b.top,b.bottom].every(Number.isFinite)){unknown.add(id);continue;}
  const x0=Math.floor(b.left/cellSize),x1=Math.floor(b.right/cellSize),y0=Math.floor(b.top/cellSize),y1=Math.floor(b.bottom/cellSize);
  // Large extents are treated conservatively without creating millions of cells.
  if((x1-x0+1)*(y1-y0+1)>4096){unknown.add(id);continue;}
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++){
   const key=`${x}:${y}`;if(!cells.has(key))cells.set(key,new Set());cells.get(key).add(id);
  }
 }
 return {cells,unknown,cellSize};
}
// Cache explicite: la révision documentaire seule ne prouve PAS la révision des routes.
// Le producteur doit incrémenter routeRevision après CHAQUE mutation de la Map.
// Sans revision fiable, le chemin conservateur reconstruit toujours l'index.
export function createRevisionedRouteIndex({cellSize=128}={}){
 if(!Number.isFinite(cellSize)||cellSize<=0)throw Error('Invalid spatial cell size');
 let lastRoutes=null,lastRevision=null,lastIndex=null;
 let builds=0,hits=0;
 return Object.freeze({
  get(routes,revision){
   if(!(routes instanceof Map))throw Error('Routes must be a Map');
   if(!Number.isSafeInteger(revision)||revision<0)throw Error('Revision must be a nonnegative safe integer');
   if(routes===lastRoutes&&revision===lastRevision){hits++;return lastIndex;}
   lastIndex=buildRouteSpatialIndex(routes,{cellSize});lastRoutes=routes;lastRevision=revision;builds++;
   return lastIndex;
  },
  invalidate(){lastRoutes=null;lastRevision=null;lastIndex=null;},
  stats(){return {builds,hits};}
 });
}
export function queryRouteSpatialIndex(index,zones){
 const ids=new Set(index.unknown),size=index.cellSize;
 for(const z of zones){
  const x0=Math.floor(z.left/size),x1=Math.floor(z.right/size),y0=Math.floor(z.top/size),y1=Math.floor(z.bottom/size);
  if((x1-x0+1)*(y1-y0+1)>4096){for(const cell of index.cells.values())for(const id of cell)ids.add(id);continue;}
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(const id of index.cells.get(`${x}:${y}`)||[])ids.add(id);
 }
 return ids;
}
export function spatialRoutingImpact(previousState,nextState,previousRoutes,{margin=24,routeIndexCache=null,routeRevision=null}={}){
 if(!Number.isFinite(margin)||margin<0)throw Error('Invalid spatial margin');
 const oldNodes=new Map((previousState?.nodes||[]).map(n=>[n.id,n]));
 const newNodes=new Map((nextState?.nodes||[]).map(n=>[n.id,n]));
 const oldEdges=new Map((previousState?.edges||[]).map(e=>[e.id,e]));
 const newEdges=new Map((nextState?.edges||[]).map(e=>[e.id,e]));
 const changedNodes=new Set(),changedEdges=new Set(),zones=[];
 for(const id of new Set([...oldNodes.keys(),...newNodes.keys()])){
  const a=oldNodes.get(id),b=newNodes.get(id);
  const geometry=n=>n&&[n.x,n.y,n.w,n.h,n.rotation,n.flipH,n.flipV,n.ports,n.interfaces];
  if(JSON.stringify(geometry(a))===JSON.stringify(geometry(b)))continue;
  changedNodes.add(id);
  if(a)zones.push(expanded(bounds(a),margin));
  if(b)zones.push(expanded(bounds(b),margin));
 }
 for(const id of new Set([...oldEdges.keys(),...newEdges.keys()])){
  const a=oldEdges.get(id),b=newEdges.get(id);
  const geometry=e=>e&&[e.from,e.to,e.style,e.offset,e.waypoints,e.fromPort,e.toPort,e.sourceInterface,e.targetInterface];
  if(JSON.stringify(geometry(a))!==JSON.stringify(geometry(b)))changedEdges.add(id);
 }
 for(const e of [...oldEdges.values(),...newEdges.values()]){
  if(changedNodes.has(e.from)||changedNodes.has(e.to))changedEdges.add(e.id);
 }
 const candidates=zones.length&&previousRoutes instanceof Map ? (()=>{
  const index=routeIndexCache && routeRevision!==null ? routeIndexCache.get(previousRoutes,routeRevision) : buildRouteSpatialIndex(previousRoutes);
  return queryRouteSpatialIndex(index,zones);
 })():null;
 // Un chemin qui traverse l'ancienne ou la nouvelle emprise peut nécessiter un reroutage.
 // Une route absente est traitée comme dépendance inconnue : invalidation conservative.
 for(const e of newEdges.values()){
  if(changedEdges.has(e.id))continue;
  if(candidates&&!candidates.has(e.id)&&previousRoutes.has(e.id))continue;
  const r=previousRoutes?.get(e.id),rb=routeBounds(r);
  if(!rb||zones.some(z=>overlap(z,rb)&&routeIntersectsZone(r,z)))changedEdges.add(e.id);
 }
 return {changedNodes,changedEdges,zones,requiresGlobalRebalance:changedNodes.size>0||changedEdges.size>0};
}


// V23.5 — qualification conservative d'un recalcul partiel de routes SAN.
// Le moteur ne peut utiliser une mise à jour locale que si les dépendances sont prouvées.
export function qualifyLocalRouteUpdate(previousState,nextState,previousRoutes,{margin=24,maxChangedEdges=64}={}){
 if(!(previousRoutes instanceof Map)||!Number.isInteger(maxChangedEdges)||maxChangedEdges<1)throw Error('Invalid local routing qualification');
 const impact=spatialRoutingImpact(previousState,nextState,previousRoutes,{margin});
 const oldEdges=new Map((previousState?.edges||[]).map(e=>[e.id,e]));
 const newEdges=new Map((nextState?.edges||[]).map(e=>[e.id,e]));
 const reasons=[];
 if(impact.changedEdges.size>1&&impact.changedNodes.size>0)reasons.push('multi-edge-local-dependency-unverified');
 if(impact.changedEdges.size>maxChangedEdges)reasons.push('edge-budget-exceeded');
 if(oldEdges.size!==newEdges.size||[...oldEdges.keys()].some(id=>!newEdges.has(id)))reasons.push('topology-changed');
 if(impact.changedNodes.size>1)reasons.push('multi-node-change');
 for(const [id,e] of newEdges){
  const route=previousRoutes.get(id);
  if(!route?.points?.length||route.points.some(p=>!Number.isFinite(p?.x)||!Number.isFinite(p?.y)))reasons.push('missing-or-invalid-route');
  if(impact.changedEdges.has(id)&&(e?.waypoints?.length||e?.sourceInterface||e?.targetInterface))reasons.push('pinned-or-interface-route');
 }
 // Le rééquilibrage global des faisceaux peut dépendre des routes non touchées.
 if(impact.changedEdges.size>0&&newEdges.size>impact.changedEdges.size){
  // Preuve conservative : un seul câble modifié, aucune extrémité partagée,
  // aucun itinéraire tiers dans les anciennes/nouvelles zones d'impact.
  const changed=[...impact.changedEdges];
  const target=newEdges.get(changed[0]);
  const independent=changed.length===1&&!!target&&impact.changedNodes.size<=1&&
    [...newEdges.values()].every(e=>e.id===target.id||
      (e.from!==target.from&&e.from!==target.to&&e.to!==target.from&&e.to!==target.to))&&
    [...newEdges.keys()].every(id=>id===target.id||
      !impact.zones.some(z=>routeIntersectsZone(previousRoutes.get(id),z)));
  if(!independent)reasons.push('global-bundle-dependency-unverified');
}
 const unique=[...new Set(reasons)];
 return {eligible:unique.length===0,mode:unique.length?'full-recompute':'local-candidate',reasons:unique,changedNodes:[...impact.changedNodes].sort(),changedEdges:[...impact.changedEdges].sort(),affectedZones:impact.zones.length};
}

// V41.6 — ownership profond : aucune référence mutable d'une route ne traverse l'API.
// structuredClone échoue avant toute mutation pour une valeur non clonable.
const cloneRouteValue=value=>structuredClone(value);
const cloneRouteMap=input=>{
 if(!(input instanceof Map))throw TypeError('Routes must be a Map');
 const result=new Map();
 for(const [id,route] of input)result.set(id,cloneRouteValue(route));
 return result;
};
export function createRouteStore(initialRoutes=new Map()){
 let routes=cloneRouteMap(initialRoutes),revision=0;
 const bump=()=>{if(revision===Number.MAX_SAFE_INTEGER)throw RangeError('Route revision overflow');revision++;};
 return Object.freeze({
  get revision(){return revision;},
  get size(){return routes.size;},
  get(id){return routes.has(id)?cloneRouteValue(routes.get(id)):undefined;},
  snapshot(){return cloneRouteMap(routes);},
  set(id,route){const safe=cloneRouteValue(route);bump();routes.set(id,safe);return revision;},
  delete(id){if(!routes.has(id))return false;bump();return routes.delete(id);},
  clear(){if(!routes.size)return false;bump();routes.clear();return true;},
  replace(next){const copy=cloneRouteMap(next);bump();routes=copy;return revision;},
  // La Map interne n'est jamais exposée. Seul le cache reçoit la référence interne.
  index(cache){if(!cache||typeof cache.get!=='function')throw TypeError('Invalid index cache');return cache.get(routes,revision);}
 });
}

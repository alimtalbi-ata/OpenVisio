// OpenVisio v25.2 — corrections SAN groupées, explicites et transactionnelles.
// Auteur : Abdelhalim Talbi
import {proposeRouteOffset,routeRevision,safeRouteCommit} from './route-preview.js';
import {routeSharedLength,countRouteCrossings} from './routing.js';
const edgeId=e=>String(e.id);
const fabric=e=>String(e.fabric||'').trim().toUpperCase();
// Distance minimale entre deux polylignes orthogonales, en unités SVG.
// Les croisements et contacts retournent zéro ; les segments disjoints
// utilisent la distance euclidienne exacte entre segments axis-aligned.
export function routeClearance(a,b){
 const valid=path=>Array.isArray(path)&&path.length>=2&&path.every(p=>p&&Number.isFinite(p.x)&&Number.isFinite(p.y));
 if(!valid(a)||!valid(b))throw Error('Tracé de séparation invalide');
 const segments=points=>points.slice(1).map((p,i)=>[points[i],p]);
 const pointDistance=(p,u,v)=>{
  const dx=v.x-u.x,dy=v.y-u.y,den=dx*dx+dy*dy;
  const t=den?Math.max(0,Math.min(1,((p.x-u.x)*dx+(p.y-u.y)*dy)/den)):0;
  return Math.hypot(p.x-u.x-t*dx,p.y-u.y-t*dy);
 };
 let minimum=Infinity;
 for(const [u,v] of segments(a))for(const [x,y] of segments(b)){
  const cross=(p,q,r)=>(q.x-p.x)*(r.y-p.y)-(q.y-p.y)*(r.x-p.x);
  const c1=cross(u,v,x),c2=cross(u,v,y),c3=cross(x,y,u),c4=cross(x,y,v);
  const intersects=(c1*c2<=0&&c3*c4<=0&&
   Math.max(Math.min(u.x,v.x),Math.min(x.x,y.x))<=Math.min(Math.max(u.x,v.x),Math.max(x.x,y.x))&&
   Math.max(Math.min(u.y,v.y),Math.min(x.y,y.y))<=Math.min(Math.max(u.y,v.y),Math.max(x.y,y.y)));
  if(intersects)return 0;
  minimum=Math.min(minimum,pointDistance(u,x,y),pointDistance(v,x,y),pointDistance(x,u,v),pointDistance(y,u,v));
 }
 return minimum;
}
export function batchFingerprint(edges,nodes){
 return JSON.stringify([...edges].sort((a,b)=>edgeId(a).localeCompare(edgeId(b))).map(e=>routeRevision(e,nodes)));
}
// v25.7 — garde des routes existantes : une proposition ne doit pas
// introduire de nouvelle violation d’espacement avec une Fabric opposée.
// Une violation déjà présente ne doit pas non plus être aggravée.
export function checkExistingFabricRoutes(edge,proposal,routes,edges,{minimum=8}={}){
 if(!edge||!proposal||!Array.isArray(proposal.points)||!(routes instanceof Map)||!Array.isArray(edges)||!Number.isFinite(minimum)||minimum<0||minimum>100)throw Error('Contrôle de proximité invalide');
 const fa=fabric(edge), current=routes.get(edgeId(edge))?.points;
 if(!['A','B'].includes(fa))return {safe:true,violations:[],checked:0};
 if(!Array.isArray(current)||current.length<2)return {safe:false,violations:[{reason:'Tracé initial absent'}],checked:0};
 const violations=[];let checked=0;
 for(const other of edges){
  const fb=fabric(other);
  if(edgeId(other)===edgeId(edge)||!['A','B'].includes(fb)||fa===fb)continue;
  const path=routes.get(edgeId(other))?.points;
  if(!Array.isArray(path)||path.length<2){violations.push({edgeId:edgeId(other),reason:'Tracé opposé absent'});continue;}
  try{
   const before=routeClearance(current,path),after=routeClearance(proposal.points,path);checked++;
   if(after<minimum&& (before>=minimum||after<before-1e-7))violations.push({edgeId:edgeId(other),before,after,reason:'FABRIC_AB_EXISTING_REGRESSION'});
  }catch{violations.push({edgeId:edgeId(other),reason:'Tracé opposé invalide'});}
 }
 return {safe:violations.length===0,violations,checked};
}
export function prepareRouteBatch(edges,nodes,routes,{limit=30,fabricClearance=0}={}){
 if(!Array.isArray(edges)||!Array.isArray(nodes)||!(routes instanceof Map)||!Number.isInteger(limit)||limit<1||limit>100||!Number.isFinite(fabricClearance)||fabricClearance<0||fabricClearance>100)throw Error('Lot invalide');
 const selected=edges.slice(0,limit),seen=new Set(),proposals=[],skipped=[];
 for(const edge of selected){
  if(seen.has(edgeId(edge))){skipped.push({edgeId:edgeId(edge),reason:'Doublon'});continue;}
  seen.add(edgeId(edge));
  const p=proposeRouteOffset(edge,nodes,routes);
  if(p.status==='preview'){
   const guard=checkExistingFabricRoutes(edge,p,routes,edges,{minimum:fabricClearance});
   if(guard.safe)proposals.push({...p,revision:routeRevision(edge,nodes)});
   else skipped.push({edgeId:edgeId(edge),reason:'Conflit avec Fabric existante',violations:guard.violations});
  }
  else skipped.push({edgeId:edgeId(edge),reason:p.reason||p.status});
 }
 const conflicts=[];
 for(let i=0;i<proposals.length;i++)for(let j=i+1;j<proposals.length;j++){
  const a=proposals[i],b=proposals[j];
  const shared=routeSharedLength({points:a.points},{points:b.points});
  const crossings=countRouteCrossings([{points:a.points},{points:b.points}]);
  const fa=fabric(edges.find(e=>edgeId(e)===a.edgeId)),fb=fabric(edges.find(e=>edgeId(e)===b.edgeId));
  const crossFabric=['A','B'].includes(fa)&&['A','B'].includes(fb)&&fa!==fb;
  const clearance=crossFabric?routeClearance(a.points,b.points):null;
  if(shared>0||crossings>0||(crossFabric&&clearance<fabricClearance))conflicts.push({a:a.edgeId,b:b.edgeId,shared,crossings,clearance,crossFabric,reason:crossFabric?'FABRIC_AB_INTERFERENCE':'ROUTE_INTERFERENCE'});
 }
 const fabricWarnings=conflicts.filter(c=>c.crossFabric);
 return {proposals,skipped,conflicts,fabricWarnings,fingerprint:batchFingerprint(edges,nodes),total:edges.length,truncated:edges.length>limit};
}
export function commitRouteBatch(edges,nodes,batch,selectedIds){
 if(!batch||!Array.isArray(batch.proposals)||!Array.isArray(batch.conflicts)||!(selectedIds instanceof Set))throw Error('Validation de lot invalide');
 if(batchFingerprint(edges,nodes)!==batch.fingerprint)throw Error('Lot obsolète : topologie modifiée');
 const selected=batch.proposals.filter(p=>selectedIds.has(p.edgeId));
 if(!selected.length)throw Error('Aucune correction sélectionnée');
 if(batch.conflicts.some(c=>selectedIds.has(c.a)&&selectedIds.has(c.b)))throw Error('Conflit entre corrections sélectionnées');
 // Pré-validation complète avant toute mutation : aucune application partielle.
 for(const p of selected){const e=edges.find(x=>edgeId(x)===p.edgeId);if(!e||routeRevision(e,nodes)!==p.revision)throw Error('Proposition obsolète');}
 const changes=selected.map(p=>({edgeId:p.edgeId,before:edges.find(e=>edgeId(e)===p.edgeId).offset,after:p.offset}));
 for(const p of selected)safeRouteCommit(edges.find(e=>edgeId(e)===p.edgeId),p,nodes,p.revision);
 return changes;
}


// v25.4 — sélection globale déterministe d'un sous-ensemble sans conflit.
// L'optimisation n'applique aucune mutation ; le commit reste transactionnel.
export function optimizeRouteBatch(batch,{fabricPriority=2}={}){
 if(!batch||!Array.isArray(batch.proposals)||!Array.isArray(batch.conflicts)||!Number.isFinite(fabricPriority)||fabricPriority<1||fabricPriority>20)throw Error('Optimisation de lot invalide');
 const byId=new Map(),adjacency=new Map();
 for(const p of batch.proposals){
  if(typeof p?.edgeId!=='string'||!p.edgeId||byId.has(p.edgeId)||!Number.isFinite(p.before?.score)||!Number.isFinite(p.after?.score))throw Error('Proposition de routage invalide ou dupliquée');
  byId.set(p.edgeId,p);adjacency.set(p.edgeId,new Set());
 }
 for(const c of batch.conflicts){
  if(!c||typeof c.a!=='string'||typeof c.b!=='string')throw Error('Conflit de routage invalide');
  if(!adjacency.has(c.a)||!adjacency.has(c.b))continue;
  adjacency.get(c.a).add(c.b);adjacency.get(c.b).add(c.a);
 }
 const benefit=id=>Math.max(0,byId.get(id).before.score-byId.get(id).after.score);
 const components=[],visited=new Set();
 for(const id of [...byId.keys()].sort()){
  if(visited.has(id))continue;
  const stack=[id],component=[];visited.add(id);
  while(stack.length){const next=stack.pop();component.push(next);for(const neighbor of adjacency.get(next))if(!visited.has(neighbor)){visited.add(neighbor);stack.push(neighbor);}}
  components.push(component.sort());
 }
 const selected=new Set();let exactComponents=0,heuristicComponents=0;
 for(const ids of components){
  if(ids.length<=18){
   exactComponents++;
   const weights=ids.map(benefit);
   const neighbors=ids.map(id=>ids.reduce((mask,other,j)=>adjacency.get(id).has(other)?mask|(1<<j):mask,0));
   let bestScore=-1,bestIds=[];
   const search=(available,chosen,score)=>{
    if(!available){
     const chosenIds=chosen.map(i=>ids[i]);
     if(score>bestScore+1e-9||(Math.abs(score-bestScore)<=1e-9&&(chosenIds.length>bestIds.length||(chosenIds.length===bestIds.length&&chosenIds.join(',')<bestIds.join(','))))){bestScore=score;bestIds=chosenIds;}
     return;
    }
    let upper=score;for(let i=0;i<ids.length;i++)if(available&(1<<i))upper+=weights[i];
    if(upper<bestScore-1e-9)return;
    const bit=available&-available,i=Math.log2(bit)|0;
    if(weights[i]>0)search(available&~bit&~neighbors[i],[...chosen,i],score+weights[i]);
    search(available&~bit,chosen,score);
   };
   search((1<<ids.length)-1,[],0);
   for(const id of bestIds)selected.add(id);
  }else{
   heuristicComponents++;
   const orders=[
    [...ids].sort((a,b)=>benefit(b)-benefit(a)||adjacency.get(a).size-adjacency.get(b).size||a.localeCompare(b)),
    [...ids].sort((a,b)=>adjacency.get(a).size-adjacency.get(b).size||benefit(b)-benefit(a)||a.localeCompare(b))
   ];
   const candidates=orders.map(order=>{const chosen=new Set();for(const id of order)if(benefit(id)>0&&![...adjacency.get(id)].some(other=>chosen.has(other)))chosen.add(id);return {chosen,score:[...chosen].reduce((sum,id)=>sum+benefit(id),0)};});
   candidates.sort((a,b)=>b.score-a.score||b.chosen.size-a.chosen.size||[...a.chosen].sort().join(',').localeCompare([...b.chosen].sort().join(',')));
   for(const id of candidates[0].chosen)selected.add(id);
  }
 }
 const selectedIds=[...selected].sort();
 return {selectedIds,estimatedGain:selectedIds.reduce((sum,id)=>sum+benefit(id),0),excludedIds:[...byId.keys()].filter(id=>!selected.has(id)).sort(),conflictsAvoided:batch.conflicts.filter(c=>selected.has(c.a)||selected.has(c.b)).length,mode:heuristicComponents?'conservative-greedy':'exact-bounded',exactComponents,heuristicComponents,fabricPriority};
}

// v25.6 — audit des routes existantes : aucune modification du diagramme.
export function auditExistingFabricClearance(edges,routes,{minimum=8,limit=250}={}){
 if(!Array.isArray(edges)||!(routes instanceof Map)||!Number.isFinite(minimum)||minimum<0||minimum>100||!Number.isInteger(limit)||limit<1||limit>1000)throw Error('Audit Fabrics invalide');
 const examined=edges.slice(0,limit),findings=[],skipped=[];
 for(let i=0;i<examined.length;i++){
  const a=examined[i],fa=fabric(a);
  if(!['A','B'].includes(fa))continue;
  for(let j=i+1;j<examined.length;j++){
   const b=examined[j],fb=fabric(b);
   if(!['A','B'].includes(fb)||fa===fb)continue;
   const pa=routes.get(edgeId(a)),pb=routes.get(edgeId(b));
   if(!pa||!pb){skipped.push({a:edgeId(a),b:edgeId(b),reason:'Tracé absent'});continue;}
   try{
    const clearance=routeClearance(pa,pb);
    if(clearance<minimum)findings.push({a:edgeId(a),b:edgeId(b),fabricA:fa,fabricB:fb,clearance,minimum,code:'FABRIC_AB_EXISTING_CLEARANCE'});
   }catch{skipped.push({a:edgeId(a),b:edgeId(b),reason:'Tracé invalide'});}
  }
 }
 return {findings,skipped,examined:examined.length,truncated:edges.length>limit,minimum,pass:findings.length===0&&skipped.length===0&&! (edges.length>limit)};
}

// v27.1 — projection pure et déterministe pour le cockpit de conflits.
export function describeRouteBatchConflicts(batch,selectedIds=new Set()){
 if(!batch||!Array.isArray(batch.proposals)||!Array.isArray(batch.conflicts)||!(selectedIds instanceof Set))throw Error('Visualisation de conflits invalide');
 const ids=new Set();const graph=new Map();
 for(const p of batch.proposals){if(typeof p?.edgeId!=='string'||!p.edgeId||ids.has(p.edgeId))throw Error('Identifiant de proposition invalide');ids.add(p.edgeId);graph.set(p.edgeId,new Set());}
 const pairs=new Set(),conflicts=[];
 for(const c of batch.conflicts){
  if(!c||typeof c.a!=='string'||typeof c.b!=='string'||!ids.has(c.a)||!ids.has(c.b)||c.a===c.b)throw Error('Conflit de routage invalide');
  const [a,b]=[c.a,c.b].sort(),key=JSON.stringify([a,b]);if(pairs.has(key))continue;pairs.add(key);
  graph.get(a).add(b);graph.get(b).add(a);
  conflicts.push({a,b,active:selectedIds.has(a)&&selectedIds.has(b),crossFabric:!!c.crossFabric,reason:c.reason||'ROUTE_INTERFERENCE'});
 }
 conflicts.sort((a,b)=>a.a.localeCompare(b.a)||a.b.localeCompare(b.b));
 const visited=new Set(),groups=[];
 for(const id of [...ids].sort()){
  if(visited.has(id))continue;const stack=[id],members=[];visited.add(id);
  while(stack.length){const next=stack.pop();members.push(next);for(const other of [...graph.get(next)].sort())if(!visited.has(other)){visited.add(other);stack.push(other);}}
  members.sort();const subset=new Set(members);
  groups.push({id:groups.length+1,edgeIds:members,conflicts:conflicts.filter(c=>subset.has(c.a)&&subset.has(c.b)).length,selected:members.filter(x=>selectedIds.has(x)).length});
 }
 return {groups,conflicts,activeConflicts:conflicts.filter(c=>c.active),valid:conflicts.every(c=>!c.active),selectedCount:[...ids].filter(x=>selectedIds.has(x)).length};
}

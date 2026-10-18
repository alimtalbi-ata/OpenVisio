// OpenVisio v25.8 — étude de trajets alternatifs, sans mutation.
// Auteur : Abdelhalim Talbi
import {routeAvoidingObstacles,intersectsObstacle,routeViaWaypoints} from './routing.js';
import {routeRevision} from './route-preview.js';
import {routeClearance} from './route-batch.js';
const valid=p=>Array.isArray(p)&&p.length>=2&&p.every(q=>q&&Number.isFinite(q.x)&&Number.isFinite(q.y));
const orthogonal=p=>p.slice(1).every((q,i)=>q.x===p[i].x||q.y===p[i].y);
const length=p=>p.slice(1).reduce((s,q,i)=>s+Math.abs(q.x-p[i].x)+Math.abs(q.y-p[i].y),0);
export function proposeSanAlternate(edge,nodes,routes,edges,{steps=[10,16,20],minimum=8}={}){
 if(!edge||!Array.isArray(nodes)||!(routes instanceof Map)||!Array.isArray(edges)||!Array.isArray(steps)||steps.length>12||!Number.isFinite(minimum)||minimum<0||minimum>100)throw Error('Recherche alternative invalide');
 if(edge.waypoints?.length||(edge.style&&edge.style!=='orthogonal'))return {status:'protected',reason:'Tracé manuel protégé'};
 const from=nodes.find(n=>n.id===edge.from),to=nodes.find(n=>n.id===edge.to),original=routes.get(String(edge.id))?.points;
 if(!from||!to||!valid(original))return {status:'unavailable',reason:'Géométrie source indisponible'};
 const others=edges.filter(e=>String(e.id)!==String(edge.id));
 const opposite=others.filter(e=>['A','B'].includes(String(e.fabric||'').toUpperCase())&&String(e.fabric).toUpperCase()!==String(edge.fabric||'').toUpperCase());
 const obstacles=nodes.filter(n=>n.id!==from.id&&n.id!==to.id);
 const baseline=opposite.map(e=>({id:String(e.id),points:routes.get(String(e.id))?.points}));
 if(baseline.some(r=>!valid(r.points)))return {status:'unavailable',reason:'Fabric opposée : géométrie manquante'};
 const quality=points=>{
  let collisions=0,regressions=0,proximity=0;
  for(let i=1;i<points.length;i++)for(const n of obstacles)if(intersectsObstacle(points[i-1],points[i],n,4))collisions++;
  for(const other of baseline){const before=routeClearance(original,other.points),after=routeClearance(points,other.points);if(after<minimum&&(before>=minimum||after<before-1e-7))regressions++;if(after<minimum)proximity++;}
  return {collisions,regressions,proximity,length:length(points)};
 };
 const before=quality(original);let best=null;
 for(const step of steps){
  if(!Number.isFinite(step)||step<4||step>200)throw Error('Pas de grille invalide');
  const result=routeAvoidingObstacles(from,to,obstacles,step,edge.fromPort||'auto',edge.toPort||'auto');
  if(!result.avoided||!valid(result.points)||!orthogonal(result.points))continue;
  const after=quality(result.points);
  if(after.collisions>before.collisions||after.regressions||after.proximity>before.proximity)continue;
  const gain=(before.collisions-after.collisions)*100000+(before.proximity-after.proximity)*10000+(before.length-after.length);
  if(gain<=0)continue;
  if(!best||gain>best.gain)best={status:'preview',edgeId:String(edge.id),points:result.points,before,after,gain,step};
 }
 return best||{status:'no-improvement',reason:'Aucun itinéraire alternatif validé',before};
}

// v25.9 : commit atomique de l'itinéraire, vérifié sur la géométrie réellement sérialisée.
const samePoints=(a,b)=>valid(a)&&valid(b)&&a.length===b.length&&a.every((p,i)=>Math.abs(p.x-b[i].x)<1e-6&&Math.abs(p.y-b[i].y)<1e-6);
export function alternateTopologyFingerprint(edges,nodes,routes){
 if(!Array.isArray(edges)||!Array.isArray(nodes)||!(routes instanceof Map))throw Error('Topologie invalide');
 return JSON.stringify({nodes:nodes.map(n=>[n.id,n.x,n.y,n.w,n.h,n.width,n.height]).sort((a,b)=>String(a[0]).localeCompare(String(b[0]))),edges:edges.map(e=>[e.id,e.from,e.to,e.style,e.offset,e.fabric,e.fromPort,e.toPort,e.waypoints]).sort((a,b)=>String(a[0]).localeCompare(String(b[0]))),routes:[...routes].map(([id,r])=>[id,r?.points]).sort((a,b)=>String(a[0]).localeCompare(String(b[0])))});
}
export function prepareAlternateCommit(proposal,edge,nodes,edges,routes){
 if(proposal?.status!=='preview'||String(edge?.id)!==proposal.edgeId||!valid(proposal.points)||!orthogonal(proposal.points)||proposal.points.length>32)throw Error('Alternative non applicable');
 if(edge.waypoints?.length||(edge.style&&edge.style!=='orthogonal'))throw Error('Trajet manuel protégé');
 const from=nodes.find(n=>n.id===edge.from),to=nodes.find(n=>n.id===edge.to);
 if(!from||!to)throw Error('Extrémités absentes');
 const waypoints=proposal.points.slice(1,-1).map(p=>({x:p.x,y:p.y}));
 const actual=routeViaWaypoints(from,to,waypoints,edge.fromPort||'auto',edge.toPort||'auto').points;
 if(!samePoints(actual,proposal.points))throw Error('Ancres incompatibles : aperçu non reproductible');
 const current=proposeSanAlternate(edge,nodes,routes,edges,{steps:[proposal.step]});
 if(current.status!=='preview'||!samePoints(current.points,proposal.points))throw Error('Alternative non confirmée par recalcul');
 return {edgeId:String(edge.id),waypoints,revision:routeRevision(edge,nodes),fingerprint:alternateTopologyFingerprint(edges,nodes,routes)};
}
export function commitAlternateRoute(edge,plan,nodes,edges,routes){
 if(!edge||!plan||String(edge.id)!==plan.edgeId||routeRevision(edge,nodes)!==plan.revision||alternateTopologyFingerprint(edges,nodes,routes)!==plan.fingerprint)throw Error('Topologie obsolète : recalcul requis');
 if(edge.waypoints?.length||(edge.style&&edge.style!=='orthogonal'))throw Error('Tracé protégé');
 if(!Array.isArray(plan.waypoints)||plan.waypoints.length>30)throw Error('Points invalides');
 const from=nodes.find(n=>n.id===edge.from),to=nodes.find(n=>n.id===edge.to);
 const points=routeViaWaypoints(from,to,plan.waypoints,edge.fromPort||'auto',edge.toPort||'auto').points;
 if(!valid(points)||!orthogonal(points))throw Error('Géométrie non orthogonale');
 edge.waypoints=plan.waypoints.map(p=>({...p}));
 return {edgeId:plan.edgeId,waypoints:edge.waypoints};
}

// v26.0 — qualification géométrique sur l'état sérialisé, sans mutation.
export function verifyCommittedAlternate(edge,plan,nodes,edges,routes,{minimum=8}={}){
 if(!edge||!plan||!Array.isArray(nodes)||!Array.isArray(edges)||!(routes instanceof Map)||!Number.isFinite(minimum)||minimum<0)throw Error('Vérification invalide');
 const original=routes.get(String(edge.id))?.points;
 const from=nodes.find(n=>n.id===edge.from),to=nodes.find(n=>n.id===edge.to);
 if(!from||!to||!valid(original)||!Array.isArray(edge.waypoints))throw Error('Géométrie de vérification indisponible');
 const actual=routeViaWaypoints(from,to,edge.waypoints,edge.fromPort||'auto',edge.toPort||'auto').points;
 if(!valid(actual)||!orthogonal(actual)||!samePoints(actual,routeViaWaypoints(from,to,plan.waypoints,edge.fromPort||'auto',edge.toPort||'auto').points))throw Error('Route appliquée divergente');
 let oldCollisions=0,newCollisions=0,oldProximity=0,newProximity=0;
 for(const n of nodes.filter(n=>n.id!==from.id&&n.id!==to.id)){
  for(let i=1;i<original.length;i++)if(intersectsObstacle(original[i-1],original[i],n,4))oldCollisions++;
  for(let i=1;i<actual.length;i++)if(intersectsObstacle(actual[i-1],actual[i],n,4))newCollisions++;
 }
 for(const other of edges.filter(e=>String(e.id)!==String(edge.id))){
  const fa=String(edge.fabric||'').toUpperCase(),fb=String(other.fabric||'').toUpperCase();
  if(!['A','B'].includes(fa)||!['A','B'].includes(fb)||fa===fb)continue;
  const points=routes.get(String(other.id))?.points;
  if(!valid(points))throw Error('Route Fabric opposée manquante');
  const old=routeClearance(original,points),next=routeClearance(actual,points);
  if(old<minimum)oldProximity++;
  if(next<minimum)newProximity++;
  if(next<minimum&&(old>=minimum||next<old-1e-7))throw Error('Régression espacement Fabric A/B');
 }
 if(newCollisions>oldCollisions||newProximity>oldProximity)throw Error('Régression géométrique');
 return {verified:true,before:{length:length(original),collisions:oldCollisions,proximity:oldProximity},after:{length:length(actual),collisions:newCollisions,proximity:newProximity},points:actual};
}

// v26.1 — qualification du cycle de vie sur copie : application, JSON, undo et redo.
import {snapshot,restore} from './model.js';
import {createHistory} from './history-transaction.js';
export function qualifyAlternateLifecycle(state,plan,routes,{minimum=8}={}){
 if(!state||!Array.isArray(state.nodes)||!Array.isArray(state.edges)||!(routes instanceof Map))throw Error('Etat de qualification invalide');
 const draft=restore(snapshot(state));
 const history=createHistory(4);
 const edge=draft.edges.find(e=>String(e.id)===String(plan?.edgeId));
 if(!edge)throw Error('Connexion de qualification absente');
 const initial=snapshot(draft);
 history.checkpoint(draft);
 commitAlternateRoute(edge,plan,draft.nodes,draft.edges,routes);
 const verified=verifyCommittedAlternate(edge,plan,draft.nodes,draft.edges,routes,{minimum});
 const applied=snapshot(draft);
 const reloaded=restore(JSON.stringify(JSON.parse(applied)));
 const persisted=reloaded.edges.find(e=>String(e.id)===String(plan.edgeId));
 if(!persisted||JSON.stringify(persisted.waypoints)!==JSON.stringify(edge.waypoints))throw Error('Persistance de la route incorrecte');
 if(!history.travel(draft,history.undo,history.redo)||snapshot(draft)!==initial)throw Error('Annulation de la route incorrecte');
 if(!history.travel(draft,history.redo,history.undo)||snapshot(draft)!==applied)throw Error('Rétablissement de la route incorrect');
 return {qualified:true,verified,persisted:true,undo:true,redo:true};
}

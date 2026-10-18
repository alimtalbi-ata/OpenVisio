import {classifyRouteClearance} from "./route-clearance.js";
import {createRouteValueCache} from "./route-cache.js";
import {createEdgeMutationSession,reconcileEdgeTransaction} from "./edge-mutation-tracker.js";
import {qualifyLocalRouteUpdate} from "./spatial-routing.js";
import {svgNodeTransform} from "./vector-transform.js";
import {physicalPortMarkers,namedPortPosition,cableDiagnostics} from "./ports.js";
import {routeEdge,routeAvoidingObstacles,routeViaWaypoints,routeWithFewerCrossings,routeSmart,optimizeConnectionOrder,separateParallelRoutes,separateSharedSegments,separatePartialOverlaps,distributeEndpointAnchors,orthogonalFanOut,reduceFanOutCrossings,edgeMidpoint} from "./routing.js";
// Auteur : Abdelhalim Talbi
const NS="http://www.w3.org/2000/svg";
function el(tag,attrs={}){const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));return n;}
const routeCache=createRouteValueCache({limit:500,onEvict(key){
 const owner=routeKeyOwner.get(key);
 if(owner!==undefined){routeKeyOwner.delete(key);const keys=edgeRouteKeys.get(owner);keys?.delete(key);if(keys?.size===0)edgeRouteKeys.delete(owner);}
}});
// Index secondaire du cache existant, jamais un second stockage de routes.
const edgeRouteKeys=new Map();
const routeKeyOwner=new Map();
function indexRouteKey(edgeId,key){
 const owner=String(edgeId);
 if(routeKeyOwner.has(key)&&routeKeyOwner.get(key)!==owner)edgeRouteKeys.get(routeKeyOwner.get(key))?.delete(key);
 routeKeyOwner.set(key,owner);
 if(!edgeRouteKeys.has(owner))edgeRouteKeys.set(owner,new Set());
 edgeRouteKeys.get(owner).add(key);
}
export function invalidateCachedEdgeRoute(edgeId){
 const owner=String(edgeId),keys=edgeRouteKeys.get(owner);
 if(!keys)return 0;
 let removed=0;
 for(const key of keys){if(routeCache.delete(key))removed++;routeKeyOwner.delete(key);}
 edgeRouteKeys.delete(owner);
 return removed;
}
export function invalidateCachedEdgeRoutes(edgeIds){
 if(!edgeIds||typeof edgeIds[Symbol.iterator]!=='function')throw new TypeError('edgeIds must be iterable');
 let removed=0;for(const id of new Set(edgeIds))removed+=invalidateCachedEdgeRoute(id);
 return removed;
}
export function routeCacheDiagnostics(){return {...routeCache.stats(),indexedEdges:edgeRouteKeys.size,indexedKeys:routeKeyOwner.size};}
const MAX_CACHE=500;
function cachedRoute(edge,a,b,obstacles,placedRoutes=[],fast=false){
 const key=JSON.stringify([edge.id,edge.style,edge.offset,edge.waypoints,edge.fromPort,edge.toPort,fast,a.x,a.y,a.w,a.h,b.x,b.y,b.w,b.h,a.rotation,a.flipH,a.flipV,b.rotation,b.flipH,b.flipV,["avoid","smart"].includes(edge.style)?obstacles.map(n=>[n.id,n.x,n.y,n.w,n.h]):null,["orthogonal","smart"].includes(edge.style)&&!edge.waypoints?.length?placedRoutes.map(r=>r.path):null]);
 const cached=routeCache.get(key);
 if(cached!==undefined){indexRouteKey(edge.id,key);return cached;}
 const routed=Array.isArray(edge.waypoints)&&edge.waypoints.length?routeViaWaypoints(a,b,edge.waypoints,edge.fromPort||"auto",edge.toPort||"auto"):(edge.style==="smart"?routeSmart(a,b,obstacles,placedRoutes,{fast}):edge.style==="avoid"?routeAvoidingObstacles(a,b,obstacles,20,edge.fromPort||"auto",edge.toPort||"auto"):(edge.style==="orthogonal"&&!Number(edge.offset)&&!([edge.fromPort,edge.toPort].some(v=>v&&v!=="auto"))?routeWithFewerCrossings(a,b,placedRoutes):routeEdge(a,b,edge.style||"orthogonal",Number(edge.offset)||0,edge.fromPort||"auto",edge.toPort||"auto")));
 const stored=routeCache.set(key,routed);
 indexRouteKey(edge.id,key);
 return stored;
}
// Cache par canevas : une sélection ou un survol ne modifie pas la géométrie.
// La signature tient compte des champs complets des nœuds et des liens, y compris ports et obstacles.
const renderStates=new WeakMap();
const renderStatistics=new WeakMap();
const diagnosticCache=new WeakMap();
const routingDecisions=new WeakMap();
const clearanceDiagnostics=new WeakMap();
const routeSegmentGeometry=new WeakMap();
export function lastRouteSegmentGeometry(svg,edgeId){const points=routeSegmentGeometry.get(svg)?.get(String(edgeId));return points?structuredClone(points):[];}
export function lastRouteClearanceDiagnostics(svg){return structuredClone(clearanceDiagnostics.get(svg)||{checked:0,invalid:0,edges:[]});}
export function lastRoutingDecision(svg){return {...(routingDecisions.get(svg)||{mode:"not-measured",reasons:[]})};}
// Cache par canevas : la sélection ne doit pas relancer les diagnostics SAN.
// Une signature des données d'entrée (et non des références mutables) garantit
// l'invalidation après modification d'un équipement, port ou câble.
export function cachedCableDiagnostics(svg,nodes,edges,diagnose=cableDiagnostics){
 if(!svg||typeof svg!=="object"||!Array.isArray(nodes)||!Array.isArray(edges)||typeof diagnose!=="function")throw new TypeError("Diagnostic SAN invalide");
 const signature=JSON.stringify([nodes,edges]);
 const old=diagnosticCache.get(svg);
 if(old&&old.signature===signature&&old.diagnose===diagnose)return old.findings;
 const findings=diagnose(nodes,edges);
 if(!Array.isArray(findings))throw new TypeError("Résultat diagnostic SAN invalide");
 diagnosticCache.set(svg,{signature,diagnose,findings});
 return findings;
}
export function clearCableDiagnosticsCache(svg){diagnosticCache.delete(svg);}

// Compteurs du DOM réellement conservé ou remplacé lors du dernier rendu.
export function lastRenderStatistics(svg){return {...(renderStatistics.get(svg)||{nodesReused:0,nodesUpdated:0,edgesReused:0,edgesUpdated:0,nodesRemoved:0,edgesRemoved:0})};}

// Seuls les champs susceptibles de modifier les trajets invalident le calcul global.
// Les propriétés d'apparence, les textes et la sélection restent gérés par le rendu SVG.
export function routingGeometrySignature(state){
 const nodes=state.nodes.map(n=>[n.id,n.x,n.y,n.w,n.h,n.rotation,n.flipH,n.flipV,n.type,n.ports,n.interfaces]);
 const edges=state.edges.map(e=>[e.id,e.from,e.to,e.style,e.offset,e.waypoints,e.fromPort,e.toPort,e.sourceInterface,e.targetInterface]);
 return JSON.stringify([nodes,edges]);
}
// Diagnostic pur des changements : aide à ne rafraîchir que les groupes SVG concernés.
export function affectedGraphElements(previousState,nextState){
 const changed=(a,b)=>JSON.stringify(a)!==JSON.stringify(b);
 const oldNodes=new Map((previousState?.nodes||[]).map(n=>[n.id,n]));
 const newNodes=new Map((nextState?.nodes||[]).map(n=>[n.id,n]));
 const oldEdges=new Map((previousState?.edges||[]).map(e=>[e.id,e]));
 const newEdges=new Map((nextState?.edges||[]).map(e=>[e.id,e]));
 const nodes=new Set([...oldNodes.keys(),...newNodes.keys()].filter(id=>changed(oldNodes.get(id),newNodes.get(id))));
 const edges=new Set([...oldEdges.keys(),...newEdges.keys()].filter(id=>changed(oldEdges.get(id),newEdges.get(id))));
 for(const e of [...oldEdges.values(),...newEdges.values()])if(nodes.has(e.from)||nodes.has(e.to))edges.add(e.id);
 return {nodes,edges,geometryChanged:routingGeometrySignature(previousState||{nodes:[],edges:[]})!==routingGeometrySignature(nextState||{nodes:[],edges:[]})};
}
export function cachedRoutingPipeline(state,previous,compute){
 const signature=routingGeometrySignature(state);
 if(previous.routingSignature===signature&&previous.routingRoutes)return previous.routingRoutes;
 const routes=compute();
 previous.routingSignature=signature;
 previous.routingRoutes=routes;
 return routes;
}
// Comparaison déterministe des tracés : un chemin local divergent doit être rejeté.
export function compareRoutingGeometry(localRoutes,globalRoutes,{tolerance=0.001}={}){
 if(!(localRoutes instanceof Map)||!(globalRoutes instanceof Map)||!Number.isFinite(tolerance)||tolerance<0)throw new TypeError("Comparaison de routes invalide");
 const divergent=[];
 for(const id of new Set([...localRoutes.keys(),...globalRoutes.keys()])){
  const a=localRoutes.get(id),b=globalRoutes.get(id);
  if(!a||!b||!Array.isArray(a.points)||!Array.isArray(b.points)||a.points.length!==b.points.length||
    a.points.some((p,i)=>!Number.isFinite(p?.x)||!Number.isFinite(p?.y)||!Number.isFinite(b.points[i]?.x)||!Number.isFinite(b.points[i]?.y)||Math.abs(p.x-b.points[i].x)>tolerance||Math.abs(p.y-b.points[i].y)>tolerance))divergent.push(id);
 }
 return {equivalent:divergent.length===0,divergentEdges:divergent.sort(),comparedEdges:new Set([...localRoutes.keys(),...globalRoutes.keys()]).size};
}
// Recalcul local prudent : seuls les liens orthogonaux indépendants sont éligibles.
// Les topologies complexes utilisent systématiquement le pipeline global historique.
export function incrementalRoutingPipeline(state,previous,compute){
 const signature=routingGeometrySignature(state);
 if(previous.routingSignature===signature&&previous.routingRoutes)return previous.routingRoutes;
 const old=previous.routingState, oldRoutes=previous.routingRoutes;
 let routes=null;
 if(old&&oldRoutes&&state.edges.length>160&&state.edges.length===old.edges.length&&
    state.nodes.length===old.nodes.length&&state.edges.every((e,i)=>e.id===old.edges[i].id&&
      ['orthogonal','avoid'].includes(e.style||'orthogonal')&&!e.waypoints?.length&&
      !e.sourceInterface&&!e.targetInterface&&!e.fromPort&&!e.toPort&&!Number(e.offset))){
  const qualification=qualifyLocalRouteUpdate(old,state,oldRoutes,{maxChangedEdges:Math.min(12,Math.ceil(state.edges.length*.04))});
  const impact={changedEdges:new Set(qualification.changedEdges)};
  const byId=new Map(state.nodes.map(n=>[n.id,n]));
  if(qualification.eligible&&impact.changedEdges.size>0){
   previous.lastRoutingMismatch=[];
   const next=new Map(oldRoutes);let safe=true;
   for(const e of state.edges){
    if(!impact.changedEdges.has(e.id))continue;
    const a=byId.get(e.from),b=byId.get(e.to);
    if(!a||!b){safe=false;break;}
    const obstacles=state.nodes.filter(n=>n.id!==a.id&&n.id!==b.id);
    next.set(e.id,(e.style==='avoid')?routeAvoidingObstacles(a,b,obstacles,20):routeEdge(a,b,'orthogonal'));
   }
   if(safe){
    // Contrôle différentiel périodique, sans imposer le coût global à chaque frame.
    previous.localVerificationCount=(previous.localVerificationCount||0)+1;
    if(previous.localVerificationCount%16===0){
     const reference=compute();
     const comparison=compareRoutingGeometry(next,reference);
     previous.lastRoutingComparison=comparison;
     if(comparison.equivalent)routes=next;
     else{routes=reference;previous.lastRoutingMismatch=comparison.divergentEdges;}
    }else routes=next;
   }
  }
 }
 previous.lastRoutingMode=routes?"local-qualified":"full-recompute";
 if(previous.lastRoutingMismatch?.length&&routes&&previous.localVerificationCount%16===0)previous.lastRoutingMode="full-recompute-divergence";
 if(!routes)routes=compute();
 previous.routingSignature=signature;
 previous.routingRoutes=routes;
 // Snapshot : les objets du state sont mutables pendant le glisser-déposer.
 previous.routingState={nodes:state.nodes.map(n=>structuredClone(n)),edges:state.edges.map(e=>structuredClone(e))};
 return routes;
}
// Une liaison SVG ne dépend visuellement que de ses propriétés, de son chemin
// calculé, de sa sélection et de ses alertes. Sérialiser les deux nœuds complets
// à chaque frame crée un coût proportionnel aux métadonnées de la CMDB.
export function edgeVisualSignature(edge,path,selected=false,warning=false){
 if(!edge||typeof path!=="string")throw new TypeError("Connexion ou tracé SVG invalide");
 return JSON.stringify([edge, path, Boolean(selected), Boolean(warning)]);
}
// Signature dédiée au nœud : ne pas conserver de références mutables entre frames.
export function nodeVisualSignature(node,selected=false){
 if(!node||typeof node!=="object")throw new TypeError("Nœud SVG invalide");
 return JSON.stringify([node,Boolean(selected)]);
}
// Une route déjà distribuée est définitive : ne pas reconstruire inutilement
// la liste des obstacles (O(nœuds)) pour chaque connexion au rendu SVG.
export function resolveDistributedRoute(edge,a,b,nodes,distributedRoutes,placedRoutes=[],fallback=cachedRoute){
 if(!(distributedRoutes instanceof Map)||!Array.isArray(nodes)||typeof fallback!=="function")throw new TypeError("Résolution de route invalide");
 const route=distributedRoutes.get(edge.id);
 if(route)return route;
 const obstacles=["avoid","smart"].includes(edge.style)?nodes.filter(n=>n.id!==a.id&&n.id!==b.id):[];
 return fallback(edge,a,b,obstacles,placedRoutes);
}
// V24.1 — compteurs de mutations DOM réellement déclenchées par le rendu.
// Aucun compteur ne prétend mesurer le temps de peinture du navigateur.
export function summarizeDomMutations(stats){
 const keys=['nodesUpdated','edgesUpdated','nodesRemoved','edgesRemoved','nodesReused','edgesReused'];
 if(!stats||keys.some(k=>!Number.isInteger(stats[k])||stats[k]<0))throw new TypeError('Statistiques DOM invalides');
 const createdOrReplaced=stats.nodesUpdated+stats.edgesUpdated;
 const removed=stats.nodesRemoved+stats.edgesRemoved;
 const reused=stats.nodesReused+stats.edgesReused;
 const total=createdOrReplaced+removed+reused;
 return {createdOrReplaced,removed,reused,total,mutationRatio:total?((createdOrReplaced+removed)/total):0};
}
// V24.2 — diagnostic sérialisable, sans référence DOM ni données métier.
export function renderDiagnosticSnapshot(svg){
 const dom=lastRenderStatistics(svg);
 return {dom:{...dom,...summarizeDomMutations(dom)},routing:lastRoutingDecision(svg)};
}
const renderPhaseProfiles=new WeakMap();
export function lastRenderPhaseProfile(svg){return {...(renderPhaseProfiles.get(svg)||{})};}
export function renderGraph(svg,state,handlers){
 const phaseStart=performance.now();
 const phaseTimes={};
 let phaseMark=phaseStart;
 const markPhase=name=>{const now=performance.now();phaseTimes[name]=+(now-phaseMark).toFixed(3);phaseMark=now;};
 let previous=renderStates.get(svg);
 if(!previous){previous={nodes:new Map(),edges:new Map()};renderStates.set(svg,previous);}
 // v41.17: invalidate incident routes when equipment geometry changes.
 // Snapshot is detached from mutable editor objects.
 const geometrySnapshot=JSON.stringify({nodes:state.nodes,edges:state.edges});
 if(previous.geometrySnapshot){
  const before=JSON.parse(previous.geometrySnapshot);
  const affected=affectedGraphElements(before,state);
  if(affected.geometryChanged&&affected.edges.size)invalidateCachedEdgeRoutes(affected.edges);
 }
 previous.geometrySnapshot=geometrySnapshot;
 // Transactional edge mutation reconciliation.
 // Snapshot is value-based: in-place editor mutations cannot bypass detection.
 if(!previous.edgeMutationSession){
  previous.edgeMutationSession=createEdgeMutationSession(state.edges);
 }else{
  reconcileEdgeTransaction(previous.edgeMutationSession,state.edges,invalidateCachedEdgeRoutes);
 }
 markPhase("mutationReconciliation");
 const nextNodes=new Map(),nextEdges=new Map();
 const stats={nodesReused:0,nodesUpdated:0,edgesReused:0,edgesUpdated:0,nodesRemoved:0,edgesRemoved:0};
 const nodesLayer=svg.querySelector("#nodesLayer"),edgesLayer=svg.querySelector("#edgesLayer");

 const byId=new Map(state.nodes.map(n=>[n.id,n]));
 const wiringFindings=cachedCableDiagnostics(svg,state.nodes,state.edges);
 const badEdges=new Set(wiringFindings.map(f=>f.edgeId));
 markPhase("cableDiagnostics");
 const routingStages={};
 const timedRoutingStage=(name,fn)=>{const started=performance.now();try{return fn();}finally{routingStages[name]=+((routingStages[name]||0)+performance.now()-started).toFixed(3);}};
 const distributedRoutes=incrementalRoutingPipeline(state,previous,()=>{
  const autoRoutes=timedRoutingStage("routeCalculation",()=>optimizeConnectionOrder(state.edges,state.nodes,(edge,a,b,placed)=>{
   const obstacles=["avoid","smart"].includes(edge.style)?state.nodes.filter(n=>n.id!==a.id&&n.id!==b.id):[];
   return cachedRoute(edge,a,b,obstacles,placed,state.edges.length>160);
  },{passes:state.edges.length>160?1:2}));
  const separatedRoutes=timedRoutingStage("parallelSeparation",()=>separateParallelRoutes(state.edges,autoRoutes.routes,{obstacles:state.nodes}));
  const sharedRoutes=timedRoutingStage("sharedSegmentHandling",()=>separatePartialOverlaps(state.edges,separateSharedSegments(state.edges,separatedRoutes,{obstacles:state.nodes}),{obstacles:state.nodes}));
  const anchoredRoutes=timedRoutingStage("distributeEndpointAnchors",()=>distributeEndpointAnchors(state.edges,sharedRoutes,state.nodes));
  const fannedRoutes=timedRoutingStage("orthogonalFanOut",()=>orthogonalFanOut(state.edges,anchoredRoutes,state.nodes));
  return timedRoutingStage("reduceFanOutCrossings",()=>reduceFanOutCrossings(state.edges,fannedRoutes,state.nodes));
 });
 markPhase("routingPipeline");
 routingDecisions.set(svg,{mode:previous.lastRoutingMode||"cached",reasons:[]});
 const placedRoutes=[];
 const clearanceResults=[];
 const segmentGeometry=new Map();
 for(const edge of state.edges){
  const a=byId.get(edge.from),b=byId.get(edge.to);if(!a||!b)continue;
  const baseRoute=resolveDistributedRoute(edge,a,b,state.nodes,distributedRoutes,placedRoutes);
  const physicalStart=edge.sourceInterface?namedPortPosition(a,edge.sourceInterface):null;
  const physicalEnd=edge.targetInterface?namedPortPosition(b,edge.targetInterface):null;
  // Les repères physiques sont réellement utilisés comme extrémités du SVG.
  // Un segment court relie le routage existant au repère ; aucune promesse
  // d'évitement complet d'obstacles sur ces segments additionnels.
  const routed=physicalStart||physicalEnd?(()=>{
   const points=[...baseRoute.points];
   if(physicalStart)points.unshift(physicalStart);
   if(physicalEnd)points.push(physicalEnd);
   return {...baseRoute,points,path:points.map((p,i)=>`${i?'L':'M'} ${p.x} ${p.y}`).join(' ')};
  })():baseRoute;
  segmentGeometry.set(String(edge.id),routed.points.map(p=>({x:p.x,y:p.y})));
  const clearance=classifyRouteClearance(routed.points,state.nodes.filter(n=>n.id!==edge.from&&n.id!==edge.to),{physicalStart:!!physicalStart,physicalEnd:!!physicalEnd});
  clearanceResults.push({edgeId:edge.id,valid:clearance.valid,strictValid:clearance.strictValid,errors:clearance.errors,reviews:clearance.reviews,issues:clearance.issues});
  const signature=edgeVisualSignature(edge,routed.path,state.selected===edge.id,badEdges.has(edge.id));
  const prior=previous.edges.get(edge.id);
  placedRoutes.push(routed);
  if(prior&&prior.signature===signature){stats.edgesReused++;nextEdges.set(edge.id,prior);continue;}
  stats.edgesUpdated++;
  const group=el("g",{"data-edge-id":edge.id});
  const path=routed.path;
  const hit=el("path",{d:path,class:"edge-hit"});hit.addEventListener("click",e=>{e.stopPropagation();handlers.select(edge.id,"edge")});
  hit.addEventListener("dblclick",e=>{e.stopPropagation();handlers.addWaypoint?.(e,edge.id);});group.append(hit);
  const line=el("path",{d:path,class:`edge ${state.selected===edge.id?"selected":""} ${badEdges.has(edge.id)?"wiring-warning":""}`});group.append(line);
  if(state.selected===edge.id&&Array.isArray(edge.waypoints)){
   edge.waypoints.forEach((point,index)=>{
    const handle=el("circle",{cx:point.x,cy:point.y,r:8,class:"waypoint-handle","data-edge":edge.id,"data-index":index,tabindex:"0",role:"button","aria-label":`Déplacer le point ${index+1}`});
    handle.addEventListener("pointerdown",e=>{e.stopPropagation();handlers.onWaypointDown?.(e,edge.id,index);});
    handle.addEventListener("click",e=>{e.stopPropagation();});
    handle.addEventListener("dblclick",e=>{e.stopPropagation();handlers.removeWaypoint?.(edge.id,index);});
    group.append(handle);
   });
  }
  if(state.selected===edge.id){
   for(const [index,point] of [routed.points[0],routed.points.at(-1)].entries()){
    if(point)group.append(el("circle",{cx:point.x,cy:point.y,r:5,class:"endpoint-anchor", "data-port-index":index, "aria-label":index===0?"Port source":"Port destination"}));
   }
  }
  if(state.selected===edge.id){
   for(const [index,name] of [[0,edge.sourceInterface],[1,edge.targetInterface]]){
    const pt=index===0?routed.points[0]:routed.points.at(-1);
    if(pt&&name){const t=el("text",{x:pt.x+8,y:pt.y-9,class:"edge-label","text-anchor":"start"});t.textContent=name;group.append(t);}
   }
  }
  if(edge.label){const m=edgeMidpoint(routed.points);const label=el("text",{x:m.x,y:m.y-7,class:"edge-label","text-anchor":"middle"});label.textContent=edge.label;group.append(label);}
  if(prior)prior.element.replaceWith(group);else edgesLayer.append(group);
  nextEdges.set(edge.id,{signature,element:group});
 }
 routeSegmentGeometry.set(svg,segmentGeometry);
 clearanceDiagnostics.set(svg,{checked:clearanceResults.length,invalid:clearanceResults.filter(x=>!x.valid).length,review:clearanceResults.filter(x=>x.reviews>0).length,edges:clearanceResults});
 markPhase("edgeDom");
 for(const n of state.nodes){
  const signature=nodeVisualSignature(n,state.selected===n.id);
  const prior=previous.nodes.get(n.id);
  if(prior&&prior.signature===signature){stats.nodesReused++;nextNodes.set(n.id,prior);continue;}
  stats.nodesUpdated++;
  const g=el("g",{class:`node ${state.selected===n.id?"selected":""}`,transform:svgNodeTransform(n), "data-id":n.id});
  let shape;
  if(n.type==="cloud"){shape=el("path",{d:`M 36 ${n.h*.72} C 14 ${n.h*.72}, 14 ${n.h*.42}, 36 ${n.h*.4} C 40 ${n.h*.12}, 76 ${n.h*.1}, 84 ${n.h*.38} C 111 ${n.h*.27}, 133 ${n.h*.46}, 119 ${n.h*.67} Q 112 ${n.h*.76}, 96 ${n.h*.76} Z`,class:"node-shape",fill:n.fill,stroke:n.stroke});}
  else if(n.type==="decision"){shape=el("polygon",{points:`${n.w/2},0 ${n.w},${n.h/2} ${n.w/2},${n.h} 0,${n.h/2}`,class:"node-shape",fill:n.fill,stroke:n.stroke});}
  else if(n.type==="terminator"){shape=el("rect",{x:0,y:0,width:n.w,height:n.h,rx:n.h/2,class:"node-shape",fill:n.fill,stroke:n.stroke});}
  else if(n.type==="database"){shape=el("path",{d:`M 0 14 A ${n.w/2} 14 0 0 1 ${n.w} 14 L ${n.w} ${n.h-14} A ${n.w/2} 14 0 0 1 0 ${n.h-14} Z M 0 14 A ${n.w/2} 14 0 0 0 ${n.w} 14`,class:"node-shape",fill:n.fill,stroke:n.stroke});}
  else if(n.type==="document"){shape=el("path",{d:`M 0 0 H ${n.w} V ${n.h-14} Q ${n.w*.75} ${n.h-26} ${n.w*.5} ${n.h-14} Q ${n.w*.25} ${n.h-2} 0 ${n.h-14} Z`,class:"node-shape",fill:n.fill,stroke:n.stroke});}
  else if(n.type==="switch"){shape=el("rect",{x:0,y:0,width:n.w,height:n.h,rx:7,class:"node-shape",fill:n.fill,stroke:n.stroke});for(let i=0;i<6;i++)g.append(el("circle",{cx:16+i*23,cy:n.h-13,r:3,fill:n.stroke}));}
  else {shape=el("rect",{x:0,y:0,width:n.w,height:n.h,rx:n.type==="storage"?14:7,class:"node-shape",fill:n.fill,stroke:n.stroke});}
  shape.setAttribute("fill",n.fill);shape.setAttribute("stroke",n.stroke);g.prepend(shape);
  const icon=el("text",{x:12,y:21,"font-size":14,fill:n.stroke});icon.textContent=n.type==="server"?"▤":n.type==="storage"?"▱":n.type==="switch"?"▦":({process:"▭",decision:"◇",terminator:"●",document:"▤",database:"▥",person:"♙",department:"▣",application:"▦",api:"⇄",firewall:"⬡",router:"⬡",loadbalancer:"⇄",container:"▤",vm:"▤",backup:"▱",tape:"▥"}[n.type]||"☁");g.append(icon);
  const title=el("text",{x:12,y:40,class:"node-title"});title.textContent=String(n.title??"").slice(0,23);g.append(title);
  const sub=el("text",{x:12,y:Math.min(n.h-8,57),class:"node-subtitle"});sub.textContent=String(n.subtitle??"").slice(0,27);g.append(sub);
  if(state.selected===n.id){
   for(const port of physicalPortMarkers(n)){
    const marker=el("circle",{cx:port.x,cy:port.y,r:3.5,class:"physical-port-marker","data-interface":port.name});
    const tooltip=el("title");tooltip.textContent=port.name;marker.append(tooltip);g.append(marker);
   }
  }
  g.addEventListener("pointerdown",e=>handlers.onPointerDown(e,n));g.addEventListener("click",e=>{e.stopPropagation();handlers.onNodeClick?.(n.id,e);});if(prior)prior.element.replaceWith(g);else nodesLayer.append(g);
  nextNodes.set(n.id,{signature,element:g});
 }
 markPhase("nodeDom");
 for(const [id,entry] of previous.edges)if(!nextEdges.has(id)){entry.element.remove();stats.edgesRemoved++;}
 for(const [id,entry] of previous.nodes)if(!nextNodes.has(id)){entry.element.remove();stats.nodesRemoved++;}
 previous.nodes=nextNodes;previous.edges=nextEdges;renderStatistics.set(svg,{...stats,domMutations:summarizeDomMutations(stats)});
 markPhase("cleanup");phaseTimes.total=+(performance.now()-phaseStart).toFixed(3);
 renderPhaseProfiles.set(svg,{...phaseTimes,routingStages});
}
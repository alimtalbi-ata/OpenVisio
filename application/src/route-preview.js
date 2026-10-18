// Aperçu conservateur du routage SAN — Auteur : Abdelhalim Talbi
import {routeEdge,routeSharedLength,countRouteCrossings,intersectsObstacle} from './routing.js';
// v22.7 : index spatial conservateur des boîtes englobantes pour éviter
// les comparaisons géométriques inutiles, sans écarter de vraie intersection.
export function routeBounds(points){
 if(!Array.isArray(points)||points.length<2||points.some(p=>!p||!Number.isFinite(p.x)||!Number.isFinite(p.y)))return null;
 let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
 for(const p of points){minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);}
 return {minX,maxX,minY,maxY};
}
export function boundsIntersect(a,b,padding=0){
 if(!a||!b)return true;
 return a.minX<=b.maxX+padding&&b.minX<=a.maxX+padding&&a.minY<=b.maxY+padding&&b.minY<=a.maxY+padding;
}
export function proposeRouteOffset(edge,nodes,routes,{step=12,maxLanes=5}={}){
 if(!edge||!Array.isArray(nodes)||!(routes instanceof Map)||!Number.isFinite(step)||step<=0||!Number.isInteger(maxLanes)||maxLanes<1||maxLanes>20)throw Error('Paramètres de prévisualisation invalides');
 if(edge.waypoints?.length||!['orthogonal',undefined,null,''].includes(edge.style))return {status:'protected',reason:'Trajet manuel ou mode de routage non pris en charge'};
 const a=nodes.find(n=>n.id===edge.from),b=nodes.find(n=>n.id===edge.to);
 if(!a||!b)return {status:'unavailable',reason:'Extrémité introuvable'};
 const existing=routes.get(String(edge.id))?.points;
 if(!Array.isArray(existing)||existing.length<2)return {status:'unavailable',reason:'Tracé affiché introuvable'};
 const other=[...routes].filter(([id])=>String(id)!==String(edge.id)).map(([,r])=>({points:r.points,bounds:routeBounds(r.points)})).filter(r=>r.bounds);
 const obstacles=nodes.filter(n=>n.id!==edge.from&&n.id!==edge.to);
 const quality=points=>{
  let overlap=0,crossings=0,collisions=0;
  const bounds=routeBounds(points);
  for(const path of other){if(!boundsIntersect(bounds,path.bounds))continue;overlap+=routeSharedLength({points},{points:path.points});crossings+=countRouteCrossings([{points},{points:path.points}]);}
  for(let i=1;i<points.length;i++)for(const o of obstacles){const ob={minX:o.x,maxX:o.x+(o.w??o.width??0),minY:o.y,maxY:o.y+(o.h??o.height??0)};if(boundsIntersect(routeBounds([points[i-1],points[i]]),ob,4)&&intersectsObstacle(points[i-1],points[i],o,4))collisions++;}
  return {overlap,crossings,collisions,score:collisions*1000000+crossings*10000+overlap*10};
 };
 const before=quality(existing);let best=null;
 for(let lane=1;lane<=maxLanes;lane++)for(const sign of [-1,1]){
  const offset=(Number(edge.offset)||0)+sign*lane*step;
  const candidate=routeEdge(a,b,'orthogonal',offset,edge.fromPort||'auto',edge.toPort||'auto');
  const after=quality(candidate.points);
  if(after.collisions>before.collisions||after.score>=before.score)continue;
  if(!best||after.score<best.after.score||(after.score===best.after.score&&Math.abs(offset)<Math.abs(best.offset)))best={status:'preview',edgeId:String(edge.id),offset,before,after,points:candidate.points};
 }
 return best||{status:'no-improvement',before,reason:'Aucun décalage plus sûr identifié'};
}
export function applyRouteOffset(edge,proposal){
 if(!edge||!proposal||proposal.status!=='preview'||String(edge.id)!==proposal.edgeId||edge.waypoints?.length||!Number.isFinite(proposal.offset))throw Error('Aperçu non applicable');
 if((edge.style||'orthogonal')!=='orthogonal')throw Error('Routage manuel protégé');
 edge.offset=proposal.offset;return edge;
}

// Sérialisation SVG contrôlée : aucun HTML injecté, tracés orthogonaux uniquement.
export function routePreviewPath(points){
 if(!Array.isArray(points)||points.length<2||points.length>10000)throw Error('Trajet invalide');
 for(const p of points)if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.y))throw Error('Coordonnée invalide');
 return points.map((p,i)=>`${i?'L':'M'} ${p.x} ${p.y}`).join(' ');
}
export function previewRouteGeometry(proposal,original){
 if(proposal?.status!=='preview'||!Array.isArray(original)||!Array.isArray(proposal.points))throw Error('Aperçu indisponible');
 return {before:routePreviewPath(original),after:routePreviewPath(proposal.points),edgeId:proposal.edgeId};
}

// v25.1 : garde transactionnelle : refuse toute proposition devenue obsolète.
export function routeRevision(edge,nodes){
 if(!edge||!Array.isArray(nodes))throw Error('Révision invalide');
 const endpoints=[edge.from,edge.to].map(id=>nodes.find(n=>n.id===id));
 if(endpoints.some(n=>!n))throw Error('Extrémité manquante');
 return JSON.stringify({edge:{id:edge.id,from:edge.from,to:edge.to,style:edge.style||'orthogonal',offset:edge.offset||0,fromPort:edge.fromPort||'auto',toPort:edge.toPort||'auto',waypoints:edge.waypoints||[]},endpoints:endpoints.map(n=>({id:n.id,x:n.x,y:n.y,w:n.w??n.width,h:n.h??n.height})),obstacles:nodes.filter(n=>n.id!==edge.from&&n.id!==edge.to).map(n=>({id:n.id,x:n.x,y:n.y,w:n.w??n.width,h:n.h??n.height})).sort((a,b)=>String(a.id).localeCompare(String(b.id)))});
}
export function safeRouteCommit(edge,proposal,nodes,revision){
 if(routeRevision(edge,nodes)!==revision)throw Error('Aperçu obsolète : recalcul nécessaire');
 return applyRouteOffset(edge,proposal);
}

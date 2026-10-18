import {routeEdge,routeViaWaypoints} from "./routing.js";
// Auteur : Abdelhalim Talbi — estimation géométrique non destructive.
const finite=n=>typeof n==='number'&&Number.isFinite(n);
export function centerOf(node){
 if(!node||![node.x,node.y,node.w,node.h].every(finite))return null;
 return {x:node.x+node.w/2,y:node.y+node.h/2};
}
export function segmentsIntersect(a,b,c,d){
 if(![a,b,c,d].every(p=>p&&finite(p.x)&&finite(p.y)))return false;
 const cross=(p,q,r)=>(q.x-p.x)*(r.y-p.y)-(q.y-p.y)*(r.x-p.x);
 const u=cross(a,b,c),v=cross(a,b,d),w=cross(c,d,a),z=cross(c,d,b);
 const eps=1e-8;
 // Croisement strict uniquement : contacts, extrémités et segments colinéaires exclus.
 return ((u>eps&&v<-eps)||(u<-eps&&v>eps))&&((w>eps&&z<-eps)||(w<-eps&&z>eps));
}
// Analyse segment par segment du chemin calculé, avec prise en compte des points de passage.
// Ne prétend pas reproduire les ajustements post-routage du renderer (fan-out, décalage, ports physiques).
export function routePolyline(edge,byId){
 const a=byId.get(edge.from),b=byId.get(edge.to);
 if(!a||!b)return null;
 try{
  const route=Array.isArray(edge.waypoints)&&edge.waypoints.length
   ?routeViaWaypoints(a,b,edge.waypoints,edge.fromPort||'auto',edge.toPort||'auto')
   :routeEdge(a,b,edge.style||'orthogonal',Number(edge.offset)||0,edge.fromPort||'auto',edge.toPort||'auto');
  return route.points.filter(p=>finite(p.x)&&finite(p.y));
 }catch{return null;}
}
export function polylineCrosses(a,b){
 if(!Array.isArray(a)||!Array.isArray(b))return false;
 for(let i=1;i<a.length;i++)for(let j=1;j<b.length;j++)
  if(segmentsIntersect(a[i-1],a[i],b[j-1],b[j]))return true;
 return false;
}
// Lit les points des chemins SVG M/L réellement produits par le moteur de rendu.
// Les commandes courbes ou relatives ne sont pas interprétées : repli sur le modèle.
export function svgPathPolyline(path){
 if(typeof path!=='string'||!path.trim())return null;
 // Lexical validation: do not silently skip unsupported punctuation or malformed numbers.
 // Bound input to avoid a pathological imported SVG freezing the UI.
 if(path.length>100000)return null;
 const tokens=[];const lex=/\s*(?:,\s*)?([A-Za-z]|[-+]?(?:(?:\d+\.?\d*)|(?:\.\d+))(?:[eE][-+]?\d+)?)/y;
 let cursor=0;
 while(cursor<path.length){
  if(!path.slice(cursor).trim())break;
  lex.lastIndex=cursor;const match=lex.exec(path);
  if(!match||match.index!==cursor||tokens.length>=20000)return null;
  tokens.push(match[1]);cursor=lex.lastIndex;
 }
 if(!tokens.length||tokens[0]!=='M')return null;
 const points=[];let i=0,command=null;
 while(i<tokens.length){
  if(/^[A-Za-z]$/.test(tokens[i])){
   command=tokens[i++];if(!['M','L'].includes(command))return null;
  }
  if(i+1>=tokens.length||!command||/^[A-Za-z]$/.test(tokens[i])||/^[A-Za-z]$/.test(tokens[i+1]))return null;
  const x=Number(tokens[i++]),y=Number(tokens[i++]);if(!finite(x)||!finite(y))return null;
  points.push({x,y});if(command==='M')command='L';
 }
 return points.length>=2?points:null;
}
export function renderedCableRoutes(svg){
 const routes=new Map();
 if(!svg?.querySelectorAll)return routes;
 for(const group of svg.querySelectorAll('[data-edge-id]')){
  const id=group.getAttribute('data-edge-id');
  const path=group.querySelector('path.edge');
  const points=svgPathPolyline(path?.getAttribute('d'));
  if(id&&points)routes.set(id,points);
 }
 return routes;
}
export function detectCableCrossings(nodes,edges,renderedRoutes=null){
 const byId=new Map(nodes.map(n=>[n.id,n]));
 const valid=edges.filter(e=>e&&typeof e.id==='string'&&e.from!==e.to)
  .map(e=>({edge:e,points:renderedRoutes?.get(e.id)||routePolyline(e,byId)})).filter(e=>e.points?.length>=2);
 // Sweep line: process only candidates with overlapping horizontal bounding boxes.
 // This avoids quadratic comparison for spatially separated large diagrams.
 const bounds=valid.map(({points})=>{
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  for(const p of points){if(p.x<minX)minX=p.x;if(p.x>maxX)maxX=p.x;if(p.y<minY)minY=p.y;if(p.y>maxY)maxY=p.y;}
  return {minX,maxX,minY,maxY};
 });
 const order=valid.map((_,i)=>i).sort((a,b)=>bounds[a].minX-bounds[b].minX||a-b);
 const active=[];const findings=[];
 for(const i of order){
  const x=bounds[i];
  for(let k=active.length-1;k>=0;k--)if(bounds[active[k]].maxX<=x.minX)active.splice(k,1);
  for(const j of active){
   const y=bounds[j];
   if(x.maxY<=y.minY||y.maxY<=x.minY)continue;
   const a=valid[i].edge,b=valid[j].edge;
   if([a.from,a.to].some(id=>id===b.from||id===b.to))continue;
   if(polylineCrosses(valid[i].points,valid[j].points)){
    // Stable result ordering independent of sweep order.
    const first=i<j?a:b,second=i<j?b:a;
    findings.push({code:'cable-crossing',edgeId:first.id,otherEdgeId:second.id});
   }
  }
  active.push(i);
 }
 findings.sort((a,b)=>a.edgeId.localeCompare(b.edgeId)||a.otherEdgeId.localeCompare(b.otherEdgeId));
 return findings;
}

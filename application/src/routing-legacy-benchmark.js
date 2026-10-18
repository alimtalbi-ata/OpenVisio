// OpenVisio v8.6 — Auteur : Abdelhalim Talbi
const center=n=>({x:n.x+n.w/2,y:n.y+n.h/2});
export function anchor(node, toward) {
 const c=center(node),dx=toward.x-c.x,dy=toward.y-c.y;
 if(Math.abs(dx/node.w)>Math.abs(dy/node.h))
  return {x:dx>=0?node.x+node.w:node.x,y:c.y,side:dx>=0?"right":"left"};
 return {x:c.x,y:dy>=0?node.y+node.h:node.y,side:dy>=0?"bottom":"top"};
}
export const PORT_SIDES = Object.freeze(["auto","left","right","top","bottom"]);
// Les ports suivent la rotation et les symétries visuelles des formes.
export function visualPortAnchor(node,side,toward){
 const raw=portAnchor(node,side,toward),cx=node.x+node.w/2,cy=node.y+node.h/2;
 const angle=((Number(node.rotation)||0)%360+360)%360*Math.PI/180;
 const dx=(raw.x-cx)*(node.flipH?-1:1),dy=(raw.y-cy)*(node.flipV?-1:1);
 return {...raw,x:cx+dx*Math.cos(angle)-dy*Math.sin(angle),y:cy+dx*Math.sin(angle)+dy*Math.cos(angle)};
}
export function portAnchor(node,side,toward){
 if(!PORT_SIDES.includes(side))throw Error("Invalid port side");
 if(!node||![node.x,node.y,node.w,node.h].every(Number.isFinite)||node.w<=0||node.h<=0)throw Error("Invalid port geometry");
 if(side==="auto")return anchor(node,toward);
 const c=center(node);
 if(side==="left")return {x:node.x,y:c.y,side};
 if(side==="right")return {x:node.x+node.w,y:c.y,side};
 if(side==="top")return {x:c.x,y:node.y,side};
 return {x:c.x,y:node.y+node.h,side};
}
export function routeEdge(from,to,style="orthogonal",offset=0,fromPort="auto",toPort="auto"){

 if(!from||!to)throw Error("Missing endpoint");
 const ca=center(from),cb=center(to);
 const a=visualPortAnchor(from,fromPort,cb),b=visualPortAnchor(to,toPort,ca);
 if(style==="straight")return {points:[a,b],path:`M ${a.x} ${a.y} L ${b.x} ${b.y}`};
 const horizontal=a.side==="left"||a.side==="right";
 let pts;
 if(horizontal){
  const mid=(a.x+b.x)/2+offset;
  pts=[a,{x:mid,y:a.y},{x:mid,y:b.y},b];
 }else{
  const mid=(a.y+b.y)/2+offset;
  pts=[a,{x:a.x,y:mid},{x:b.x,y:mid},b];
 }
 return {points:pts,path:pts.map((p,i)=>`${i?"L":"M"} ${p.x} ${p.y}`).join(" ")};
}
export function edgeMidpoint(points){
 if(points.length<2)return {x:0,y:0};
 const segments=points.slice(1).map((p,i)=>({a:points[i],b:p,len:Math.hypot(p.x-points[i].x,p.y-points[i].y)}));
 const half=segments.reduce((s,v)=>s+v.len,0)/2;let elapsed=0;
 for(const s of segments){if(elapsed+s.len>=half){const t=s.len?(half-elapsed)/s.len:0;return {x:s.a.x+(s.b.x-s.a.x)*t,y:s.a.y+(s.b.y-s.a.y)*t};}elapsed+=s.len;}
 return points.at(-1);
}

// Routing rectiligne à segments orthogonaux avec évitement simple des obstacles.
// Le parcours A* est calculé sur une grille bornée ; aucun trajet n'est garanti.
export function intersectsObstacle(a,b,o,margin=8){
 const left=o.x-margin,right=o.x+o.w+margin,top=o.y-margin,bottom=o.y+o.h+margin;
 if(a.x===b.x)return a.x>left&&a.x<right&&Math.max(a.y,b.y)>top&&Math.min(a.y,b.y)<bottom;
 if(a.y===b.y)return a.y>top&&a.y<bottom&&Math.max(a.x,b.x)>left&&Math.min(a.x,b.x)<right;
 return false;
}
export function routeAvoidingObstacles(from,to,obstacles=[],step=20,fromPort="auto",toPort="auto"){
 if(!from||!to||![from,to].every(n=>[n.x,n.y,n.w,n.h].every(Number.isFinite)&&n.w>0&&n.h>0))throw Error("Invalid endpoint geometry");
 if(!Number.isFinite(step)||step<4||step>200)throw Error("Invalid routing grid step");
 if(!Array.isArray(obstacles)||obstacles.length>2000||obstacles.some(n=>!n||![n.x,n.y,n.w,n.h].every(Number.isFinite)||n.w<=0||n.h<=0))throw Error("Invalid routing obstacles");
 const a=visualPortAnchor(from,fromPort,center(to)),b=visualPortAnchor(to,toPort,center(from));
 const round=p=>({x:Math.round(p.x/step)*step,y:Math.round(p.y/step)*step});
 const start=round(a),end=round(b);
 const bounds={minX:Math.max(-200,Math.min(start.x,end.x,...obstacles.map(o=>o.x))-100),maxX:Math.max(start.x,end.x,...obstacles.map(o=>o.x+o.w))+100,minY:Math.max(-200,Math.min(start.y,end.y,...obstacles.map(o=>o.y))-100),maxY:Math.max(start.y,end.y,...obstacles.map(o=>o.y+o.h))+100};
 // Index conservateur par ligne/colonne de grille : ne change pas la géométrie.
 // Les obstacles géants restent dans une liste de secours pour éviter une explosion mémoire.
 const rows=new Map(),cols=new Map(),large=[];
 for(const o of obstacles){
  const loY=Math.ceil((o.y-8)/step),hiY=Math.floor((o.y+o.h+8)/step);
  const loX=Math.ceil((o.x-8)/step),hiX=Math.floor((o.x+o.w+8)/step);
  if(hiY-loY>1000||hiX-loX>1000){large.push(o);continue;}
  for(let y=loY;y<=hiY;y++){if(!rows.has(y))rows.set(y,[]);rows.get(y).push(o);}
  for(let x=loX;x<=hiX;x++){if(!cols.has(x))cols.set(x,[]);cols.get(x).push(o);}
 }
 const blocked=(p,n)=>{
  const candidates=p.y===n.y?rows.get(Math.round(p.y/step)):cols.get(Math.round(p.x/step));
  return (candidates?.some(o=>intersectsObstacle(p,n,o))||false)||large.some(o=>intersectsObstacle(p,n,o));
 };
 const key=p=>`${p.x},${p.y}`,queue=[start],seen=new Set([key(start)]),parents=new Map(),dirs=[[step,0],[-step,0],[0,step],[0,-step]];
 let found=false,iter=0,head=0;
 while(head<queue.length&&iter++<12000){
  const p=queue[head++];
  if(p.x===end.x&&p.y===end.y){found=true;break;}
  for(const [dx,dy] of dirs){
   const n={x:p.x+dx,y:p.y+dy},k=key(n);
   if(n.x<bounds.minX||n.x>bounds.maxX||n.y<bounds.minY||n.y>bounds.maxY||seen.has(k))continue;
   if(blocked(p,n))continue;
   seen.add(k);parents.set(k,p);queue.push(n);
  }
 }
 if(!found)return {...routeEdge(from,to,"orthogonal",0,fromPort,toPort),avoided:false};
 const raw=[end];let p=end;
 while(key(p)!==key(start)){p=parents.get(key(p));if(!p)break;raw.push(p);}
 raw.reverse();
 const pts=[a,...raw,b].filter((p,i,arr)=>i===0||p.x!==arr[i-1].x||p.y!==arr[i-1].y);
 const clean=[];
 for(const p of pts){
  clean.push(p);
  while(clean.length>=3){
   const [x,y,z]=clean.slice(-3);
   if((x.x===y.x&&y.x===z.x)||(x.y===y.y&&y.y===z.y))clean.splice(clean.length-2,1);else break;
  }
 }
 return {points:clean,path:clean.map((p,i)=>`${i?"L":"M"} ${p.x} ${p.y}`).join(" "),avoided:true};
}

export function routeViaWaypoints(from,to,waypoints=[],fromPort="auto",toPort="auto"){
 if(!Array.isArray(waypoints)||waypoints.some(p=>!p||!Number.isFinite(p.x)||!Number.isFinite(p.y)))throw Error("Invalid waypoints");
 const a=visualPortAnchor(from,fromPort,waypoints[0]||center(to)),b=visualPortAnchor(to,toPort,waypoints.at(-1)||center(from));
 const points=[a,...waypoints,b];
 return {points,path:points.map((p,i)=>`${i?"L":"M"} ${p.x} ${p.y}`).join(" "),manual:true};
}
export function parseWaypoints(value){
 if(typeof value!=="string"||!value.trim())return [];
 const points=value.split(";").map(pair=>pair.trim().split(",").map(Number));
 if(points.length>30||points.some(p=>p.length!==2||p.some(v=>!Number.isFinite(v)||Math.abs(v)>100000)))throw Error("Format attendu : x,y ; x,y");
 return points.map(([x,y])=>({x,y}));
}
export function serializeWaypoints(points=[]){return points.map(p=>`${p.x},${p.y}`).join("; ");}

// Géométrie indépendante du DOM, testable sans navigateur.
export function projectOnSegment(point,a,b){
 const dx=b.x-a.x,dy=b.y-a.y,denom=dx*dx+dy*dy;
 const t=denom?Math.max(0,Math.min(1,((point.x-a.x)*dx+(point.y-a.y)*dy)/denom)):0;
 const projected={x:a.x+t*dx,y:a.y+t*dy};
 return {point:projected,t,distance2:(point.x-projected.x)**2+(point.y-projected.y)**2};
}
export function nearestSegmentIndex(points,point){
 if(!Array.isArray(points)||points.length<2)throw Error("At least two points required");
 let best={index:0,distance2:Infinity};
 for(let i=0;i<points.length-1;i++){
  const candidate=projectOnSegment(point,points[i],points[i+1]);
  if(candidate.distance2<best.distance2)best={index:i,distance2:candidate.distance2};
 }
 return best.index;
}
export function insertWaypoint(from,to,waypoints,point,style="orthogonal",offset=0){
 if(!Number.isFinite(point?.x)||!Number.isFinite(point?.y))throw Error("Invalid waypoint");
 if(!Array.isArray(waypoints)||waypoints.length>=30)throw Error("Waypoint limit");
 const route=waypoints.length?routeViaWaypoints(from,to,waypoints):routeEdge(from,to,style,offset);
 const segment=nearestSegmentIndex(route.points,point);
 // Pour un chemin automatique comportant plusieurs segments, le premier point
 // manuel est inséré comme waypoint unique ; il conserve le chemin complet via
 // l'éditeur, sans prétendre reproduire les coudes automatiques précédents.
 const index=waypoints.length?Math.max(0,Math.min(waypoints.length,segment)):0;
 const result=waypoints.map(p=>({...p}));
 result.splice(index,0,{x:point.x,y:point.y});
 return result;
}


// Mesure des croisements entre connexions orthogonales (hors contacts aux extrémités).
// Fonction pure utilisable pour diagnostiquer les grands diagrammes.
export function countRouteCrossings(routes){
 if(!Array.isArray(routes))throw Error("Routes must be an array");
 const segments=routes.map(route=>{
  if(!Array.isArray(route?.points)||route.points.some(p=>!Number.isFinite(p?.x)||!Number.isFinite(p?.y)))throw Error("Invalid route");
  return route.points.slice(1).map((b,i)=>[route.points[i],b]).filter(([a,b])=>a.x!==b.x||a.y!==b.y);
 });
 let count=0;
 for(let i=0;i<segments.length;i++)for(let j=i+1;j<segments.length;j++){
  for(const [a,b] of segments[i])for(const [c,e] of segments[j]){
   const av=a.x===b.x,ah=a.y===b.y,cv=c.x===e.x,ch=c.y===e.y;
   if(!((av&&ch)||(ah&&cv)))continue;
   const v=av?[a,b]:[c,e],h=ah?[a,b]:[c,e],x=v[0].x,y=h[0].y;
   if(x>Math.min(h[0].x,h[1].x)&&x<Math.max(h[0].x,h[1].x)&&y>Math.min(v[0].y,v[1].y)&&y<Math.max(v[0].y,v[1].y))count++;
  }
 }
 return count;
}

// V21.9 — longueur des segments colinéaires partagés entre liaisons distinctes.
// Les contacts ponctuels et les segments de longueur nulle ne sont pas pénalisés.
export function routeSharedLength(a,b){
 if(!Array.isArray(a?.points)||!Array.isArray(b?.points))throw Error("Invalid route points");
 const segments=r=>r.points.slice(1).map((end,i)=>[r.points[i],end]);
 let total=0;
 for(const [p,q] of segments(a))for(const [u,v] of segments(b)){
  if(![p,q,u,v].every(t=>Number.isFinite(t?.x)&&Number.isFinite(t?.y)))throw Error("Invalid route geometry");
  if(p.y===q.y&&u.y===v.y&&p.y===u.y)
   total+=Math.max(0,Math.min(Math.max(p.x,q.x),Math.max(u.x,v.x))-Math.max(Math.min(p.x,q.x),Math.min(u.x,v.x)));
  else if(p.x===q.x&&u.x===v.x&&p.x===u.x)
   total+=Math.max(0,Math.min(Math.max(p.y,q.y),Math.max(u.y,v.y))-Math.max(Math.min(p.y,q.y),Math.min(u.y,v.y)));
 }
 return total;
}
export function totalRouteSharedLength(routes){
 if(!Array.isArray(routes))throw Error("Routes must be an array");
 let total=0;
 for(let i=0;i<routes.length;i++)for(let j=i+1;j<routes.length;j++)total+=routeSharedLength(routes[i],routes[j]);
 return total;
}

// Choisit parmi plusieurs décalages de connecteur le tracé présentant le moins
// de croisements stricts avec les connexions déjà placées ; ne déplace aucun équipement.
export function routeWithFewerCrossings(from,to,existingRoutes=[],offsets=[0,-40,40,-80,80]){
 if(!Array.isArray(offsets)||!offsets.length||offsets.some(x=>!Number.isFinite(x)))throw Error("Invalid offsets");
 let best=null;
 for(const offset of offsets){
  const candidate=routeEdge(from,to,"orthogonal",offset);
  const crossings=countRouteCrossings([...existingRoutes,candidate]);
  const shared=existingRoutes.reduce((n,r)=>n+routeSharedLength(r,candidate),0);
  const score=crossings*100000+shared*10+Math.abs(offset);
  if(!best||score<best.score)best={...candidate,crossings,offset,score};
 }
 const {score,...result}=best;
 return result;
}

// v15.3 — routage intelligent : ports candidats et obstacles, sans altérer les formes.
export function routeSmart(from,to,obstacles=[],existingRoutes=[],{fast=false}={}){
 if(!from||!to)throw Error("Missing endpoint");
 const choices=["left","right","top","bottom"];
 const candidates=[];
 const dx=center(to).x-center(from).x,dy=center(to).y-center(from).y;
 const preferred=Math.abs(dx)>=Math.abs(dy)?[dx>=0?"right":"left",dx>=0?"left":"right"]:[dy>=0?"bottom":"top",dy>=0?"top":"bottom"];
 const pairs=fast?[preferred,["left","right"],["right","left"],["top","bottom"],["bottom","top"]].filter((p,i,a)=>a.findIndex(q=>q[0]===p[0]&&q[1]===p[1])===i):choices.flatMap(a=>choices.map(b=>[a,b]));
 for(const [a,b] of pairs){
  const route=routeAvoidingObstacles(from,to,obstacles,20,a,b);
  const segments=route.points.slice(1).map((p,i)=>[route.points[i],p]);
  const length=segments.reduce((n,[p,q])=>n+Math.hypot(q.x-p.x,q.y-p.y),0);
  const bends=Math.max(0,segments.length-1);
  const collisions=segments.reduce((n,[p,q])=>n+obstacles.filter(o=>intersectsObstacle(p,q,o)).length,0);
  const crossings=segments.reduce((n,[p,q])=>n+existingRoutes.reduce((v,other)=>v+(other.points||[]).slice(1).filter((t,i)=>{
   const u=other.points[i];
   if(p.x===q.x&&u.y===t.y)return Math.min(p.y,q.y)<u.y&&u.y<Math.max(p.y,q.y)&&Math.min(u.x,t.x)<p.x&&p.x<Math.max(u.x,t.x);
   if(p.y===q.y&&u.x===t.x)return Math.min(p.x,q.x)<u.x&&u.x<Math.max(p.x,q.x)&&Math.min(u.y,t.y)<p.y&&p.y<Math.max(u.y,t.y);
   return false;
  }).length,0),0);
  candidates.push({...route,fromPort:a,toPort:b,score:length+bends*12+collisions*100000+crossings*80+(route.avoided?0:10000)});
 }
 candidates.sort((a,b)=>a.score-b.score||choices.indexOf(a.fromPort)-choices.indexOf(b.fromPort)||choices.indexOf(a.toPort)-choices.indexOf(b.toPort));
 return candidates[0];
}

// Optimisation globale déterministe : les chemins manuels restent intacts.
// Trie les connexions automatiques les plus contraintes avant routage, puis
// tente deux ordres et retient le meilleur selon croisements, longueur et coudes.
export function optimizeConnectionOrder(edges,nodes,route,{passes=2}={}){
 if(!Array.isArray(edges)||!Array.isArray(nodes)||typeof route!=="function")throw Error("Invalid routing input");
 const byId=new Map(nodes.map(n=>[n.id,n]));
 const distance=e=>{const a=byId.get(e.from),b=byId.get(e.to);return a&&b?Math.hypot(a.x+a.w/2-b.x-b.w/2,a.y+a.h/2-b.y-b.h/2):Infinity;};
 const manual=edges.filter(e=>e.waypoints?.length),automatic=edges.filter(e=>!e.waypoints?.length);
 const largeGraph=edges.length>160;
 const orders=largeGraph?[automatic.slice()]:[automatic.slice(),automatic.slice().sort((a,b)=>distance(a)-distance(b)||String(a.id).localeCompare(String(b.id)))];
 let best=null;
 for(const order of orders.slice(0,Math.max(1,Math.min(2,passes)))){
  const placed=[],result=new Map();
  for(const e of [...manual,...order]){
   const a=byId.get(e.from),b=byId.get(e.to);if(!a||!b)continue;
   const r=route(e,a,b,placed);
   result.set(e.id,r);placed.push(r);
  }
  const crossings=largeGraph?0:countRouteCrossings(placed);
  const length=placed.reduce((total,r)=>total+r.points.slice(1).reduce((n,p,i)=>n+Math.hypot(p.x-r.points[i].x,p.y-r.points[i].y),0),0);
  const bends=placed.reduce((n,r)=>n+Math.max(0,r.points.length-2),0);
  const sharedLength=largeGraph?0:totalRouteSharedLength(placed);
  const score=crossings*10000+sharedLength*10+length+bends*12;
  if(!best||score<best.score)best={routes:result,score,crossings,length,bends,sharedLength};
 }
 return {...(best||{routes:new Map(),score:0,crossings:0,length:0,bends:0,sharedLength:0}),crossingsEvaluated:!largeGraph};
}


// v16.1 — écarte les liaisons automatiques strictement superposées.
// Les extrémités restent ancrées sur les équipements ; les chemins manuels
// et les chemins comportant plusieurs coudes ne sont jamais modifiés.
export function separateParallelRoutes(edges, routes, {spacing=12,maxLanes=9,obstacles=[]}={}){
 if(!Array.isArray(edges)||!(routes instanceof Map)||!Number.isFinite(spacing)||spacing<=0||!Number.isInteger(maxLanes)||maxLanes<1)throw Error("Invalid lane configuration");
 const result=new Map(routes),groups=new Map();
 for(const edge of edges){
  const route=routes.get(edge.id);
  if(!route||edge.waypoints?.length||!Array.isArray(route.points)||route.points.length<2)continue;
  if(!route.points.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)))continue;
  if(!route.points.slice(1).every((p,i)=>p.x===route.points[i].x||p.y===route.points[i].y))continue;
  const key=route.points.map(p=>`${p.x}:${p.y}`).join("|");
  if(!groups.has(key))groups.set(key,[]);
  groups.get(key).push(edge.id);
 }
 for(const ids of groups.values()){
  if(ids.length<2)continue;
  // v22.1: stable lane assignment regardless of edge insertion order.
  const lanes=planParallelLanes(ids,{spacing,maxLanes});
  for(const [id,offset] of lanes){
   const r=routes.get(id);
   if(Math.abs(offset)<0.001)continue;
   const pts=r.points;
   // Decale les segments orthogonaux, puis raccorde leurs intersections.
   // Les ancrages d'origine et de destination restent immuables.
   const segments=[];
   for(let j=1;j<pts.length;j++){
    const a=pts[j-1],b=pts[j];
    if(a.x===b.x&&a.y===b.y)continue;
    const horizontal=a.y===b.y;
    segments.push({horizontal,coord:(horizontal?a.y:a.x)+offset,a,b});
   }
   if(!segments.length)continue;
   const inner=[];
   const first=segments[0];
   inner.push(first.horizontal?{x:pts[0].x,y:first.coord}:{x:first.coord,y:pts[0].y});
   for(let j=1;j<segments.length;j++){
    const prev=segments[j-1],cur=segments[j];
    if(prev.horizontal!==cur.horizontal){
     inner.push(prev.horizontal?{x:cur.coord,y:prev.coord}:{x:prev.coord,y:cur.coord});
    }else{
     // Conserve un coude intermediaire en cas de segments colineaires.
     inner.push(prev.horizontal?{x:cur.a.x,y:prev.coord}:{x:prev.coord,y:cur.a.y});
     inner.push(cur.horizontal?{x:cur.a.x,y:cur.coord}:{x:cur.coord,y:cur.a.y});
    }
   }
   const last=segments.at(-1);
   inner.push(last.horizontal?{x:pts.at(-1).x,y:last.coord}:{x:last.coord,y:pts.at(-1).y});
   const raw=[pts[0],...inner,pts.at(-1)];
   const points=raw.filter((p,j)=>j===0||p.x!==raw[j-1].x||p.y!==raw[j-1].y);
   // Aucun faisceau ne doit traverser une forme pour gagner quelques pixels.
   const collision=obstacles.some(n=>{
    if(!Number.isFinite(n.x)||!Number.isFinite(n.y)||!Number.isFinite(n.w)||!Number.isFinite(n.h))return false;
    const left=n.x,top=n.y,right=n.x+n.w,bottom=n.y+n.h;
    return points.slice(1).some((b,j)=>{
     const a=points[j];
     if(a.x===b.x)return a.x>left&&a.x<right&&Math.max(a.y,b.y)>top&&Math.min(a.y,b.y)<bottom;
     if(a.y===b.y)return a.y>top&&a.y<bottom&&Math.max(a.x,b.x)>left&&Math.min(a.x,b.x)<right;
     return false;
    });
   });
   if(collision)continue;
   result.set(id,{...r,points,path:points.map((v,j)=>`${j?'L':'M'} ${v.x} ${v.y}`).join(' '),laneOffset:offset});
  }
 }
 return result;
}


// v22.2 — diagnostic read-only, bounded for large SAN topology reports.
// Never modifies a route, edge or node. Counts only strict interior crossings.
export function diagnoseRouteTopology(routes, obstacles=[], {maxSegments=12000}={}){
 if(!(routes instanceof Map)||!Array.isArray(obstacles)||!Number.isInteger(maxSegments)||maxSegments<1)throw Error("Invalid routing diagnostic input");
 const segments=[];let invalidRoutes=0,collisions=0,overlaps=0,crossings=0,truncated=false;
 for(const [id,route] of routes){
  const pts=route?.points;
  if(!Array.isArray(pts)||pts.length<2||pts.some(p=>!p||!Number.isFinite(p.x)||!Number.isFinite(p.y))){invalidRoutes++;continue;}
  for(let i=1;i<pts.length;i++){
   const a=pts[i-1],b=pts[i];
   if(a.x!==b.x&&a.y!==b.y){invalidRoutes++;continue;}
   if(a.x===b.x&&a.y===b.y)continue;
   if(segments.length>=maxSegments){truncated=true;break;}
   const horizontal=a.y===b.y;
   const seg={id,horizontal,c:horizontal?a.y:a.x,lo:horizontal?Math.min(a.x,b.x):Math.min(a.y,b.y),hi:horizontal?Math.max(a.x,b.x):Math.max(a.y,b.y)};
   for(const o of obstacles){
    if(!o||![o.x,o.y,o.w,o.h].every(Number.isFinite)||o.w<=0||o.h<=0)continue;
    if(horizontal ? seg.c>o.y&&seg.c<o.y+o.h&&seg.hi>o.x&&seg.lo<o.x+o.w : seg.c>o.x&&seg.c<o.x+o.w&&seg.hi>o.y&&seg.lo<o.y+o.h)collisions++;
   }
   segments.push(seg);
  }
  if(truncated)break;
 }
 // O(n²) pair scan is intentionally disabled for large sets to bound UI latency.
 const pairAnalysisComplete=segments.length<=1500&&!truncated;
 if(pairAnalysisComplete)for(let i=0;i<segments.length;i++)for(let j=i+1;j<segments.length;j++){
  const a=segments[i],b=segments[j];if(a.id===b.id)continue;
  if(a.horizontal===b.horizontal){if(a.c===b.c&&Math.min(a.hi,b.hi)>Math.max(a.lo,b.lo))overlaps++;}
  else{const h=a.horizontal?a:b,v=a.horizontal?b:a;if(v.c>h.lo&&v.c<h.hi&&h.c>v.lo&&h.c<v.hi)crossings++;}
 }
 return {routes:routes.size,segments:segments.length,invalidRoutes,obstacleCollisions:collisions,overlappingSegmentPairs:pairAnalysisComplete?overlaps:null,crossingPairs:pairAnalysisComplete?crossings:null,pairAnalysisComplete,truncated};
}

// v16.3: distribute overlapping internal orthogonal segments even when the
// complete routes differ. Conservative: only segments with room for two jogs.
export function separateSharedSegments(edges,routes,{spacing=10,obstacles=[]}={}){
 if(!Array.isArray(edges)||!(routes instanceof Map)||!Number.isFinite(spacing)||spacing<=0)throw Error("Invalid shared-segment configuration");
 const result=new Map(routes), groups=new Map(), eligible=new Set(edges.filter(e=>!e.waypoints?.length).map(e=>e.id));
 const keyFor=(a,b)=>a.y===b.y?`H:${a.y}:${Math.min(a.x,b.x)}:${Math.max(a.x,b.x)}`:a.x===b.x?`V:${a.x}:${Math.min(a.y,b.y)}:${Math.max(a.y,b.y)}`:null;
 for(const [id,r] of routes){
  if(!eligible.has(id)||!Array.isArray(r?.points)||r.points.length<4)continue;
  for(let j=1;j<r.points.length-2;j++){
   const a=r.points[j],b=r.points[j+1],key=keyFor(a,b);
   if(!key||Math.hypot(b.x-a.x,b.y-a.y)<spacing*5)continue;
   if(!groups.has(key))groups.set(key,[]);
   groups.get(key).push({id,j});
  }
 }
 const modified=new Set();
 for(const group of groups.values()){
  const distinct=[...new Map(group.map(x=>[x.id,x])).values()].filter(x=>!modified.has(x.id)).sort((a,b)=>String(a.id).localeCompare(String(b.id)));
  if(distinct.length<2)continue;
  const count=Math.min(distinct.length,7); // bornage des voies pour limiter l’encombrement
  for(let k=0;k<count;k++){
   const {id,j}=distinct[k],r=result.get(id),p=r.points;
   const offset=(k-(count-1)/2)*spacing;
   if(Math.abs(offset)<0.01)continue;
   const a=p[j],b=p[j+1],horizontal=a.y===b.y;
   const inset=Math.min(spacing*1.5,Math.hypot(b.x-a.x,b.y-a.y)/4);
   const sign=horizontal?Math.sign(b.x-a.x):Math.sign(b.y-a.y);
   const q1=horizontal?{x:a.x+sign*inset,y:a.y}:{x:a.x,y:a.y+sign*inset};
   const q2=horizontal?{x:b.x-sign*inset,y:b.y}:{x:b.x,y:b.y-sign*inset};
   const shifted1=horizontal?{x:q1.x,y:q1.y+offset}:{x:q1.x+offset,y:q1.y};
   const shifted2=horizontal?{x:q2.x,y:q2.y+offset}:{x:q2.x+offset,y:q2.y};
   const points=[...p.slice(0,j+1),q1,shifted1,shifted2,q2,...p.slice(j+1)];
   const collides=obstacles.some(n=>Number.isFinite(n.x)&&Number.isFinite(n.y)&&Number.isFinite(n.w)&&Number.isFinite(n.h)&&points.slice(1).some((v,i)=>{
    const u=points[i],l=n.x,t=n.y,rr=l+n.w,bb=t+n.h;
    return u.x===v.x?u.x>l&&u.x<rr&&Math.max(u.y,v.y)>t&&Math.min(u.y,v.y)<bb:u.y===v.y?u.y>t&&u.y<bb&&Math.max(u.x,v.x)>l&&Math.min(u.x,v.x)<rr:true;
   }));
   if(collides)continue;
   result.set(id,{...r,points,path:points.map((v,i)=>`${i?'L':'M'} ${v.x} ${v.y}`).join(' '),sharedLaneOffset:offset});
   modified.add(id);
  }
 }
 return result;
}


// v16.4 — détecte les portions colinéaires qui se chevauchent même si les
// extrémités des segments diffèrent. Uniquement les segments internes automatiques.
export function findPartialOverlaps(edges,routes,{minLength=30}={}){
 if(!Array.isArray(edges)||!(routes instanceof Map)||!Number.isFinite(minLength)||minLength<=0)throw Error("Invalid overlap configuration");
 const eligible=new Set(edges.filter(e=>!e.waypoints?.length).map(e=>e.id));
 const segments=[];
 for(const [id,r] of routes){
  if(!eligible.has(id)||!Array.isArray(r?.points)||r.points.length<4)continue;
  const p=r.points;
  for(let j=1;j<p.length-2;j++){
   const a=p[j],b=p[j+1];
   if(![a?.x,a?.y,b?.x,b?.y].every(Number.isFinite))continue;
   const horizontal=a.y===b.y,vertical=a.x===b.x;
   if(!horizontal&&!vertical||a.x===b.x&&a.y===b.y)continue;
   segments.push({id,j,axis:horizontal?'H':'V',coord:horizontal?a.y:a.x,start:Math.min(horizontal?a.x:a.y,horizontal?b.x:b.y),end:Math.max(horizontal?a.x:a.y,horizontal?b.x:b.y)});
  }
 }
 const overlaps=[];
 for(let i=0;i<segments.length;i++)for(let k=i+1;k<segments.length;k++){
  const a=segments[i],b=segments[k];
  if(a.id===b.id||a.axis!==b.axis||a.coord!==b.coord)continue;
  const start=Math.max(a.start,b.start),end=Math.min(a.end,b.end);
  if(end-start>=minLength)overlaps.push({a,b,start,end,length:end-start});
 }
 return overlaps.sort((a,b)=>b.length-a.length||String(a.a.id).localeCompare(String(b.a.id))||String(a.b.id).localeCompare(String(b.b.id)));
}

export function separatePartialOverlaps(edges,routes,{spacing=10,minLength=40,obstacles=[]}={}){
 if(!Number.isFinite(spacing)||spacing<=0||!Array.isArray(obstacles))throw Error("Invalid separation configuration");
 const result=new Map(routes),modified=new Set();
 for(const overlap of findPartialOverlaps(edges,routes,{minLength})){
  const pair=[overlap.a,overlap.b];
  // Déplace au maximum un segment par route et ne modifie jamais les ancrages.
  for(let lane=0;lane<pair.length;lane++){
   const seg=pair[lane];if(modified.has(seg.id))continue;
   const r=result.get(seg.id),p=r.points,a=p[seg.j],b=p[seg.j+1];
   const horizontal=seg.axis==='H',sign=(horizontal?b.x-a.x:b.y-a.y)>=0?1:-1;
   const inset=Math.min(spacing,overlap.length/5);
   const start=overlap.start+inset,end=overlap.end-inset;
   if(end<=start)continue;
   const offset=(lane===0?-1:1)*spacing/2;
   const before=horizontal?{x:sign>0?start:end,y:a.y}:{x:a.x,y:sign>0?start:end};
   const after=horizontal?{x:sign>0?end:start,y:a.y}:{x:a.x,y:sign>0?end:start};
   const movedBefore=horizontal?{x:before.x,y:before.y+offset}:{x:before.x+offset,y:before.y};
   const movedAfter=horizontal?{x:after.x,y:after.y+offset}:{x:after.x+offset,y:after.y};
   const points=[...p.slice(0,seg.j+1),before,movedBefore,movedAfter,after,...p.slice(seg.j+1)];
   const blocked=obstacles.some(n=>Number.isFinite(n?.x)&&Number.isFinite(n?.y)&&Number.isFinite(n?.w)&&Number.isFinite(n?.h)&&points.slice(1).some((v,i)=>{
    const u=points[i],l=n.x,t=n.y,rr=l+n.w,bb=t+n.h;
    if(u.x===v.x)return u.x>l&&u.x<rr&&Math.max(u.y,v.y)>t&&Math.min(u.y,v.y)<bb;
    if(u.y===v.y)return u.y>t&&u.y<bb&&Math.max(u.x,v.x)>l&&Math.min(u.x,v.x)<rr;
    return true;
   }));
   if(blocked)continue;
   result.set(seg.id,{...r,points,path:points.map((v,i)=>`${i?'L':'M'} ${v.x} ${v.y}`).join(' '),partialLaneOffset:offset});
   modified.add(seg.id);
  }
 }
 return result;
}

// V16.5 : éventail des ancrages automatiques, sans déplacer les formes.
export function distributeEndpointAnchors(edges,routes,nodes,{margin=14,minimumGap=9}={}){
 if(!Array.isArray(edges)||!(routes instanceof Map)||!Array.isArray(nodes)||!Number.isFinite(margin)||margin<0||!Number.isFinite(minimumGap)||minimumGap<=0)throw Error("Invalid endpoint distribution");
 const byId=new Map(nodes.map(n=>[n.id,n])), groups=new Map(), result=new Map(routes);
 for(const edge of edges){
  if(edge.waypoints?.length||edge.sourceInterface||edge.targetInterface)continue;
  const route=routes.get(edge.id);if(!route?.points||route.points.length<2)continue;
  for(const end of [0,1]){
   if((end===0?edge.fromPort:edge.toPort)&& (end===0?edge.fromPort:edge.toPort)!=="auto")continue;
   const node=byId.get(end===0?edge.from:edge.to);if(!node||node.rotation||node.flipH||node.flipV)continue;
   const p=route.points[end===0?0:route.points.length-1], eps=0.001;
   const side=Math.abs(p.x-node.x)<eps?"left":Math.abs(p.x-node.x-node.w)<eps?"right":Math.abs(p.y-node.y)<eps?"top":Math.abs(p.y-node.y-node.h)<eps?"bottom":null;
   if(!side)continue;
   const key=`${node.id}:${side}`;if(!groups.has(key))groups.set(key,[]);
   const other=route.points[end===0?route.points.length-1:0];
   groups.get(key).push({edge,end,node,side,sort:side==="left"||side==="right"?other.y:other.x});
  }
 }
 for(const group of groups.values()){
  if(group.length<2)continue;
  group.sort((a,b)=>a.sort-b.sort||String(a.edge.id).localeCompare(String(b.edge.id)));
  const {node,side}=group[0],vertical=side==="left"||side==="right";
  const lo=(vertical?node.y:node.x)+margin,hi=(vertical?node.y+node.h:node.x+node.w)-margin;
  if(hi<=lo||hi-lo<(group.length-1)*minimumGap)continue;
  for(let i=0;i<group.length;i++){
   const {edge,end}=group[i],r=result.get(edge.id),pts=r.points.map(p=>({...p}));
   const idx=end===0?0:pts.length-1,adj=end===0?1:pts.length-2;
   const desired=lo+(hi-lo)*(i+1)/(group.length+1);
   if(vertical){pts[idx].y=desired; if(pts.length>2&&Math.abs(pts[adj].y-r.points[idx].y)<.001)pts[adj].y=desired;}
   else{pts[idx].x=desired;if(pts.length>2&&Math.abs(pts[adj].x-r.points[idx].x)<.001)pts[adj].x=desired;}
   result.set(edge.id,{...r,points:pts,path:pts.map((p,j)=>`${j?'L':'M'} ${p.x} ${p.y}`).join(' '),distributedAnchors:true});
  }
 }
 return result;
}

// V16.6 — sorties orthogonales en éventail, avec validation des obstacles.
export function orthogonalFanOut(edges,routes,nodes,{stub=16}={}){
 if(!Array.isArray(edges)||!(routes instanceof Map)||!Array.isArray(nodes)||!Number.isFinite(stub)||stub<=0)throw Error("Invalid fan-out configuration");
 const byId=new Map(nodes.map(n=>[n.id,n])),result=new Map(routes);
 const pathOf=points=>points.map((p,i)=>`${i?'L':'M'} ${p.x} ${p.y}`).join(' ');
 const blocked=(points,from,to)=>nodes.some(n=>{
  if(n.id===from||n.id===to)return false;
  const l=n.x,t=n.y,r=l+n.w,b=t+n.h;
  return points.slice(1).some((v,i)=>{const u=points[i];
   if(u.x===v.x)return u.x>l&&u.x<r&&Math.max(u.y,v.y)>t&&Math.min(u.y,v.y)<b;
   if(u.y===v.y)return u.y>t&&u.y<b&&Math.max(u.x,v.x)>l&&Math.min(u.x,v.x)<r;
   return true;
  });
 });
 for(const edge of edges){
  const route=result.get(edge.id);if(!route?.distributedAnchors||edge.waypoints?.length||edge.sourceInterface||edge.targetInterface)continue;
  let pts=route.points.map(p=>({...p})),changed=false;
  for(const end of [0,1]){
   const port=end===0?edge.fromPort:edge.toPort;if(port&&port!=='auto')continue;
   const node=byId.get(end===0?edge.from:edge.to);if(!node||node.rotation||node.flipH||node.flipV)continue;
   const p=end===0?pts[0]:pts.at(-1),neighbor=end===0?pts[1]:pts.at(-2);
   if(!p||!neighbor)continue;
   const eps=.001;let outward=null;
   if(Math.abs(p.x-node.x)<eps)outward={x:-1,y:0};
   else if(Math.abs(p.x-node.x-node.w)<eps)outward={x:1,y:0};
   else if(Math.abs(p.y-node.y)<eps)outward={x:0,y:-1};
   else if(Math.abs(p.y-node.y-node.h)<eps)outward={x:0,y:1};
   if(!outward)continue;
   const tip={x:p.x+outward.x*stub,y:p.y+outward.y*stub};
   const corner=outward.x?{x:tip.x,y:neighbor.y}:{x:neighbor.x,y:tip.y};
   const candidate=end===0?[p,tip,corner,...pts.slice(1)]:[...pts.slice(0,-1),corner,tip,p];
   // Keep a short orthogonal stub, but reject reversals and obstacle collisions.
   const forward=(neighbor.x-p.x)*outward.x+(neighbor.y-p.y)*outward.y;
   if(forward<stub||blocked(candidate,edge.from,edge.to))continue;
   if(candidate.slice(1).some((v,i)=>v.x!==candidate[i].x&&v.y!==candidate[i].y))continue;
   pts=candidate;changed=true;
  }
  if(changed)result.set(edge.id,{...route,points:pts,path:pathOf(pts),orthogonalFanOut:true});
 }
 return result;
}


// v16.7 — accepte uniquement les améliorations locales sans collision ni
// augmentation du nombre de croisements. Budget borne pour grands graphes.
export function reduceFanOutCrossings(edges,routes,nodes,{maxEdges=160,offsets=[0,-8,8,-16,16]}={}){
 if(!Array.isArray(edges)||!(routes instanceof Map)||!Array.isArray(nodes)||!Number.isInteger(maxEdges)||maxEdges<1||!Array.isArray(offsets)||!offsets.every(Number.isFinite))throw Error("Invalid crossing reduction input");
 const result=new Map(routes);
 if(edges.length>maxEdges)return result;
 const eligible=edges.filter(e=>!e.waypoints?.length&&!e.sourceInterface&&!e.targetInterface&&result.get(e.id)?.orthogonalFanOut);
 const same=(a,b)=>Math.abs(a-b)<.001;
 const orthogonal=pts=>pts.slice(1).every((p,i)=>same(p.x,pts[i].x)||same(p.y,pts[i].y));
 const blocked=(pts,e)=>nodes.some(n=>n.id!==e.from&&n.id!==e.to&&pts.slice(1).some((p,i)=>intersectsObstacle(pts[i],p,n,0)));
 // V41.33: compare only crossings involving the candidate route.
 // Crossings between unchanged routes are constant for every candidate,
 // so excluding them preserves the original ordering exactly.
 const score=(e,r,others)=>{
  const crosses=countRouteCrossings([...others,r]);
  const length=r.points.slice(1).reduce((sum,p,i)=>sum+Math.abs(p.x-r.points[i].x)+Math.abs(p.y-r.points[i].y),0);
  return crosses*10000+length;
 };
 for(const e of eligible){
  const original=result.get(e.id);if(!orthogonal(original.points)||blocked(original.points,e))continue;
  const others=edges.filter(x=>x.id!==e.id).map(x=>result.get(x.id)).filter(Boolean);
  let best=original,bestScore=score(e,original,others);
  // Move only an internal straight segment, retaining endpoint stubs and ports.
  for(let i=2;i<original.points.length-2;i++){
   const pts=original.points;
   const a=pts[i-1],b=pts[i],c=pts[i+1],d=pts[i+2];
   const horizontal=same(b.y,c.y),vertical=same(b.x,c.x);
   if(!horizontal&&!vertical)continue;
   if(horizontal&&(!same(a.x,b.x)||!same(c.x,d.x)))continue;
   if(vertical&&(!same(a.y,b.y)||!same(c.y,d.y)))continue;
   for(const shift of offsets){if(!shift)continue;
    const candidate=pts.map(p=>({...p}));
    if(horizontal){candidate[i].y+=shift;candidate[i+1].y+=shift;}
    else{candidate[i].x+=shift;candidate[i+1].x+=shift;}
    if(!orthogonal(candidate)||blocked(candidate,e))continue;
    const r={...original,points:candidate,path:candidate.map((p,j)=>`${j?'L':'M'} ${p.x} ${p.y}`).join(' ')};
    const v=score(e,r,others);if(v<bestScore-0.001){best=r;bestScore=v;}
   }
  }
  if(best!==original)result.set(e.id,{...best,crossingOptimized:true});
 }
 return result;
}

// v22.0 — attribution stable des voies parallèles, indépendante de l’ordre d’entrée.
export function planParallelLanes(edgeIds,{spacing=10,maxLanes=7}={}){
 if(!Array.isArray(edgeIds)||!Number.isFinite(spacing)||spacing<=0||!Number.isInteger(maxLanes)||maxLanes<1)throw Error('Invalid parallel lane configuration');
 const ids=[...new Set(edgeIds.map(String))].sort((a,b)=>a.localeCompare(b));
 const selected=ids.slice(0,maxLanes), center=(selected.length-1)/2;
 return new Map(selected.map((id,i)=>[id,(i-center)*spacing]));
}

// v22.4 — anomalies géométriques localisables, sans modifier les routes.
export function locateRouteAnomalies(routes,{maxSegments=1200,maxFindings=200}={}){
 if(!(routes instanceof Map)||!Number.isInteger(maxSegments)||maxSegments<1||!Number.isInteger(maxFindings)||maxFindings<1)throw Error('Invalid anomaly limits');
 const segments=[],findings=[],seen=new Set();let truncated=false;
 const add=(code,a,b)=>{const ids=b?[String(a),String(b)].sort():[String(a)];const key=code+':'+ids.join(':');if(seen.has(key))return;seen.add(key);if(findings.length>=maxFindings){truncated=true;return;}findings.push({code,edgeId:ids[0],otherEdgeId:ids[1]||null});};
 for(const [id,route] of routes){
  const pts=route?.points;if(!Array.isArray(pts)||pts.length<2||pts.some(p=>!p||!Number.isFinite(p.x)||!Number.isFinite(p.y))){add('invalid-route',id);continue;}
  for(let i=1;i<pts.length;i++){const a=pts[i-1],b=pts[i];if(a.x!==b.x&&a.y!==b.y){add('invalid-route',id);continue;}if(a.x===b.x&&a.y===b.y)continue;
   if(segments.length>=maxSegments){truncated=true;break;}const h=a.y===b.y;segments.push({id,h,c:h?a.y:a.x,lo:h?Math.min(a.x,b.x):Math.min(a.y,b.y),hi:h?Math.max(a.x,b.x):Math.max(a.y,b.y)});
  }if(truncated)break;
 }
 if(!truncated)outer:for(let i=0;i<segments.length;i++)for(let j=i+1;j<segments.length;j++){
  const a=segments[i],b=segments[j];if(a.id===b.id)continue;
  if(a.h===b.h){if(a.c===b.c&&Math.min(a.hi,b.hi)>Math.max(a.lo,b.lo))add('route-overlap',a.id,b.id);}
  else{const h=a.h?a:b,v=a.h?b:a;if(v.c>h.lo&&v.c<h.hi&&h.c>v.lo&&h.c<v.hi)add('route-crossing',a.id,b.id);}
  if(findings.length>=maxFindings){truncated=true;break outer;}
 }
 return {findings,truncated,segments:segments.length};
}


// v22.8 — diagnostic rapide par balayage spatial ; budget explicite et déterministe.
// Le rapport conserve les identifiants de connexions et n'altère jamais les routes.
export function analyzeDenseRouteBundles(routes,{maxSegments=6000,maxPairs=250000,maxFindings=100}={}){
 if(!(routes instanceof Map)||![maxSegments,maxPairs,maxFindings].every(v=>Number.isInteger(v)&&v>0))throw Error('Invalid dense bundle limits');
 const segments=[],issues=[],seen=new Set();let invalid=0,segmentLimit=false,pairLimit=false,pairsChecked=0;
 for(const [id,route] of routes){
  const pts=route?.points;
  if(!Array.isArray(pts)||pts.length<2||pts.some(p=>!p||!Number.isFinite(p.x)||!Number.isFinite(p.y))){invalid++;continue;}
  let bad=false;
  for(let i=1;i<pts.length;i++){
   const a=pts[i-1],b=pts[i];if(a.x!==b.x&&a.y!==b.y){bad=true;continue;}
   if(a.x===b.x&&a.y===b.y)continue;
   if(segments.length===maxSegments){segmentLimit=true;break;}
   segments.push({id:String(id),h:a.y===b.y,c:a.y===b.y?a.y:a.x,lo:a.y===b.y?Math.min(a.x,b.x):Math.min(a.y,b.y),hi:a.y===b.y?Math.max(a.x,b.x):Math.max(a.y,b.y),minX:Math.min(a.x,b.x),maxX:Math.max(a.x,b.x),minY:Math.min(a.y,b.y),maxY:Math.max(a.y,b.y)});
  }
  if(bad)invalid++;
  if(segmentLimit)break;
 }
 // Interval sweep: only overlapping x ranges need geometric comparison.
 const sorted=segments.sort((a,b)=>a.minX-b.minX||a.maxX-b.maxX||a.id.localeCompare(b.id));
 const active=[];
 outer:for(const b of sorted){
  for(let k=active.length-1;k>=0;k--)if(active[k].maxX<b.minX)active.splice(k,1);
  for(const a of active){
   if(a.id===b.id||a.maxY<b.minY||b.maxY<a.minY)continue;
   if(pairsChecked>=maxPairs){pairLimit=true;break outer;}
   pairsChecked++;
   let code=null;
   if(a.h===b.h){if(a.c===b.c&&Math.min(a.hi,b.hi)>Math.max(a.lo,b.lo))code='route-overlap';}
   else{const h=a.h?a:b,v=a.h?b:a;if(v.c>h.lo&&v.c<h.hi&&h.c>v.lo&&h.c<v.hi)code='route-crossing';}
   if(code){const ids=[a.id,b.id].sort(),key=code+':'+ids.join(':');if(!seen.has(key)){seen.add(key);if(issues.length<maxFindings)issues.push({code,edgeId:ids[0],otherEdgeId:ids[1]});}}
  }
  active.push(b);
 }
 return {routes:routes.size,segments:segments.length,invalidRoutes:invalid,pairsChecked,issues,findingsLimited:seen.size>maxFindings,segmentLimit,pairLimit,complete:!segmentLimit&&!pairLimit};
}

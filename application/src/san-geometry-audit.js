/** Contrôle géométrique SAN, sans dépendance DOM. Auteur : Abdelhalim Talbi. */
const EPS=1e-7;
export function rectangleOf(node){
  const x=Number(node.x),y=Number(node.y),w=Number(node.w),h=Number(node.h);
  if(![x,y,w,h].every(Number.isFinite)||w<=0||h<=0) throw new TypeError('Rectangle invalide');
  return {left:x,right:x+w,top:y,bottom:y+h};
}
export function segmentIntersectsInterior(a,b,rect){
  // Liang-Barsky sur rectangle réduit : contact sur le bord autorisé.
  const r={left:rect.left+EPS,right:rect.right-EPS,top:rect.top+EPS,bottom:rect.bottom-EPS};
  if(r.left>=r.right||r.top>=r.bottom)return false;
  let lo=0,hi=1;const dx=b.x-a.x,dy=b.y-a.y;
  for(const [p,q] of [[-dx,a.x-r.left],[dx,r.right-a.x],[-dy,a.y-r.top],[dy,r.bottom-a.y]]){
    if(Math.abs(p)<EPS){if(q<0)return false;continue;}
    const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);
    if(lo>hi)return false;
  }
  return hi>=lo;
}
export function auditSanRoutes(nodes,edges,routes,{tolerance=2}={}){
  const lookup=new Map(nodes.map(n=>[n.id,n]));const findings=[];let checked=0;
  for(const edge of edges){
    const from=lookup.get(edge.from),to=lookup.get(edge.to),points=routes[edge.id];
    if(!from||!to){findings.push({edge:edge.id,kind:'missing-endpoint'});continue;}
    if(!Array.isArray(points)||points.length<2||points.some(p=>!p||![p.x,p.y].every(Number.isFinite))){findings.push({edge:edge.id,kind:'invalid-route'});continue;}
    checked++;
    const touches=(p,r)=>p.x>=r.left-tolerance&&p.x<=r.right+tolerance&&p.y>=r.top-tolerance&&p.y<=r.bottom+tolerance;
    if(!touches(points[0],rectangleOf(from)))findings.push({edge:edge.id,kind:'detached-source'});
    if(!touches(points.at(-1),rectangleOf(to)))findings.push({edge:edge.id,kind:'detached-target'});
    for(let i=1;i<points.length;i++){
      const a=points[i-1],b=points[i];
      if(Math.abs(a.x-b.x)>EPS&&Math.abs(a.y-b.y)>EPS)findings.push({edge:edge.id,kind:'non-orthogonal',segment:i-1});
      for(const node of nodes){if(node.id===edge.from||node.id===edge.to)continue;
        if(segmentIntersectsInterior(a,b,rectangleOf(node)))findings.push({edge:edge.id,kind:'node-collision',node:node.id,segment:i-1});
      }
    }
  }
  return {pass:findings.length===0,checked,findings};
}

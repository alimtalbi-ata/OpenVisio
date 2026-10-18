// OpenVisio v41.39 — independent final-route clearance diagnostics.
// Auteur : Abdelhalim Talbi
import {intersectsObstacle} from './routing.js';
export function inspectRouteClearance(points, obstacles = []) {
 if(!Array.isArray(points)||points.length<2||!Array.isArray(obstacles))throw Error('Invalid clearance input');
 const issues=[];
 for(let i=1;i<points.length;i++){
  const a=points[i-1],b=points[i];
  if(!a||!b||![a.x,a.y,b.x,b.y].every(Number.isFinite)){
   issues.push({segment:i-1,type:'invalid-coordinate'});continue;
  }
  if(a.x!==b.x&&a.y!==b.y)issues.push({segment:i-1,type:'non-orthogonal'});
  for(let j=0;j<obstacles.length;j++){
   const o=obstacles[j];
   if(!o||![o.x,o.y,o.w,o.h].every(Number.isFinite)||o.w<=0||o.h<=0){issues.push({segment:i-1,type:'invalid-obstacle',obstacle:j});continue;}
   if(intersectsObstacle(a,b,o))issues.push({segment:i-1,type:'obstacle-intersection',obstacle:j});
  }
 }
 return {valid:issues.length===0,issues,segments:points.length-1};
}

// v41.41: classify physical-port lead-in geometry separately from routed-core defects.
// Preserve original issue records for callers that depend on inspectRouteClearance.
export function classifyRouteClearance(points, obstacles=[], {physicalStart=false,physicalEnd=false}={}) {
 const result=inspectRouteClearance(points,obstacles);
 const last=points.length-2;
 const issues=result.issues.map(issue=>{
   const portLead=(physicalStart&&issue.segment===0)||(physicalEnd&&issue.segment===last);
   return {...issue, severity:portLead?'review':'error', scope:portLead?'physical-port-lead':'routed-core'};
 });
 return {valid:issues.every(i=>i.severity!=='error'),strictValid:result.valid,issues,segments:result.segments,errors:issues.filter(i=>i.severity==='error').length,reviews:issues.filter(i=>i.severity==='review').length};
}

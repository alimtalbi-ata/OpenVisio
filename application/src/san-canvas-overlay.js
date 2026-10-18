// OpenVisio v28.1 — visualisation SAN déclarative. Auteur : Abdelhalim Talbi.
import {analyzeSanRecommendations} from './san-recommendations.js';
import {buildSanVisualPlan} from './san-visual-plan.js';
export function buildCanvasSanOverlay(corrections, diagram){
 const report=analyzeSanRecommendations(corrections), plan=buildSanVisualPlan(report);
 const objects=Array.isArray(diagram?.objects)?diagram.objects:[];
 const connections=Array.isArray(diagram?.connections)?diagram.connections:[];
 const ids=new Set(objects.map(o=>String(o.id)));
 const marks=[], warnings=[];
 for(const group of plan.groups)for(const node of group.nodes){
  const correction=corrections.find(c=>String(c.id)===node.id);
  const targets=[...(Array.isArray(correction?.affectedObjectIds)?correction.affectedObjectIds:[])].map(String);
  if(!targets.length)warnings.push(`Aucune correspondance objet déclarée pour ${node.id}`);
  for(const id of targets){if(!ids.has(id)){warnings.push(`Objet introuvable : ${id}`);continue;}
   marks.push({objectId:id,correctionId:node.id,groupId:group.id,state:node.after,fabric:node.fabric});}
 }
 const marked=new Set(marks.map(m=>m.objectId));
 const links=connections.filter(c=>marked.has(String(c.sourceId??c.from??c.source))||marked.has(String(c.targetId??c.to??c.target))).map(c=>String(c.id??''));
 return {readOnly:true,marks,connectionIds:[...new Set(links)],connectionMarks:connections.filter(c=>links.includes(String(c.id??''))).map(c=>({connectionId:String(c.id??''),fabric:String(c.fabric??'UNKNOWN').toUpperCase()})),warnings,summary:report.summary};
}
export function renderCanvasSanOverlay(svg,overlay){
 if(!svg||typeof svg.querySelectorAll!=='function')throw new Error('Canvas SVG requis');
 svg.querySelectorAll('[data-san-overlay]').forEach(el=>el.remove());
 const namespace='http://www.w3.org/2000/svg';const layer=svg.ownerDocument.createElementNS(namespace,'g');layer.setAttribute('data-san-overlay','true');layer.setAttribute('pointer-events','none');
 const nodes=[...svg.querySelectorAll('[data-id]')];
 for(const mark of overlay.marks){const node=nodes.find(n=>n.getAttribute('data-id')===mark.objectId);if(!node||typeof node.getBBox!=='function')continue;
  let box;try{box=node.getBBox()}catch{continue}if(!box||!Number.isFinite(box.x+box.y+box.width+box.height))continue;
  const rect=svg.ownerDocument.createElementNS(namespace,'rect');rect.setAttribute('x',box.x-4);rect.setAttribute('y',box.y-4);rect.setAttribute('width',Math.max(1,box.width+8));rect.setAttribute('height',Math.max(1,box.height+8));rect.setAttribute('rx','6');rect.setAttribute('fill','none');rect.setAttribute('stroke',mark.state==='anomaly'?'#d62828':'#168a57');rect.setAttribute('stroke-width','3');rect.setAttribute('stroke-dasharray',mark.state==='proposed'?'7 4':'');layer.append(rect);
 }for(const link of (overlay.connectionMarks??[])){if(!link.connectionId)continue;const el=[...svg.querySelectorAll('[data-connection-id]')].find(e=>e.getAttribute('data-connection-id')===link.connectionId);if(!el)continue;const clone=el.cloneNode(true);clone.removeAttribute('id');clone.setAttribute('data-san-overlay','true');clone.setAttribute('pointer-events','none');clone.setAttribute('fill','none');clone.setAttribute('stroke',link.fabric==='A'?'#2563eb':link.fabric==='B'?'#c026d3':'#d97706');clone.setAttribute('stroke-width','4');clone.setAttribute('stroke-dasharray','8 4');layer.append(clone)}svg.append(layer);return layer.childElementCount;
}

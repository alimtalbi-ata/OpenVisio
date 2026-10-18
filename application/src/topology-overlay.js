// OpenVisio v13.6 — auteur Abdelhalim Talbi. Visualisation SVG non destructive.
import {diffTopologies,validateTopology} from './topology-diff.js';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=(v,fallback=0)=>Number.isFinite(Number(v))?Number(v):fallback;
export function overlayModel(before,after){
 validateTopology(before);validateTopology(after);const changes=diffTopologies(before,after),status=new Map(changes.map(c=>[c.kind+':'+c.id,c.status]));
 const nodes=[];for(const [doc,source] of [[before,'before'],[after,'after']])for(const n of doc.nodes){const s=status.get('nodes:'+n.id)||'unchanged';if((source==='before'&&s!=='removed'&&s!=='changed')||(source==='after'&&s==='removed'))continue;nodes.push({id:n.id,title:String(n.title||n.id),source,status:s,x:num(n.x),y:num(n.y),w:Math.max(30,num(n.w,110)),h:Math.max(20,num(n.h,55))});}
 const edges=[];for(const [doc,source] of [[before,'before'],[after,'after']]){const map=new Map(doc.nodes.map(n=>[n.id,n]));for(const e of doc.edges){const s=status.get('edges:'+e.id)||'unchanged';if((source==='before'&&s!=='removed'&&s!=='changed')||(source==='after'&&s==='removed'))continue;const a=map.get(e.from),b=map.get(e.to);edges.push({id:e.id,source,status:s,x1:num(a.x)+num(a.w,110)/2,y1:num(a.y)+num(a.h,55)/2,x2:num(b.x)+num(b.w,110)/2,y2:num(b.y)+num(b.h,55)/2});}}
 return {nodes,edges,changes};
}
export function overlaySvg(model,{filter='all',focus=null}={}){
 const allowed=new Set(['all','added','removed','changed','unchanged']);if(!allowed.has(filter))throw Error('Filtre inconnu');
 const nodes=model.nodes.filter(n=>(filter==='all'||n.status===filter)&&(!focus||n.id===focus));const edges=model.edges.filter(e=>(filter==='all'||e.status===filter)&&!focus);
 const all=[...nodes.flatMap(n=>[{x:n.x,y:n.y},{x:n.x+n.w,y:n.y+n.h}]),...edges.flatMap(e=>[{x:e.x1,y:e.y1},{x:e.x2,y:e.y2}])];const minX=Math.min(0,...all.map(p=>p.x))-30,minY=Math.min(0,...all.map(p=>p.y))-30,maxX=Math.max(640,...all.map(p=>p.x))+30,maxY=Math.max(360,...all.map(p=>p.y))+30;
 const colors={added:'#187a4b',removed:'#ba3040',changed:'#b77b00',unchanged:'#60768c'};
 const lines=edges.map(e=>`<line x1="${e.x1}" y1="${e.y1}" x2="${e.x2}" y2="${e.y2}" stroke="${colors[e.status]}" stroke-width="3" ${e.source==='before'?'stroke-dasharray="8 5"':''}><title>${esc(e.id)} — ${esc(e.status)}</title></line>`).join('');
 const boxes=nodes.map(n=>`<g data-node-id="${esc(n.id)}"><rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="7" fill="${n.source==='before'?'#fff7f7':'#f7fbff'}" stroke="${colors[n.status]}" stroke-width="3" ${n.source==='before'?'stroke-dasharray="7 4"':''}/><text x="${n.x+8}" y="${n.y+Math.min(22,n.h/2)}" fill="#18283d" font-size="13">${esc(n.title.slice(0,28))}</text><title>${esc(n.id)} — ${esc(n.status)} (${esc(n.source)})</title></g>`).join('');
 return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Superposition des topologies" viewBox="${minX} ${minY} ${maxX-minX} ${maxY-minY}" style="width:100%;height:auto;min-height:220px;max-height:440px;background:#f4f7fb;border:1px solid #ccd5df;border-radius:8px">${lines}${boxes}</svg>`;
}

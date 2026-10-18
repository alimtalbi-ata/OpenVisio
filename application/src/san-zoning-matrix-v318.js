// OpenVisio v31.8 — matrice des écarts par Fabric/VSAN/switch/zone. Auteur : Abdelhalim Talbi.
import {summarizeZoningEvidence} from './san-zoning-drift-v317.js';
const clean=x=>String(x??'').trim();
export function buildZoningMatrix(imported){
 const report=summarizeZoningEvidence(imported);
 const entries=report.findings.map(f=>{
  const records=[...f.active,...f.configured,...f.unknown];
  const switches=[...new Set(records.map(z=>clean(z.switch||z.switchName||z.sourceSwitch)).filter(Boolean))].sort();
  const fabrics=[...new Set(records.map(z=>clean(z.fabric||z.fabricName)).filter(Boolean))].sort();
  const priority=f.status==='MEMBERS_DIFFER'?'P2':f.status==='UNVERIFIED'?'P3':'P4';
  return {fabric:fabrics.join('; ')||'Non documentée',vsan:f.vsan,switch:switches.join('; ')||'Non documenté',zone:f.name,status:f.status,priority,missing:[...f.missing],extra:[...f.extra],recommendation:f.recommendation,sourceLines:[...new Set(records.map(z=>z.line).filter(x=>Number.isInteger(x)))].sort((a,b)=>a-b)};
 });
 const rank={P1:0,P2:1,P3:2,P4:3};entries.sort((a,b)=>rank[a.priority]-rank[b.priority]||a.fabric.localeCompare(b.fabric)||a.vsan.localeCompare(b.vsan)||a.switch.localeCompare(b.switch)||a.zone.localeCompare(b.zone));
 return {entries,counts:{total:entries.length,different:entries.filter(e=>e.status==='MEMBERS_DIFFER').length,unverified:entries.filter(e=>e.status==='UNVERIFIED').length,matched:entries.filter(e=>e.status==='MATCHED').length},limitations:report.limitations};
}
export function filterZoningMatrix(entries,priority='ALL'){return (Array.isArray(entries)?entries:[]).filter(e=>priority==='ALL'||e.priority===priority);}
export function zoningMatrixCsv(report){const cell=x=>{const s=String(x??'');return '"'+(/^[\s]*[=+@\-]/.test(s)?"'"+s:s).replaceAll('"','""')+'"';};return [['priority','fabric','vsan','switch','zone','status','missing','extra','source_lines','recommendation'],...(report?.entries??[]).map(e=>[e.priority,e.fabric,e.vsan,e.switch,e.zone,e.status,e.missing.join(';'),e.extra.join(';'),e.sourceLines.join(';'),e.recommendation])].map(r=>r.map(cell).join(',')).join('\r\n');}

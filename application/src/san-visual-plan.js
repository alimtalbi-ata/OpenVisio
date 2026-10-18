// OpenVisio v28.0 — projection visuelle déclarative, auteur Abdelhalim Talbi.
export function buildSanVisualPlan(report){
 if(!report||!Array.isArray(report.recommendations)||!Array.isArray(report.issues))throw new Error('Rapport SAN invalide');
 const unsafe=new Set();for(const issue of report.issues){if(issue.id)unsafe.add(issue.id);if(issue.relatedId)unsafe.add(issue.relatedId);for(const id of issue.relatedIds||[])unsafe.add(id)}
 const groups=new Map();for(const r of report.recommendations){const id=String(r.groupId||'sans-groupe');if(!groups.has(id))groups.set(id,{id,nodes:[],before:0,after:0});const g=groups.get(id);const affected=unsafe.has(r.id)||r.status==='blocked'||r.status==='dependency-cycle';const eligible=r.selected&&!affected&&r.status==='selected';g.nodes.push({id:r.id,title:r.title,fabric:r.fabric||'?',status:r.status,before:affected?'anomaly':'review',after:eligible?'proposed':affected?'anomaly':'unchanged',eligible,estimatedGain:eligible&&Number.isFinite(r.gain)&&r.gain>0?r.gain:0});if(affected)g.before++;if(affected&&!eligible)g.after++}
 return {readOnly:true,groups:[...groups.values()].sort((a,b)=>a.id.localeCompare(b.id)),warning:'Simulation déclarative uniquement : aucun état réel des équipements n’est mesuré.'};
}

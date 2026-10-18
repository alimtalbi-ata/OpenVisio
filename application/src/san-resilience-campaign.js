// OpenVisio v14.9 — campagnes documentaires de résilience. Auteur : Abdelhalim Talbi.
import {failureTargets,simulateMultipleSanFailures} from './san-failure-simulator.js';
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const csv=x=>{let s=String(x??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
export function runResilienceCampaign(doc,scenarios){
 if(!Array.isArray(scenarios)||scenarios.length<1||scenarios.length>100)throw new Error('Entre 1 et 100 scénarios requis');
 const known=new Set(failureTargets(doc).map(t=>JSON.stringify([t.kind,t.id])));
 const ids=new Set();const results=[];
 for(const [i,s] of scenarios.entries()){
  const id=String(s?.id??'').trim();if(!id||id.length>80||ids.has(id))throw new Error('Identifiant de scénario invalide ou dupliqué');ids.add(id);
  if(!Array.isArray(s.failures)||!s.failures.length)throw new Error('Scénario sans panne : '+id);
  for(const f of s.failures)if(!known.has(JSON.stringify([f?.kind,f?.id])))throw new Error('Cible inconnue : '+id);
  const result=simulateMultipleSanFailures(doc,s.failures);
  results.push({id,name:String(s.name??id).slice(0,120),failures:result.targets,summary:result.summary,rows:result.rows,applications:result.applications,index:i});
 }
 results.sort((a,b)=>b.summary.loss-a.summary.loss||b.summary.degraded-a.summary.degraded||b.summary.applications-a.summary.applications||a.index-b.index);
 const equipment=new Map();for(const r of results)for(const f of r.failures){const key=JSON.stringify([f.kind,f.id]);const e=equipment.get(key)||{kind:f.kind,id:f.id,scenarios:0,loss:0,degraded:0,applications:0};e.scenarios++;e.loss+=r.summary.loss;e.degraded+=r.summary.degraded;e.applications+=r.summary.applications;equipment.set(key,e);}
 const critical=[...equipment.values()].sort((a,b)=>b.loss-a.loss||b.degraded-a.degraded||b.applications-a.applications||a.kind.localeCompare(b.kind)||a.id.localeCompare(b.id));
 return {results,critical,scope:'Simulation documentaire : corrélation indicative, sans découverte ni action sur les équipements. Les cumuls par cible ne démontrent pas une causalité isolée.'};
}
export function campaignCsv(c){return [['Scénario','Pannes','Paires','Pertes','Dégradations','Applications'],...c.results.map(r=>[r.name,r.failures.map(f=>f.kind+':'+f.id).join(' | '),r.summary.pairs,r.summary.loss,r.summary.degraded,r.summary.applications])].map(row=>row.map(csv).join(',')).join('\r\n')+'\r\n';}
export function campaignHtml(c){return '<!doctype html><html lang="fr"><meta charset="utf-8"><title>Campagne de résilience SAN</title><style>body{font:14px system-ui;margin:2rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:8px}th{background:#e8f1fa}</style><h1>Campagne de résilience SAN</h1><p>Auteur : Abdelhalim Talbi</p><p>'+esc(c.scope)+'</p><h2>Classement des scénarios</h2><table><tr><th>Scénario</th><th>Défaillances</th><th>Pertes</th><th>Dégradations</th><th>Applications</th></tr>'+c.results.map(r=>'<tr>'+[r.name,r.failures.map(f=>f.kind+':'+f.id).join(' | '),r.summary.loss,r.summary.degraded,r.summary.applications].map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</table><h2>Fréquence des cibles dans les scénarios</h2><p>Les cumuls ne constituent pas un classement causal des équipements.</p><table><tr><th>Cible</th><th>Scénarios</th><th>Pertes cumulées</th></tr>'+c.critical.map(r=>'<tr>'+[r.kind+':'+r.id,r.scenarios,r.loss].map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</table></html>';}

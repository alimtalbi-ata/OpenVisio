// OpenVisio v29.4 — priorisation conservative des risques SPOF. Auteur : Abdelhalim Talbi.
import {analyzeSanSpof} from './san-spof.js';
const integer=x=>Number.isSafeInteger(x)&&x>=0?x:0;
export function classifySpofRisk(entry){
 const loss=integer(entry?.loss),degraded=integer(entry?.degraded),apps=integer(entry?.applications);
 if(loss>0)return {level:apps>0||loss>=3?'P1':'P2',reason:`${loss} paire(s) serveur/stockage perdue(s) dans le modèle`};
 if(degraded>0)return {level:'P3',reason:`${degraded} paire(s) dégradée(s) dans le modèle`};
 return {level:'P4',reason:'Aucune perte ou dégradation démontrée dans le modèle'};
}
export function buildSpofRiskMatrix(doc,options={}){
 const analysis=analyzeSanSpof(doc,options);
 const rows=analysis.results.map(r=>{const risk=classifySpofRisk(r);return {kind:r.kind,id:r.id,label:r.label,loss:integer(r.loss),degraded:integer(r.degraded),applications:integer(r.applications),priority:risk.level,reason:risk.reason,recommendation:r.kind==='fabric'?'Vérifier deux fabrics indépendantes, zoning, masking et multipathing':r.kind==='edge'?'Étudier un chemin FC indépendant et contrôler le câblage et les ports':'Vérifier les dépendances communes et la redondance du composant',affected:r.rows||[]};});
 const order={P1:0,P2:1,P3:2,P4:3};rows.sort((a,b)=>order[a.priority]-order[b.priority]||b.loss-a.loss||b.degraded-a.degraded||a.kind.localeCompare(b.kind)||a.id.localeCompare(b.id));
 return {rows,summary:Object.fromEntries(['P1','P2','P3','P4'].map(p=>[p,rows.filter(r=>r.priority===p).length])),scope:'Classification indicative des impacts modélisés, non une priorité ITIL opérationnelle. Validation humaine obligatoire.'};
}
export function spofRiskCsv(report){const q=v=>{let s=String(v??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"'};return [['Priorité','Type','ID','Nom','Pertes','Dégradations','Applications','Motif','Recommandation'],...report.rows.map(r=>[r.priority,r.kind,r.id,r.label,r.loss,r.degraded,r.applications,r.reason,r.recommendation])].map(r=>r.map(q).join(',')).join('\r\n')+'\r\n'};

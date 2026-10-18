import {validateSanHistory} from './san-cockpit.js';
import {compareSanImports} from './zoneset-document.js';
import {complianceTimeline} from './san-compliance-report.js';

export function visualAuditModel(history,{fabric='ALL',severity='all',left=null,right=null,maxAgeDays=30,requireBothFabrics=true}={}){
 const entries=validateSanHistory(history);
 const selected=entries.filter(e=>fabric==='ALL'||e.data.fabric===fabric);
 const a=selected.find(e=>e.id===left)??selected.at(-2);
 const b=selected.find(e=>e.id===right)??selected.at(-1);
 const changes=a&&b?compareSanImports(a.data,b.data):[];
 const severityFor=c=>c.status==='removed'?'error':c.status==='added'?'warning':c.status==='modified'?'warning':'info';
 const filtered=changes.filter(c=>severity==='all'||severityFor(c)===severity);
 const timeline=complianceTimeline(entries,{maxAgeDays,requireBothFabrics});
 return {entries:selected.map(e=>({id:e.id,at:e.at,label:e.label,fabric:e.data.fabric,vendor:e.data.vendor})),left:a?.id??null,right:b?.id??null,changes:filtered.map(c=>({...c,severity:severityFor(c)})),timeline};
}
export function sparklinePoints(values,width=600,height=100){
 if(!values.length)return '';
 return values.map((v,i)=>`${values.length===1?width/2:i*width/(values.length-1)},${height-(Math.max(0,Math.min(100,Number(v)||0))*height/100)}`).join(' ');
}

export function comparisonHtmlReport(history,options={}){
 const model=visualAuditModel(history,options);
 const escape=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
 const counts={error:0,warning:0,info:0};
 for(const c of model.changes)counts[c.severity]++;
 const rows=model.changes.map(c=>`<tr class="${escape(c.severity)}"><td>${escape(c.key)}</td><td>${escape(c.status)}</td><td>${escape(c.severity)}</td></tr>`).join('');
 const entry=id=>model.entries.find(e=>e.id===id);
 const left=entry(model.left),right=entry(model.right);
 return `<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>OpenVisio — Comparaison SAN</title><style>body{font:15px system-ui,sans-serif;margin:2rem;color:#182c42}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd7e3;padding:8px;text-align:left}.error{background:#ffe4e4}.warning{background:#fff3d6}.info{background:#e9f2fc}@media print{body{margin:1cm}}</style></head><body><h1>Comparaison des configurations SAN</h1><p>Auteur : Abdelhalim Talbi</p><p>Fabric : ${escape(options.fabric??'ALL')} · Criticité : ${escape(options.severity??'all')}</p><p>Version 1 : ${escape(left?.label??'Non disponible')} (${escape(left?.at??'')})</p><p>Version 2 : ${escape(right?.label??'Non disponible')} (${escape(right?.at??'')})</p><p>Écarts : ${model.changes.length} · Critiques : ${counts.error} · Avertissements : ${counts.warning}</p><table><thead><tr><th>Zone / zoneset</th><th>Changement</th><th>Criticité indicative</th></tr></thead><tbody>${rows}</tbody></table><p>Analyse déclarative hors ligne : aucune vérification du zoning actif sur les switches.</p></body></html>`;
}

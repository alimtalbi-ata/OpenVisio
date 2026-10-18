// OpenVisio v29.5 — SPOF intégré, lecture seule. Auteur : Abdelhalim Talbi.
import {buildSpofRiskMatrix,spofRiskCsv} from './san-spof-priority.js';
export function filterRiskRows(report,priority='ALL') {return (report?.rows||[]).filter(r=>priority==='ALL'||r.priority===priority);}
export function summarizeRiskRows(rows){return Object.fromEntries(['P1','P2','P3','P4'].map(p=>[p,rows.filter(r=>r.priority===p).length]));}
const byId=id=>document.getElementById(id);
let snapshot=null,report=null;
const marked=new Map();
export function clearSpofHighlight(){for(const [element,previous] of marked){if(!element.isConnected)continue;if(previous===null)element.removeAttribute('style');else element.setAttribute('style',previous);}marked.clear();}
export function spofSelectors(row){const id=String(row?.id??'');if(!id||!['node','edge','fabric'].includes(String(row?.kind)))return [];const attr=row.kind==='edge'?'data-connection-id':'data-object-id';if(row.kind==='fabric')return [];return [{attr,id}];}
export function highlightSpofTarget(doc,row){clearSpofHighlight();const svg=doc.querySelector('svg');if(!svg)return 0;let count=0;for(const {attr,id} of spofSelectors(row)){for(const el of svg.querySelectorAll('['+attr+']')){if(el.getAttribute(attr)!==id)continue;marked.set(el,el.getAttribute('style'));el.style.setProperty('filter','drop-shadow(0 0 5px #f59e0b)');el.style.setProperty('outline','3px solid #f59e0b');el.scrollIntoView?.({block:'nearest',inline:'nearest'});count++;}}return count;}

function render(){const tbody=byId('sanSpofRows');if(!tbody)return;tbody.replaceChildren();if(!report)return;const rows=filterRiskRows(report,byId('sanSpofFilter').value);byId('sanSpofSummary').textContent=`${rows.length} cibles affichées · `+Object.entries(summarizeRiskRows(rows)).map(([k,v])=>`${k}: ${v}`).join(' · ');for(const r of rows){const tr=document.createElement('tr');for(const value of [r.priority,r.kind,r.label,r.loss,r.degraded,r.reason,r.recommendation]){const td=document.createElement('td');td.textContent=String(value??'');td.style.padding='4px';tr.append(td)}const td=document.createElement('td'),b=document.createElement('button');b.type='button';b.textContent='Localiser';b.addEventListener('click',()=>{const count=highlightSpofTarget(document,r);document.dispatchEvent(new CustomEvent('openvisio:san-select',{detail:{kind:r.kind,id:r.id}}));byId('sanSpofStatus').textContent=count?`Cible ${r.kind}:${r.id} surlignée (${count} élément(s)).`:`Cible ${r.kind}:${r.id} non trouvée sur le canvas ; navigation événementielle demandée.`});td.append(b);tr.append(td);tbody.append(tr)}}
if(typeof document!=='undefined'&&byId('sanSpofPanel')){
 document.addEventListener('openvisio:san-snapshot',e=>{snapshot=e.detail;report=null;clearSpofHighlight();byId('sanSpofStatus').textContent='Document actualisé : relancer l’analyse SPOF.';render()});
 document.addEventListener('openvisio:canvas-painted',()=>{report=null;clearSpofHighlight();byId('sanSpofStatus').textContent='Canvas modifié : analyse invalidée.';render()});
 byId('sanSpofAnalyze').addEventListener('click',()=>{try{if(!snapshot){document.dispatchEvent(new Event('openvisio:san-snapshot-request'));if(!snapshot)throw Error('Document actif indisponible');}report=buildSpofRiskMatrix(snapshot);byId('sanSpofStatus').textContent=`${report.rows.length} cibles analysées (simulation documentaire).`;render()}catch(e){report=null;byId('sanSpofStatus').textContent='Analyse impossible : '+e.message;render()}});
 byId('sanSpofFilter').addEventListener('change',render);
 byId('sanSpofExport').addEventListener('click',()=>{if(!report)return;const blob=new Blob([spofRiskCsv({...report,rows:filterRiskRows(report,byId('sanSpofFilter').value)})],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='openvisio-v29.6-spof.csv';a.click();URL.revokeObjectURL(url)});
 document.dispatchEvent(new Event('openvisio:san-snapshot-request'));
}

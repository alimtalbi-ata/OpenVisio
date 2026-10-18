// OpenVisio v29.8 — panneau de dépendances SAN. Auteur : Abdelhalim Talbi.
import {analyzeSharedTransit} from './san-spof-v298.js';
let snapshot=null;
const get=id=>document.getElementById(id);
function status(s){get('sanSharedStatus').textContent=s;}
if(typeof document!=='undefined'&&get('sanSharedRun')){
 document.addEventListener('openvisio:san-snapshot',e=>{snapshot=e.detail;status('Document modifié : relancer l’analyse.');get('sanSharedRows').replaceChildren();});
 get('sanSharedRun').addEventListener('click',()=>{
  try{if(!snapshot)document.dispatchEvent(new Event('openvisio:san-snapshot-request'));if(!snapshot)throw Error('Document actif indisponible');
   const result=analyzeSharedTransit(snapshot);const body=get('sanSharedRows');body.replaceChildren();
   for(const r of result.findings){const tr=document.createElement('tr');for(const value of [r.serverId,r.storageId,r.componentId,r.classification,r.recommendation]){const td=document.createElement('td');td.textContent=value;tr.append(td);}const td=document.createElement('td');const btn=document.createElement('button');btn.type='button';btn.textContent='Localiser';btn.addEventListener('click',()=>document.dispatchEvent(new CustomEvent('openvisio:san-select',{detail:{id:r.componentId}})));td.append(btn);tr.append(td);body.append(tr);}
   status(`${result.findings.length} dépendance(s) commune(s) documentée(s).${result.truncated?' Exploration tronquée : résultat incomplet.':''}`);
  }catch(e){status('Analyse impossible : '+e.message);}
 });document.dispatchEvent(new Event('openvisio:san-snapshot-request'));
}

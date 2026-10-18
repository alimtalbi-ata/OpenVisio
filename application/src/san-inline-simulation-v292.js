// OpenVisio v29.2 — visualisation non destructive, Abdelhalim Talbi.
import {buildSanImpactReport,sanImpactCsv} from './san-impact-report.js';
const $=id=>document.getElementById(id);
let diagram=null, report=null;
let source="none";
const marked=new Set();
export function clearProjection(root=document){
  for(const g of root.querySelectorAll('[data-edge-id]')){
    if(!marked.has(g))continue;
    g.classList.remove('ov-san-lost','ov-san-kept');
  }
  marked.clear();
}
export function classifyEdges(report){
  return {lost:new Set((report?.visual?.lostEdgeIds||[]).map(String)),kept:new Set((report?.visual?.preservedEdgeIds||[]).map(String))};
}
function applyProjection(){
  clearProjection();
  const {lost,kept}=classifyEdges(report);
  let count=0;
  for(const g of document.querySelectorAll('#diagramCanvas [data-edge-id]')){
    const id=g.getAttribute('data-edge-id');
    if(lost.has(id)){g.classList.add('ov-san-lost');marked.add(g);count++}
    else if(kept.has(id)){g.classList.add('ov-san-kept');marked.add(g);count++}
  }
  return count;
}
if(typeof document!=='undefined' && $('sanSimFile')){
  const useActive=$('sanSimActive');
  function loadDiagram(data, origin){
    if(!Array.isArray(data?.nodes)||!Array.isArray(data?.edges))throw Error('nodes[] et edges[] requis');
    clearProjection();report=null;$('sanSimExport').disabled=true;
    diagram=data;source=origin;
    const select=$('sanSimFailure');select.querySelectorAll('option[data-equipment]').forEach(x=>x.remove());
    for(const n of data.nodes){if(n.id==null)continue;const o=document.createElement('option');o.value='node:'+String(n.id);o.dataset.equipment='1';o.textContent='Équipement : '+String(n.label??n.name??n.id);select.append(o)}
    $('sanSimStatus').textContent=`${data.nodes.length} équipements et ${data.edges.length} connexions · source : ${origin}.`;
  }
  document.addEventListener('openvisio:san-snapshot',e=>{if(useActive?.checked)try{loadDiagram(e.detail,'document actif')}catch(err){$('sanSimStatus').textContent=err.message}});
  function requestActive(){document.dispatchEvent(new Event('openvisio:san-snapshot-request'))}
  useActive?.addEventListener('change',()=>{if(useActive.checked)requestActive()});
  document.addEventListener('openvisio:canvas-painted',()=>{
    if(source==='document actif' && useActive?.checked){report=null;$('sanSimExport').disabled=true;$('sanSimStatus').textContent='Document modifié : relancer la simulation.';}
    if(report)applyProjection();
  });
  if(useActive?.checked)requestActive();
  const css=document.createElement('style');
  css.textContent='#diagramCanvas .ov-san-lost path,#diagramCanvas .ov-san-lost line,#diagramCanvas .ov-san-lost polyline{stroke:#dc2626!important;stroke-width:5!important}#diagramCanvas .ov-san-kept path,#diagramCanvas .ov-san-kept line,#diagramCanvas .ov-san-kept polyline{stroke:#16a34a!important;stroke-width:4!important}';
  document.head.append(css);
  $('sanSimFile').addEventListener('change',async e=>{
    clearProjection();report=null;$('sanSimExport').disabled=true;
    try{
      const file=e.target.files?.[0];if(!file)return;
      const data=JSON.parse(await file.text());
      if(useActive)useActive.checked=false;
      loadDiagram(data,'fichier JSON');
    }catch(err){diagram=null;$('sanSimStatus').textContent='Import refusé : '+err.message}
  });
  $('sanSimRun').addEventListener('click',()=>{
    if(!diagram){$('sanSimStatus').textContent='Charger le document actif ou un fichier JSON.';return}
    try{
      const value=$('sanSimFailure').value;const kind=value.slice(0,value.indexOf(':')),id=value.slice(value.indexOf(':')+1);
      report=buildSanImpactReport(diagram,kind==='fabric'?{failedFabric:id}:{failedNodeId:id});
      const matches=applyProjection(),s=report.summary;
      $('sanSimStatus').textContent=`Avant ${s.pathsBefore} · Après ${s.pathsAfter} · Perdus ${s.lostPaths} · Paires inaccessibles ${s.disconnectedPairs} · ${matches} liens correspondants dans le canvas.${report.truncated?' Exploration tronquée.':''}`;
      $('sanSimExport').disabled=false;
    }catch(err){clearProjection();report=null;$('sanSimExport').disabled=true;$('sanSimStatus').textContent='Erreur : '+err.message}
  });
  $('sanSimClear').addEventListener('click',()=>{clearProjection();$('sanSimStatus').textContent='Projection effacée.'});
  $('sanSimExport').addEventListener('click',()=>{
    if(!report)return;
    const url=URL.createObjectURL(new Blob([sanImpactCsv(report)],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download='openvisio-v29.3-impact-san.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
}

import {lastRouteClearanceDiagnostics,lastRouteSegmentGeometry} from "./renderer.js";
import {renderRouteClearancePanel} from "./route-clearance-view.js";
import { installPrimaryShortcuts } from "./primary-shortcuts-v395.js";
import {simulateSanFailure as simulateSanFailureV289} from './san-failure-simulation.js';
import {exploreSanPaths} from './san-path-explorer.js';
import {filterSanLines} from './san-inspector-filter.js';
import {inspectSanSelection} from './san-inline-inspector.js';
import {routeEdge} from './routing.js';
import {proposeSanAlternate,prepareAlternateCommit,commitAlternateRoute,verifyCommittedAlternate,qualifyAlternateLifecycle} from "./san-alternate-routes.js";
import {auditSanRoutes} from "./san-geometry-audit.js";
import {commonValue,selectionBounds,selectionKinds} from "./multi-inspector-model.js";
import {DOCUMENT_KEY,saveDocumentWithBackup,decodeDocument,recoverBackup} from "./unified-storage.js";
import {inspectRecovery} from "./recovery-diagnostics.js";
import {createRecoveryRecord,verifyRecoveryRecord} from "./recovery-integrity-v403.js";
import {exportPortableBackup,inspectPortableBackup,restorePortableBackup} from "./portable-backup.js";
import {commitZoningUpdate} from "./zoning-transaction.js";
import {planEdgeProperty,applyEdgeProperty} from "./edge-property-transaction.js";
import {planNodeProperty,applyNodeProperty} from './property-transaction.js';
import {detectCableCrossings,renderedCableRoutes} from './cable-crossings.js';
import {proposeRouteOffset,applyRouteOffset,previewRouteGeometry} from "./route-preview.js";
import {prepareRouteBatch,commitRouteBatch,batchFingerprint,optimizeRouteBatch,describeRouteBatchConflicts,auditExistingFabricClearance} from "./route-batch.js";
import {nextFindingIndex,edgeViewportTarget,fitConflictGroupZoom,summarizeSanConflictGroup} from './wiring-navigation.js';
import {installToolMenus} from "./tool-menus.js";
import {createFrameScheduler} from "./frame-scheduler.js";
import {createInteractionMetrics} from "./interaction-metrics.js";
import {transformNodes} from "./vector-transform.js";
import {normalizeGuides,snapToGuides,moveGuide,toggleGuideLock} from "./custom-guides.js";
import {resizeFromCorner,rulerTicks} from "./vector-resize.js";
import {uniformDimensions} from "./vector-sizing.js";
import {magneticSnap,alignToReference} from "./magnetic-guides.js";
import {reorderShapes} from "./z-order.js";
import {analyzeSanSpof,spofCsv,spofHtml} from "./san-spof.js";
import {runResilienceCampaign,campaignCsv,campaignHtml} from "./san-resilience-campaign.js";
import {failureTargets,simulateSanFailure,failureCsv,failureHtml,simulateMultipleSanFailures,multipleFailureCsv,multipleFailureHtml} from "./san-failure-simulator.js";
import {validateSanEndToEnd,sanEndToEndCsv,sanEndToEndHtml} from './san-end-to-end.js';
import {parseLunMasking} from "./lun-masking.js";
import {auditSanAccess,sanAccessCsv,sanAccessHtml} from './san-access-audit.js';
import {correlateSanZoning,zoningCorrelationCsv,zoningCorrelationHtml} from './san-zoning-correlation.js';
import {RELATION_FIELDS,validateRelationField,auditSanRelations,sanRelationsCsv,sanRelationsHtml} from "./san-relations.js";
import {parseSanProperty} from "./san-properties.js";
import {compareSanChains,sanChainsCsv,sanChainsHtml} from "./san-chain.js";
import {buildSanImpactMatrix,sanImpactMatrixCsv,sanImpactMatrixHtml} from "./san-impact-matrix.js";
import {compareFcPorts,applicationImpact,portImpactHtml} from "./san-port-impact.js";
import {compareSanConnectivity,sanImpactHtml} from "./san-impact-diff.js";
import {overlayModel,overlaySvg} from "./topology-overlay.js";
import {diffTopologies,diffSummary,topologyDiffHtml} from "./topology-diff.js";
import {visualAuditModel,sparklinePoints,comparisonHtmlReport} from './san-visual-audit.js';
import {complianceHtmlReport} from "./san-compliance-report.js";
import {compareFabricSnapshots,complianceCsv} from "./san-compliance.js";
import {appendSanSnapshot,validateSanHistory,cockpitSummary,cockpitCsv} from "./san-cockpit.js";
import {validateSanImport,compareSanImports,sanDiffCsv} from "./zoneset-document.js";
import {parseSanConfig,assignSanRoles,compareSanZones,auditSanZonesets} from "./san-config-import.js";
import {validateZones,exportDiagram,importZones} from "./zoning-document.js";
import {summarizeDiagnostics,filterDiagnostics,diagnosticLevel,diagnosticDescription,resolveDiagnosticEdge} from './wiring-diagnostics.js';
import {buildWiringReport,reportCsv,reportHtml} from "./wiring-report.js";
import {parsePorts,portChangeImpact,planPortRename,applyPortRename} from "./ports.js";
import {CATEGORIES,shapeKey,filterShapes,toggleFavorite,readFavorites,readRecentShapes,trackRecentShape} from "./library.js";
import {TEMPLATES,createTemplate} from "./templates.js";
import {moveSelectionRigid,duplicateSubgraph} from "./graph-operations.js";
import {arrangeNodes,planCollisionFreeGrid,applyGridPlan} from "./layout.js";
import {parseWaypoints,insertWaypoint,diagnoseRouteTopology,locateRouteAnomalies,analyzeDenseRouteBundles} from "./routing.js";
import {buildDenseTopologySummary} from "./dense-report.js";
// Auteur : Abdelhalim Talbi
import {SHAPES,DEFAULTS} from "./catalog.js";
import {makeNode,makeEdge,snapshot,restore,validateGraph} from "./model.js";
import {createHistory} from "./history-transaction.js";
import {renderGraph,lastRenderStatistics,renderDiagnosticSnapshot} from "./renderer.js";
import {renderInspector} from "./inspector.js";
import {groupNodes,ungroupNodes,createLayer,setLayer,visibleNode,editableNode} from "./organization.js";
const $=id=>document.getElementById(id);
let unifiedStorageReady=false;
let declaredZones=[];
let lastSanImport=null;
const svg=$("diagramCanvas"),state={nodes:[],edges:[],selected:null,tool:"select",zoom:1,groups:[],layers:[{id:"default",name:"Principal",visible:true,locked:false}],guides:[]};
const history=createHistory(60,{
 captureExtras:()=>({declaredZones:structuredClone(declaredZones),lastSanImport:structuredClone(lastSanImport)}),
 validateExtras:extras=>{validateZones(extras.declaredZones);validateSanImport(extras.lastSanImport);},
 restoreExtras:extras=>{
  const zones=validateZones(extras.declaredZones);
  const imported=validateSanImport(extras.lastSanImport);
  declaredZones=zones;lastSanImport=imported;persistZones();persistSanImport();
 }
});
const undoStack=history.undo,redoStack=history.redo;
let drag=null,waypointDrag=null,connectFrom=null,toastTimer,suppressNextClick=false;
const multi=new Set();
const graphHandlers={select,onPointerDown,onWaypointDown,addWaypoint,removeWaypoint,onNodeClick};
const GRID=10;
let snapEnabled=false;
let magneticEnabled=false;
let activeMagneticGuides=[];
let resizeDrag=null;
let rulersEnabled=true;
let guideDrag=null;let customGuidesEnabled=true;
const snap=v=>snapEnabled?Math.round(v/GRID)*GRID:v;
function selectedNodes(){return state.nodes.filter(n=>multi.has(n.id));}
function clearMulti(){multi.clear();}
function refreshMulti(){document.querySelectorAll(".node").forEach(g=>g.classList.toggle("selected",multi.has(g.dataset.id)));}
function updateSelectionLabel(){const count=multi.size;$("selectionLabel").textContent=count?` · ${count} forme(s) sélectionnée(s)`:" · aucune sélection";}
function notify(message){const t=$("toast");t.textContent=message;t.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove("show"),2100);}
function cancelGestureHistory(gesture){if(!gesture?.historySaved)return;history.cancelCheckpoint(gesture.previousRedo);syncHistoryButtons();}
function saveUndo(){history.checkpoint(state);syncHistoryButtons();}
function syncHistoryButtons(){$("undoBtn").disabled=!undoStack.length;$("redoBtn").disabled=!redoStack.length;}
function travelHistory(source,destination,message){if(!history.travel(state,source,destination))return;clearMulti();if(state.selected&&!state.nodes.some(n=>n.id===state.selected)&&!state.edges.some(e=>e.id===state.selected))state.selected=null;syncHistoryButtons();paint();notify(message);}
function persist(){if(!unifiedStorageReady)return;try{saveDocumentWithBackup(localStorage,DOCUMENT_KEY,snapshot(state),declaredZones,lastSanImport,{restoreGraph:restore,validateZones,validateSanImport});$("saveState").textContent="Enregistré localement";}catch{$("saveState").textContent="Session";}}
function updateSanInlinePanel(){
 const host=document.getElementById('sanInlineDetails');if(!host)return;
 const report=inspectSanSelection(state,state.selected);
 host.replaceChildren();
 const heading=document.createElement('strong');heading.textContent=report.title;host.append(heading);
 const toolbar=document.createElement('label');toolbar.textContent='Filtrer les chemins : ';
 const picker=document.createElement('select');picker.setAttribute('aria-label','Filtrer par Fabric');
 for(const [value,label] of [['all','Toutes'],['A','Fabric A'],['B','Fabric B'],['unknown','Non renseignée']]){const option=document.createElement('option');option.value=value;option.textContent=label;picker.append(option);}
 picker.value=window.openVisioSanFabricFilter||'all';toolbar.append(picker);host.append(toolbar);
 const linesHost=document.createElement('div');host.append(linesHost);
 const showLines=()=>{window.openVisioSanFabricFilter=picker.value;linesHost.replaceChildren();for(const line of filterSanLines(report.lines,picker.value)){const p=document.createElement('p');p.textContent=line;linesHost.append(p);}if(!linesHost.childNodes.length){const p=document.createElement('p');p.textContent='Aucune information pour ce filtre.';linesHost.append(p);}};
 picker.addEventListener('change',showLines);showLines();
 const pathSection=document.createElement('section');pathSection.setAttribute('aria-label','Chemins SAN de bout en bout');
 const pathTitle=document.createElement('h4');pathTitle.textContent='Chemins FC documentés — serveur vers baie';pathSection.append(pathTitle);
 const analysis=exploreSanPaths(state,{maxDepth:10,maxPaths:300});
 const selected=String(state.selected??'');
 const matches=analysis.paths.filter(p=>!selected||p.nodeIds.includes(selected)||p.edgeIds.includes(selected));
 const summary=document.createElement('p');summary.textContent=`${matches.length} chemin(s) associé(s) · ${analysis.resilience.length} paire(s) serveur/baie${analysis.truncated?' · Résultat tronqué':''}`;pathSection.append(summary);
 for(const path of matches.slice(0,30)){
  const line=document.createElement('div');line.style.cssText='padding:6px;margin:4px 0;border-left:4px solid '+(path.fabrics.length===1&&path.fabrics[0]==='A'?'#2074bf':path.fabrics.length===1&&path.fabrics[0]==='B'?'#8151a6':'#ba831b');
  const title=document.createElement('span');title.textContent=`${path.serverId} → ${path.storageId} · Fabric ${path.fabrics.join('/')} ${path.issues.length?'⚠ '+path.issues.join(', '):'✓'}`;line.append(title);
  for(const id of path.nodeIds){const btn=document.createElement('button');btn.type='button';btn.textContent=id;btn.title='Sélectionner '+id;btn.addEventListener('click',()=>select(id));line.append(btn);}
  pathSection.append(line);
 }
 if(matches.length>30){const more=document.createElement('p');more.textContent='Affichage limité à 30 chemins ; affiner la sélection.';pathSection.append(more);}
 const simulation=document.createElement('div');simulation.setAttribute('aria-label','Simulation de panne SAN');
 const simTitle=document.createElement('h4');simTitle.textContent='Simulation de perte SAN (lecture seule)';simulation.append(simTitle);
 const simPicker=document.createElement('select');simPicker.setAttribute('aria-label','Défaillance simulée');
 for(const [value,label] of [['','Choisir une défaillance'],['FABRIC:A','Perte Fabric A'],['FABRIC:B','Perte Fabric B'],...state.nodes.filter(n=>/switch/i.test(String(n.type))).map(n=>['NODE:'+n.id,'Perte switch '+n.id])]){const opt=document.createElement('option');opt.value=value;opt.textContent=label;simPicker.append(opt);}
 const simResult=document.createElement('p');simResult.setAttribute('aria-live','polite');
 simPicker.addEventListener('change',()=>{if(!simPicker.value){simResult.textContent='';return;}const [type,id]=simPicker.value.split(':');const r=simulateSanFailureV289(state,type==='NODE'?{failedNodeId:id}:{failedFabric:id});const lost=r.affected.filter(x=>x.lost>0);simResult.textContent=`${lost.length} paire(s) impactée(s), ${lost.filter(x=>x.unreachable).length} inaccessible(s) dans le modèle${r.truncated?' · résultats tronqués':''}. Simulation uniquement.`;});
 simulation.append(simPicker,simResult);pathSection.append(simulation);
 const disclaimer=document.createElement('small');disclaimer.textContent='Analyse documentaire uniquement : ni découverte réelle ni preuve de multipathing.';pathSection.append(disclaimer);
 host.append(pathSection);
 const related=document.createElement('div');
 for(const id of report.related){const b=document.createElement('button');b.type='button';b.textContent='Voir '+id;b.addEventListener('click',()=>select(id));related.append(b);}
 host.append(related);
}
function updateCounts(){updateSanInlinePanel();$("objectCount").textContent=`${state.nodes.length} objet${state.nodes.length!==1?"s":""} · ${state.edges.length} connexion${state.edges.length!==1?"s":""}`;$("emptyState").style.display=state.nodes.length?"none":"block";$("selectionLabel").textContent=state.selected?" · objet sélectionné":" · aucune sélection";}
// Le cache ne fige pas les positions : il conserve les references des objets mutables.
// Toute operation complete (paint) invalide le cache avant le rendu.
let interactiveGraphCache=null;
function visibleGraph(){const nodes=state.nodes.filter(n=>visibleNode(state,n));const ids=new Set(nodes.map(n=>n.id));return {...state,nodes,edges:state.edges.filter(e=>ids.has(e.from)&&ids.has(e.to))};}
function interactiveVisibleGraph(){return interactiveGraphCache??(interactiveGraphCache=visibleGraph());}
function invalidateInteractiveGraph(){interactiveGraphCache=null;}

const interactionMetrics=createInteractionMetrics();
const graphPhaseMetrics=createInteractionMetrics();
const overlayPhaseMetrics=createInteractionMetrics();
const fullPaintMetrics=createInteractionMetrics();
let lastDiagnosticExport=null;
export function buildRenderDiagnosticReport({interactive,graph,overlay,full,rendered,generatedAt}){
 if(!rendered||!interactive||!graph||!overlay||!full)throw new TypeError('Rapport de rendu incomplet');
 return {schema:'openvisio.render-diagnostic.v1',generatedAt,interactive,graph,overlay,full,rendered};
}
function currentRenderDiagnosticReport(){return buildRenderDiagnosticReport({interactive:interactionMetrics.snapshot(),graph:graphPhaseMetrics.snapshot(),overlay:overlayPhaseMetrics.snapshot(),full:fullPaintMetrics.snapshot(),rendered:renderDiagnosticSnapshot(svg),generatedAt:new Date().toISOString()});}

// Diagnostic interactif non intrusif : affichage à la demande, sans télémétrie externe.
function refreshRenderDiagnostics(){
 const output=$('renderDiagnosticsOutput');if(!output)return;
 const m=interactionMetrics.snapshot();
 const graph=graphPhaseMetrics.snapshot(),overlay=overlayPhaseMetrics.snapshot();
 const dom=lastRenderStatistics(svg);
 const report=currentRenderDiagnosticReport();
 const ratio=report.rendered.dom.mutationRatio;
 output.textContent=`${m.count} rendu(s) interactif(s) · total moyen ${m.meanMs.toFixed(2)} ms · P95 ${m.p95Ms.toFixed(2)} ms · max ${m.maxMs.toFixed(2)} ms · >16,67 ms : ${m.over16ms} · SVG moyen ${graph.meanMs.toFixed(2)} ms · habillage moyen ${overlay.meanMs.toFixed(2)} ms · DOM dernier rendu : ${dom.nodesReused} nœuds et ${dom.edgesReused} liens conservés, ${dom.nodesUpdated} nœuds et ${dom.edgesUpdated} liens reconstruits · mutations ${(ratio*100).toFixed(1)} % · routage ${report.rendered.routing.mode} · rendu complet moyen ${report.full.meanMs.toFixed(2)} ms`;
}
$('renderDiagnosticsToggle')?.addEventListener('click',()=>{
 const panel=$('renderDiagnosticsPanel');panel.hidden=!panel.hidden;
 $('renderDiagnosticsToggle').setAttribute('aria-expanded',String(!panel.hidden));
 if(!panel.hidden)refreshRenderDiagnostics();
});
$('renderDiagnosticsReset')?.addEventListener('click',()=>{interactionMetrics.reset();graphPhaseMetrics.reset();overlayPhaseMetrics.reset();fullPaintMetrics.reset();refreshRenderDiagnostics();});

$('renderDiagnosticsExport')?.addEventListener('click',()=>{
 const report=currentRenderDiagnosticReport();
 const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob);
 const a=document.createElement('a');a.href=url;a.download='OpenVisio-diagnostic-rendu-v24.2.json';a.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
});
const interactiveFrames=createFrameScheduler(()=>{const started=performance.now();renderGraph(svg,interactiveVisibleGraph(),graphHandlers);const afterGraph=performance.now();drawMagneticGuides();drawEditorOverlays();refreshMulti();const finished=performance.now();graphPhaseMetrics.record(afterGraph-started);overlayPhaseMetrics.record(finished-afterGraph);interactionMetrics.record(finished-started);if(!$('renderDiagnosticsPanel').hidden)refreshRenderDiagnostics();refreshRouteQualityPanel();});
document.addEventListener('openvisio:san-snapshot-request',()=>{document.dispatchEvent(new CustomEvent('openvisio:san-snapshot',{detail:{nodes:structuredClone(state.nodes),edges:structuredClone(state.edges)}}));});
// Transient diagnostic highlight: remove any previous mark before highlighting a new edge.
function highlightRouteDiagnosticEdge(canvas,edgeId){
 const edges=[...canvas.querySelectorAll('[data-edge-id]')];
 for(const edge of edges){edge.classList.remove('route-diagnostic-focus');edge.removeAttribute('data-route-diagnostic-focus');}
 const selected=edges.find(edge=>edge.getAttribute('data-edge-id')===String(edgeId));
 if(selected){selected.classList.add('route-diagnostic-focus');selected.setAttribute('data-route-diagnostic-focus','true');}
 return Boolean(selected);
}
function clearRouteDiagnosticSegments(canvas){for(const line of canvas.querySelectorAll('[data-route-segment-overlay]'))line.remove();}
function highlightRouteDiagnosticSegment(canvas,edgeId,number){
 clearRouteDiagnosticSegments(canvas);
 const points=lastRouteSegmentGeometry(canvas,edgeId);
 if(!Number.isInteger(number)||number<1||number>=points.length)return false;
 const a=points[number-1],b=points[number];
 if(![a.x,a.y,b.x,b.y].every(Number.isFinite))return false;
 const line=document.createElementNS('http://www.w3.org/2000/svg','line');
 for(const [key,value] of Object.entries({x1:a.x,y1:a.y,x2:b.x,y2:b.y}))line.setAttribute(key,String(value));
 line.setAttribute('data-route-segment-overlay','true');line.setAttribute('class','route-diagnostic-segment-focus');line.setAttribute('pointer-events','none');
 canvas.append(line);
 const viewport=$('canvasViewport');
 if(viewport){const target=edgeViewportTarget(viewport.getBoundingClientRect(),line.getBoundingClientRect(),viewport.scrollLeft,viewport.scrollTop);if(target)viewport.scrollTo?.({...target,behavior:'auto'});}
 return true;
}
function refreshRouteQualityPanel(){
 const panel=$('routeQualityPanel');
 if(!panel||panel.hidden)return;
 renderRouteClearancePanel($('routeQualityResults'),lastRouteClearanceDiagnostics(svg),{
  filter:$('routeQualityFilter')?.value||"all",
  search:$('routeQualitySearch')?.value||"",
  selectedEdgeId:state.selected,
  onSelectSegment:(id,number)=>{if(!state.edges.some(edge=>String(edge.id)===String(id)))return;select(id);highlightRouteDiagnosticEdge(svg,id);highlightRouteDiagnosticSegment(svg,id,number);svg.focus?.();},
  onSelect:id=>{
   if(!state.edges.some(edge=>String(edge.id)===String(id)))return;
   select(id);
   const element=[...svg.querySelectorAll('[data-edge-id]')].find(el=>el.getAttribute('data-edge-id')===String(id));
   if(element){highlightRouteDiagnosticEdge(svg,id);const viewport=$('canvasViewport');const target=edgeViewportTarget(viewport.getBoundingClientRect(),element.getBoundingClientRect(),viewport.scrollLeft,viewport.scrollTop);if(target)viewport.scrollTo?.({...target,behavior:'smooth'});}
   svg.focus?.();
  }
 });
}
$('routeQualityFilter')?.addEventListener('change',refreshRouteQualityPanel);
$('routeQualitySearch')?.addEventListener('input',refreshRouteQualityPanel);
$('routeQualityToggle')?.addEventListener('click',()=>{
 const panel=$('routeQualityPanel');panel.hidden=!panel.hidden;if(panel.hidden){clearRouteDiagnosticSegments(svg);highlightRouteDiagnosticEdge(svg,null);}
 $('routeQualityToggle').setAttribute('aria-expanded',String(!panel.hidden));
 refreshRouteQualityPanel();
});
function paint(){interactiveFrames.cancel();invalidateInteractiveGraph();refreshDocumentStatus();const fullStarted=performance.now();const picker=$('guidePicker');if(picker){const previous=picker.value;picker.replaceChildren();state.guides.forEach((g,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=`${i+1} · ${g.axis==='x'?'Vertical':'Horizontal'} ${g.position} ${g.locked?'🔒':'🔓'}`;picker.append(option);});if([...picker.options].some(o=>o.value===previous))picker.value=previous;}activeMagneticGuides=[];renderGraph(svg,visibleGraph(),graphHandlers);drawEditorOverlays();refreshMulti();if(multi.size>1)renderMultiInspector();else renderInspector($("inspectorContent"),state,{update:updateProperty,remove:removeSelected,duplicate:duplicateSelected,renamePort:renameSelectedPort});renderLayers();updateCounts();updateSelectionLabel();document.dispatchEvent(new Event('openvisio:canvas-painted'));persist();fullPaintMetrics.record(performance.now()-fullStarted);if(!$('renderDiagnosticsPanel').hidden)refreshRenderDiagnostics();refreshRouteQualityPanel();}
function select(id){clearRouteDiagnosticSegments(svg);clearMulti();if(state.nodes.some(n=>n.id===id))multi.add(id);state.selected=id;paint();}
function onNodeClick(id,e){
 if(state.tool!=="select"||e.ctrlKey||e.metaKey||e.shiftKey)return;
 if(suppressNextClick){suppressNextClick=false;return;}
 if(multi.size>1&&multi.has(id))return;
 select(id);
}
function addShape(shape){recentShapes=trackRecentShape(recentShapes,shapeKey(shape));try{localStorage.setItem("openvisio-recent-shapes",JSON.stringify(recentShapes));}catch{}if(activeLibraryCategory==="recent")renderLibrary();saveUndo();const d=DEFAULTS[shape.type]||{};const n=makeNode({...shape,...d},250+Math.random()*240,180+Math.random()*220);state.nodes.push(n);clearMulti();multi.add(n.id);state.selected=n.id;paint();}
function onPointerDown(e,node){if(e.button!==0||!editableNode(state,node))return;if(state.tool==="connect"){e.stopPropagation();if(!connectFrom){connectFrom=node.id;state.selected=node.id;notify("Choisissez la forme de destination.");paint();}else if(connectFrom!==node.id){saveUndo();state.edges.push({...makeEdge(connectFrom,node.id),style:"smart"});connectFrom=null;state.tool="select";setActiveTool();paint();notify("Connexion créée.");}return;}if(state.tool!=="select")return;if(e.ctrlKey||e.metaKey||e.shiftKey){e.stopPropagation();if(multi.has(node.id))multi.delete(node.id);else multi.add(node.id);state.selected=multi.has(node.id)?node.id:(selectedNodes()[0]?.id||null);drag=null;paint();return;}
if(!multi.has(node.id)){clearMulti();multi.add(node.id);}if(node.groupId){state.nodes.filter(n=>n.groupId===node.groupId&&editableNode(state,n)).forEach(n=>multi.add(n.id));}state.selected=node.id;drag={id:node.id,startPoint:pointerToCanvas(e),positions:selectedNodes().map(n=>({id:n.id,x:n.x,y:n.y})),moved:false,historySaved:false,previousRedo:redoStack.slice()};svg.setPointerCapture?.(e.pointerId);refreshMulti();updateSelectionLabel();}
function pointerToCanvas(e){
 const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;
 const ctm=svg.getScreenCTM();
 if(!ctm)return null;
 const q=p.matrixTransform(ctm.inverse());
 return {x:Math.round(q.x),y:Math.round(q.y)};
}
function addWaypoint(e,edgeId){
 const edge=state.edges.find(v=>v.id===edgeId);const p=pointerToCanvas(e);
 if(!edge||!p)return;
 const from=state.nodes.find(n=>n.id===edge.from),to=state.nodes.find(n=>n.id===edge.to);
 if(!from||!to)return;
 try{
  const updated=insertWaypoint(from,to,edge.waypoints||[],{x:snap(p.x),y:snap(p.y)},edge.style||"orthogonal",Number(edge.offset)||0);
  saveUndo();edge.waypoints=updated;
 }catch(error){notify("Point non ajouté : "+error.message);return;}
 state.selected=edgeId;clearMulti();paint();notify("Point de passage ajouté.");
}
function removeWaypoint(edgeId,index){
 const edge=state.edges.find(v=>v.id===edgeId);
 if(!edge?.waypoints?.[index])return;
 saveUndo();edge.waypoints.splice(index,1);paint();notify("Point de passage supprimé.");
}
function onWaypointDown(e,edgeId,index){
 if(e.button!==0)return;
 const edge=state.edges.find(v=>v.id===edgeId);
 if(!edge||!edge.waypoints?.[index])return;
 waypointDrag={edgeId,index,saved:false,original:{...edge.waypoints[index]},previousRedo:redoStack.slice()};
 svg.setPointerCapture?.(e.pointerId);
}
svg.addEventListener("pointermove",e=>{
 if(!waypointDrag)return;
 const point=pointerToCanvas(e);if(!point)return;
 const edge=state.edges.find(v=>v.id===waypointDrag.edgeId);
 if(!edge?.waypoints?.[waypointDrag.index])return;
 const next={x:snap(point.x),y:snap(point.y)};
 if(edge.waypoints[waypointDrag.index].x===next.x&&edge.waypoints[waypointDrag.index].y===next.y)return;
 if(!waypointDrag.saved){saveUndo();waypointDrag.saved=true;waypointDrag.historySaved=true;}
 edge.waypoints[waypointDrag.index]=next;
 interactiveFrames.schedule();
});
svg.addEventListener("pointerup",()=>{if(waypointDrag){waypointDrag=null;paint();}});
svg.addEventListener("pointercancel",()=>{if(waypointDrag){const edge=state.edges.find(v=>v.id===waypointDrag.edgeId);if(edge?.waypoints?.[waypointDrag.index])edge.waypoints[waypointDrag.index]={...waypointDrag.original};cancelGestureHistory(waypointDrag);}waypointDrag=null;interactiveFrames.cancel();paint();});
svg.addEventListener("pointermove",e=>{if(!drag)return;const n=state.nodes.find(v=>v.id===drag.id);if(!n)return;const current=pointerToCanvas(e);if(!current||!drag.startPoint)return;const dx=current.x-drag.startPoint.x,dy=current.y-drag.startPoint.y;
if(!drag.moved&&(Math.abs(dx)>2||Math.abs(dy)>2)){saveUndo();drag.historySaved=true;drag.moved=true;}
if(!drag.moved)return;
const movedPositions=moveSelectionRigid(drag.positions,dx,dy,{grid:snapEnabled?GRID:0});
for(const item of state.nodes){const next=movedPositions.get(item.id);if(next){item.x=next.x;item.y=next.y;}}
if(magneticEnabled&&drag.positions.length===1){const item=state.nodes.find(v=>v.id===drag.id);if(item){const result=magneticSnap(item,state.nodes.filter(v=>v.id!==item.id&&visibleNode(state,v)),{threshold:7,grid:snapEnabled?GRID:0});item.x=Math.max(0,result.x);item.y=Math.max(0,result.y);activeMagneticGuides=result.guides;}}
if(customGuidesEnabled&&drag.positions.length===1){const item=state.nodes.find(v=>v.id===drag.id);if(item){const snapped=snapToGuides(item,state.guides);item.x=snapped.x;item.y=snapped.y;}}
interactiveFrames.schedule();});
svg.addEventListener("pointerup",()=>{if(drag){activeMagneticGuides=[];const moved=drag.moved;drag=null;if(moved){suppressNextClick=true;paint();}}});
svg.addEventListener("pointercancel",()=>{if(drag){const originals=new Map(drag.positions.map(p=>[p.id,p]));for(const node of state.nodes){const initial=originals.get(node.id);if(initial){node.x=initial.x;node.y=initial.y;}}cancelGestureHistory(drag);}drag=null;interactiveFrames.cancel();activeMagneticGuides=[];paint();});
svg.addEventListener("click",e=>{if(e.target===svg||e.target.tagName==="rect"&&e.target.parentElement===svg){state.selected=null;clearMulti();paint();}});
function drawEditorOverlays(){
 svg.querySelector('#editorOverlays')?.remove();
 const ns='http://www.w3.org/2000/svg';const g=document.createElementNS(ns,'g');g.id='editorOverlays';svg.append(g);
 const view=svg.viewBox.baseVal;
 const line=(x1,y1,x2,y2,color='#8794a7')=>{const el=document.createElementNS(ns,'line');for(const [k,v] of Object.entries({x1,y1,x2,y2,stroke:color,'stroke-width':1,'pointer-events':'none'}))el.setAttribute(k,String(v));g.append(el);};
 if(rulersEnabled){
  for(const x of rulerTicks(view.x,view.x+view.width,100)){line(x,view.y,x,view.y+14);const t=document.createElementNS(ns,'text');t.setAttribute('x',x+2);t.setAttribute('y',view.y+10);t.setAttribute('font-size','9');t.setAttribute('fill','#53657d');t.setAttribute('pointer-events','none');t.textContent=String(x);g.append(t);}
  for(const y of rulerTicks(view.y,view.y+view.height,100)){line(view.x,y,view.x+14,y);const t=document.createElementNS(ns,'text');t.setAttribute('x',view.x+2);t.setAttribute('y',y+24);t.setAttribute('font-size','9');t.setAttribute('fill','#53657d');t.setAttribute('pointer-events','none');t.textContent=String(y);g.append(t);}
 }
 if(customGuidesEnabled){state.guides.forEach((guide,index)=>{const vertical=guide.axis==='x';const el=document.createElementNS(ns,'line');for(const [k,v] of Object.entries({x1:vertical?guide.position:view.x,x2:vertical?guide.position:view.x+view.width,y1:vertical?view.y:guide.position,y2:vertical?view.y+view.height:guide.position,stroke:guide.locked?'#d97706':'#16a085','stroke-width':1.5,'stroke-dasharray':'7 3',style:guide.locked?'cursor:not-allowed':(vertical?'cursor:ew-resize':'cursor:ns-resize')}))el.setAttribute(k,String(v));el.setAttribute('aria-label',`Déplacer repère ${index+1}`);el.addEventListener('pointerdown',e=>{if(e.button!==0)return;e.stopPropagation();e.preventDefault();if(guide.locked){notify('Repère verrouillé : déverrouillez-le dans la liste.');return;}guideDrag={index,original:guide.position,moved:false};svg.setPointerCapture?.(e.pointerId);});g.append(el);});}
 const node=state.nodes.find(n=>n.id===state.selected);
 if(!node||multi.size!==1||!editableNode(state,node)||state.tool!=='select')return;
 const handle=document.createElementNS(ns,'rect');for(const [k,v] of Object.entries({x:node.x+node.w-6,y:node.y+node.h-6,width:12,height:12,rx:2,fill:'#fff',stroke:'#1683d8','stroke-width':2,style:'cursor:nwse-resize'}))handle.setAttribute(k,String(v));
 handle.setAttribute('aria-label','Redimensionner la forme');
 handle.addEventListener('pointerdown',e=>{if(e.button!==0)return;e.stopPropagation();e.preventDefault();resizeDrag={id:node.id,origin:pointerToCanvas(e),w:node.w,h:node.h,moved:false,historySaved:false,previousRedo:redoStack.slice(),proportional:e.shiftKey};svg.setPointerCapture?.(e.pointerId);});g.append(handle);
}
svg.addEventListener('pointermove',e=>{if(!resizeDrag)return;const point=pointerToCanvas(e);if(!point||!resizeDrag.origin)return;const node=state.nodes.find(n=>n.id===resizeDrag.id);if(!node)return;const dx=point.x-resizeDrag.origin.x,dy=point.y-resizeDrag.origin.y;if(!resizeDrag.moved&&Math.abs(dx)+Math.abs(dy)<2)return;if(!resizeDrag.moved){saveUndo();resizeDrag.historySaved=true;resizeDrag.moved=true;}const dims=resizeFromCorner({w:resizeDrag.w,h:resizeDrag.h},dx,dy,{grid:snapEnabled?GRID:0,proportional:e.shiftKey||resizeDrag.proportional});node.w=dims.w;node.h=dims.h;interactiveFrames.schedule();});
svg.addEventListener('pointerup',()=>{if(resizeDrag){const changed=resizeDrag.moved;resizeDrag=null;if(changed){suppressNextClick=true;paint();}}});
svg.addEventListener('pointercancel',()=>{if(resizeDrag){const node=state.nodes.find(n=>n.id===resizeDrag.id);if(node){node.w=resizeDrag.w;node.h=resizeDrag.h;}cancelGestureHistory(resizeDrag);resizeDrag=null;interactiveFrames.cancel();paint();}});
$('showRulers')?.addEventListener('change',e=>{rulersEnabled=e.target.checked;paint();});
$('showCustomGuides')?.addEventListener('change',e=>{customGuidesEnabled=e.target.checked;paint();});
$('addVerticalGuide')?.addEventListener('click',()=>{saveUndo();state.guides=normalizeGuides([...state.guides,{axis:'x',position:Math.round(svg.viewBox.baseVal.x+svg.viewBox.baseVal.width/2)}]);paint();});
$('addHorizontalGuide')?.addEventListener('click',()=>{saveUndo();state.guides=normalizeGuides([...state.guides,{axis:'y',position:Math.round(svg.viewBox.baseVal.y+svg.viewBox.baseVal.height/2)}]);paint();});
$('toggleGuideLock')?.addEventListener('click',()=>{const index=Number($('guidePicker').value);if(!Number.isInteger(index)||index<0||index>=state.guides.length){notify('Sélectionnez un repère.');return;}saveUndo();state.guides=toggleGuideLock(state.guides,index);paint();});
$('clearCustomGuides')?.addEventListener('click',()=>{if(state.guides.length)saveUndo();state.guides=[];paint();});
svg.addEventListener('pointermove',e=>{if(!guideDrag)return;const p=pointerToCanvas(e);if(!p)return;const axis=state.guides[guideDrag.index]?.axis;if(!axis)return;const position=Math.max(0,Math.round(p[axis]));if(position!==state.guides[guideDrag.index].position){guideDrag.moved=true;state.guides=moveGuide(state.guides,guideDrag.index,position);}drawEditorOverlays();});
svg.addEventListener('pointerup',()=>{if(guideDrag){if(guideDrag.moved){const final=state.guides[guideDrag.index].position;state.guides[guideDrag.index].position=guideDrag.original;saveUndo();state.guides[guideDrag.index].position=final;}guideDrag=null;paint();}});
svg.addEventListener('pointercancel',()=>{if(guideDrag){state.guides[guideDrag.index].position=guideDrag.original;guideDrag=null;paint();}});

function drawMagneticGuides(){
 if(!magneticEnabled||!activeMagneticGuides.length)return;
 const namespace='http://www.w3.org/2000/svg';
 const view=svg.viewBox.baseVal;
 for(const guide of activeMagneticGuides){
  const line=document.createElementNS(namespace,'line');
  const vertical=guide.axis==='x';
  line.setAttribute('x1',String(vertical?guide.position:view.x));
  line.setAttribute('x2',String(vertical?guide.position:view.x+view.width));
  line.setAttribute('y1',String(vertical?view.y:guide.position));
  line.setAttribute('y2',String(vertical?view.y+view.height:guide.position));
  line.setAttribute('stroke','#e455a3');line.setAttribute('stroke-width','1.5');
  line.setAttribute('stroke-dasharray','5 4');line.setAttribute('pointer-events','none');
  line.setAttribute('class','magnetic-guide');svg.append(line);
 }
}
function updateProperty(key,value){const n=state.nodes.find(v=>v.id===state.selected);if(n){
 let plan;
 try{plan=planNodeProperty(n,key,value,state.edges);}catch(err){notify(err.message);return;}
 if(!plan.ok){
  const affected=plan.impact.affected;
  const details=affected.slice(0,8).map(x=>`${x.edgeId} (${x.sides.map(s=>s.port).join(', ')})`).join('\n');
  notify(`${affected.length} liaison(s) utilisent des ports supprimés : modification refusée.`);
  window.alert(`Ports encore utilisés par ${affected.length} liaison(s). Réaffectez les connexions avant de retirer ces ports.\n${details}${affected.length>8?'\n…':''}`);
  return;
 }
 if(!plan.changed)return;
 saveUndo();applyNodeProperty(n,plan);
 }else{const edge=state.edges.find(v=>v.id===state.selected);if(edge&&["label","style","offset","waypoints","fromPort","toPort","sourceInterface","targetInterface",...RELATION_FIELDS.map(x=>x[0])].includes(key)){let parsed=RELATION_FIELDS.some(([k])=>k===key)?validateRelationField(key,value):value;
 if(key==="waypoints"){try{parsed=parseWaypoints(value);}catch(error){notify("Coordonnées invalides : "+error.message);return;}}
 let edgePlan;
 try{edgePlan=planEdgeProperty(edge,key,parsed,state.nodes);}catch(err){notify(err.message);return;}
 if(!edgePlan.changed)return;saveUndo();applyEdgeProperty(edge,edgePlan);}}paint();}
function renameSelectedPort(){
 const node=state.nodes.find(n=>n.id===state.selected);if(!node)return;
 const oldName=window.prompt('Port existant à renommer :',(node.ports||[])[0]||'');
 if(oldName===null)return;
 const newName=window.prompt('Nouveau nom du port :',oldName);
 if(newName===null)return;
 try{
  const plan=planPortRename(node,oldName.trim(),newName.trim(),state.edges);
  if(!plan.changed)return;
  const details=plan.affected.slice(0,12).map(x=>`${x.edgeId} : ${x.sides.join(' + ')}`).join('\n');
  const message=`Renommer ${plan.oldName} → ${plan.newName} sur ${node.title||node.id} ?\n${plan.affected.length} connexion(s) seront réaffectées.\n${details}${plan.affected.length>12?'\n…':''}\nLes propriétés SAN et les points de passage restent inchangés.`;
  if(!window.confirm(message))return;
  saveUndo();applyPortRename(state.nodes,state.edges,plan);paint();notify('Port renommé et connexions réaffectées');
 }catch(err){notify(err.message);window.alert(err.message);}
}
function removeSelected(){if(!state.selected&&!multi.size)return;saveUndo();const ids=new Set([...multi,state.selected].filter(Boolean));state.nodes=state.nodes.filter(n=>!ids.has(n.id));state.edges=state.edges.filter(e=>!ids.has(e.id)&&!ids.has(e.from)&&!ids.has(e.to));state.selected=null;clearMulti();paint();}
function duplicateSelected(){
 const ns=selectedNodes();if(!ns.length)return;
 const copies=duplicateSubgraph(state.nodes,state.edges,ns.map(n=>n.id));
 saveUndo();state.nodes.push(...copies.nodes);state.edges.push(...copies.edges);
 clearMulti();for(const n of copies.nodes)multi.add(n.id);
 state.selected=copies.nodes[0]?.id||null;paint();
 notify(`${copies.nodes.length} équipement(s) et ${copies.edges.length} connexion(s) dupliqués.`);
}

function setActiveTool(){document.querySelectorAll("[data-tool]").forEach(b=>b.classList.toggle("active",b.dataset.tool===state.tool));}
let favoriteShapes=readFavorites(localStorage.getItem("openvisio-favorites"));
let recentShapes=readRecentShapes(localStorage.getItem("openvisio-recent-shapes"));
let activeLibraryCategory="all";
function renderLibraryCategories(){
 const host=$("libraryCategories");host.replaceChildren();
 for(const category of CATEGORIES){
  const button=document.createElement("button");button.type="button";button.className=`library-category ${activeLibraryCategory===category.id?"active":""}`;
  button.textContent=category.name;button.setAttribute("aria-pressed",String(activeLibraryCategory===category.id));
  button.addEventListener("click",()=>{activeLibraryCategory=category.id;$("categoryFilter").value=["favorites","recent","all"].includes(category.id)?"":category.id;renderLibraryCategories();renderLibrary();});
  host.append(button);
 }
}
function renderLibrary(){
 const q=$("shapeSearch").value,vendor=$("vendorFilter").value,cat=$("categoryFilter").value;
 const effectiveCategory=["favorites","recent"].includes(activeLibraryCategory)?activeLibraryCategory:cat||activeLibraryCategory;
 const host=$("shapeLibrary");host.replaceChildren();
 for(const shape of filterShapes(SHAPES,{query:q,vendor,category:effectiveCategory,favorites:favoriteShapes,recent:recentShapes}).sort((a,b)=>effectiveCategory==="recent"?recentShapes.indexOf(shapeKey(a))-recentShapes.indexOf(shapeKey(b)):0)){
  const wrapper=document.createElement("div");wrapper.className="shape-entry";
  const button=document.createElement("button");button.type="button";button.className="shape-card";
  const icon=document.createElement("span");icon.className="shape-icon";icon.textContent=shape.icon;
  const name=document.createElement("strong");name.textContent=shape.name;
  const vendorLabel=document.createElement("small");vendorLabel.textContent=shape.vendor;
  button.append(icon,name,vendorLabel);button.addEventListener("click",()=>addShape(shape));
  const favorite=document.createElement("button");favorite.type="button";favorite.className="favorite-shape";
  const key=shapeKey(shape),isFavorite=favoriteShapes.includes(key);
  favorite.textContent=isFavorite?"★":"☆";favorite.title=isFavorite?"Retirer des favoris":"Ajouter aux favoris";
  favorite.setAttribute("aria-label",`${favorite.title} : ${shape.name}`);favorite.setAttribute("aria-pressed",String(isFavorite));
  favorite.addEventListener("click",()=>{favoriteShapes=toggleFavorite(favoriteShapes,key);try{localStorage.setItem("openvisio-favorites",JSON.stringify(favoriteShapes));}catch{}renderLibrary();});
  wrapper.append(button,favorite);host.append(wrapper);
 }
 if(!host.children.length){const empty=document.createElement("p");empty.className="hint";empty.textContent=effectiveCategory==="recent"?"Aucune forme récente. Ajoutez une forme au diagramme pour la retrouver ici.":"Aucune forme ne correspond aux filtres.";host.append(empty);}
}
renderLibraryCategories();
$("shapeSearch").addEventListener("input",renderLibrary);$("vendorFilter").addEventListener("change",renderLibrary);$("categoryFilter").addEventListener("change",()=>{activeLibraryCategory="all";renderLibraryCategories();renderLibrary();});
document.querySelectorAll("[data-shape]").forEach(b=>b.addEventListener("click",()=>addShape(SHAPES.find(s=>s.type===b.dataset.shape)||SHAPES[0])));
document.querySelectorAll("[data-tool]").forEach(b=>b.addEventListener("click",()=>{state.tool=b.dataset.tool;connectFrom=null;setActiveTool();notify(state.tool==="connect"?"Cliquez sur la source puis sur la destination.":"Mode sélection actif.");}));
$("undoBtn").addEventListener("click",()=>travelHistory(undoStack,redoStack,"Action annulée."));
$("redoBtn").addEventListener("click",()=>travelHistory(redoStack,undoStack,"Action rétablie."));
$("newDiagram").addEventListener("click",()=>{if(isDocumentDirty() && !confirm("Créer un nouveau diagramme ? Les modifications non enregistrées seront perdues."))return;saveUndo();state.nodes=[];state.edges=[];declaredZones=[];persistZones();lastSanImport=null;persistSanImport();state.groups=[];state.layers=[{id:"default",name:"Principal",visible:true,locked:false}];state.selected=null;clearMulti();savedFingerprint=documentFingerprint();exportPendingVerification=false;paint();});
$("addFirstShape").addEventListener("click",()=>addShape(SHAPES[0]));
$("toggleLibraries").addEventListener("click",()=> $("libraryPanel").classList.toggle("hidden-panel"));$("closeLibrary").addEventListener("click",()=> $("libraryPanel").classList.add("hidden-panel"));
// v21.5 : un seul état visuel partagé pour les boutons et le mode canevas seul.
function syncWorkspaceControls(){
  const libVisible=!$("libraryPanel").classList.contains("hidden-panel");
  const inspectorVisible=!$("inspectorPanel").classList.contains("hidden-panel");
  $("toggleLibraries").setAttribute("aria-expanded",String(libVisible));
  $("toggleInspector").setAttribute("aria-expanded",String(inspectorVisible));
  $("focusCanvasBtn").setAttribute("aria-pressed",String(!libVisible&&!inspectorVisible));
}
$("focusCanvasBtn").addEventListener("click",()=>{
  const bothHidden=$("libraryPanel").classList.contains("hidden-panel")&&$("inspectorPanel").classList.contains("hidden-panel");
  $("libraryPanel").classList.toggle("hidden-panel",!bothHidden);
  $("inspectorPanel").classList.toggle("hidden-panel",!bothHidden);
  syncWorkspaceControls();
});
$("toggleInspector").addEventListener("click",()=>{$("inspectorPanel").classList.toggle("hidden-panel");syncWorkspaceControls();});$("closeInspector").addEventListener("click",()=>{$("inspectorPanel").classList.add("hidden-panel");syncWorkspaceControls();});
$("toggleLibraries").addEventListener("click",syncWorkspaceControls);$("closeLibrary").addEventListener("click",syncWorkspaceControls);
document.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.shiftKey&&!e.altKey&&e.key.toLowerCase()==="f"){e.preventDefault();$("focusCanvasBtn").click();}});
syncWorkspaceControls();
function setZoom(z){state.zoom=Math.min(1.5,Math.max(.5,z));svg.style.width=`${100*state.zoom}%`;svg.style.height=`${100*state.zoom}%`;$("zoomValue").textContent=`${Math.round(state.zoom*100)}%`;}
$("zoomIn").addEventListener("click",()=>setZoom(state.zoom+.1));$("zoomOut").addEventListener("click",()=>setZoom(state.zoom-.1));$("fitCanvas").addEventListener("click",()=>setZoom(1));
const portableDependencies={restoreGraph:restore,validateZones,validateSanImport};
$("portableExportBtn").addEventListener("click",async()=>{
 try{
  const raw=await exportPortableBackup(snapshot(state),declaredZones,lastSanImport);
  const blob=new Blob([raw],{type:"application/json;charset=utf-8"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");a.href=url;a.download="openvisio-backup-v209.json";a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  notify("Sauvegarde externe exportée (empreinte SHA-256).");
 }catch(error){notify("Export impossible : "+error.message);}
});
$("portableImportBtn").addEventListener("click",()=>$("portableImportFile").click());
$("portableImportFile").addEventListener("change",async event=>{
 const file=event.target.files?.[0];event.target.value="";if(!file)return;
 try{
  if(file.size>20_000_000)throw Error("Fichier trop volumineux (20 Mo maximum)");
  const inspection=await inspectPortableBackup(await file.text(),portableDependencies);
  const {nodes,edges,zones}=inspection.summary;
  if(!window.confirm(`Restaurer cette sauvegarde (${nodes} objets, ${edges} connexions, ${zones} zones) ? Le document courant sera remplacé.`))return;
  const result=restorePortableBackup(localStorage,DOCUMENT_KEY,inspection,portableDependencies);
  if(!result.changed){notify("Document déjà identique.");return;}
  saveUndo();
  const doc=result.document;
  Object.assign(state,doc.graph);declaredZones=doc.zones;lastSanImport=doc.sanImport;
  clearMulti();paint();notify(result.changed?"Sauvegarde restaurée.":"Document déjà identique.");
 }catch(error){notify("Restauration refusée : "+error.message);}
});
$("exportBtn").addEventListener("click",()=>{if(!validateGraph(state)){notify("Le diagramme contient une connexion invalide.");return;}const clone=svg.cloneNode(true);clone.setAttribute("xmlns","http://www.w3.org/2000/svg");clone.style.width="1200px";clone.style.height="760px";const blob=new Blob([new XMLSerializer().serializeToString(clone)],{type:"image/svg+xml;charset=utf-8"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="openvisio-diagram.svg";a.click();URL.revokeObjectURL(url);notify("Export SVG préparé.");});

function downloadText(name,text,type){
 const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
// Indicateur documentaire : les modifications de sélection ne comptent pas.
function documentFingerprint(){
 return JSON.stringify({nodes:state.nodes,edges:state.edges,groups:state.groups,layers:state.layers,guides:state.guides,zones:declaredZones,sanImport:lastSanImport});
}
let savedFingerprint = documentFingerprint();
let nativeFileHandle = null;
let exportPendingVerification = false;
const documentStatus = document.createElement('span');
documentStatus.id='documentSaveStatus';
documentStatus.setAttribute('role','status');
documentStatus.setAttribute('aria-live','polite');
documentStatus.style.cssText='font-size:12px;padding:4px 8px;border-radius:6px;white-space:nowrap';
($('saveJsonBtn').parentElement || document.body).append(documentStatus);
function isDocumentDirty(){return documentFingerprint()!==savedFingerprint;}
function refreshDocumentStatus(){
 const dirty=isDocumentDirty();
 documentStatus.textContent=dirty?(exportPendingVerification?'● Export lancé — téléchargement à vérifier':'● Modifications non enregistrées'):'✓ Document ouvert ou réinitialisé';
 documentStatus.title=dirty?'Le téléchargement JSON ne confirme pas une écriture sur disque. Réouvrez le fichier pour vérifier la sauvegarde.':'Aucune modification depuis l’ouverture ou la création du document.';
 documentStatus.style.background=dirty?'#fff1ce':'#e4f4e8';
 documentStatus.style.color='#273344';
}
window.addEventListener('beforeunload',event=>{
 if(!isDocumentDirty())return;
 event.preventDefault();event.returnValue='';
});
refreshDocumentStatus();
// Sauvegarde native uniquement si le navigateur expose File System Access.
// Le statut est validé seulement après fermeture réussie du flux d'écriture.
const nativeSaveButton=document.createElement('button');
nativeSaveButton.id='saveNativeBtn';nativeSaveButton.type='button';
nativeSaveButton.textContent='Enregistrer sur disque…';
nativeSaveButton.title='Écriture confirmée sur disque (navigateurs compatibles)';
($('saveJsonBtn').parentElement || document.body).append(nativeSaveButton);
async function saveNativeDocument(){
 if(typeof window.showSaveFilePicker!=='function'){
  notify('Sauvegarde native indisponible ici : utilisez Export JSON puis vérifiez le fichier téléchargé.');return false;
 }
 if(!validateGraph(state)){notify('Le diagramme contient une connexion invalide.');return false;}
 try{
  const content=serializeSanDiagram({...exportDiagram(state,declaredZones),sanImport:lastSanImport,guides:state.guides});
  const parsed=JSON.stringify(JSON.parse(content),null,2);
  const handle=nativeFileHandle || await window.showSaveFilePicker({suggestedName:'openvisio-diagram.json',types:[{description:'Diagramme OpenVisio JSON',accept:{'application/json':['.json']}}]});
  const writable=await handle.createWritable();
  try{await writable.write(parsed);await writable.close();}
  catch(error){try{await writable.abort();}catch{}throw error;}
  nativeFileHandle=handle;savedFingerprint=documentFingerprint();exportPendingVerification=false;
  refreshDocumentStatus();notify('Fichier JSON écrit sur disque.');return true;
 }catch(error){
  if(error?.name!=='AbortError')notify('Sauvegarde native non confirmée : '+(error?.message||'échec'));
  return false;
 }
}
nativeSaveButton.addEventListener('click',saveNativeDocument);
$('saveJsonBtn').addEventListener("click",()=>{
 if(!validateGraph(state)){notify("Le diagramme contient une connexion invalide.");return;}
 try{
  const json=serializeSanDiagram({...exportDiagram(state,declaredZones),sanImport:lastSanImport,guides:state.guides});
  downloadText("openvisio-diagram.json",JSON.stringify(JSON.parse(json),null,2),"application/json");
  exportPendingVerification=true;refreshDocumentStatus();notify("Export JSON lancé : vérifiez le téléchargement et conservez le fichier. Le document reste signalé comme non confirmé.");
 }catch(error){notify("Export refusé : "+error.message);}
});
$("openJsonBtn").addEventListener("click",()=>$("openJsonInput").click());
$("openJsonInput").addEventListener("change",async e=>{
 const file=e.target.files?.[0];if(!file)return;
 try{
  const data=deserializeSanDiagram(await file.text());
  if(!Array.isArray(data.nodes)||!Array.isArray(data.edges)||!data.nodes.every(n=>n&&typeof n.id==="string"&&typeof n.type==="string")||!data.edges.every(v=>v&&typeof v.id==="string"&&typeof v.from==="string"&&typeof v.to==="string"))throw new Error("structure");
  const next={nodes:data.nodes,edges:data.edges};
  if(!validateGraph(next)||new Set(data.nodes.map(n=>n.id)).size!==data.nodes.length||new Set(data.edges.map(e=>e.id)).size!==data.edges.length)throw new Error("references");
  const zones=importZones(data);const importedSan=validateSanImport(data.sanImport??null);
  if (isDocumentDirty() && !confirm("Ouvrir ce fichier remplacera le diagramme actuel et ses modifications non enregistrées. Continuer ?")) { e.target.value=""; return; }
  saveUndo();declaredZones=zones;persistZones();lastSanImport=importedSan;persistSanImport();state.nodes=data.nodes;state.edges=data.edges;state.groups=Array.isArray(data.groups)?data.groups:[];state.layers=Array.isArray(data.layers)?data.layers:[{id:"default",name:"Principal",visible:true,locked:false}];state.guides=normalizeGuides(data.guides??[]);state.selected=null;clearMulti();nativeFileHandle=null;savedFingerprint=documentFingerprint();exportPendingVerification=false;paint();notify("Diagramme JSON importé.");
 }catch{notify("Import refusé : JSON invalide ou connexions incohérentes.");}
 e.target.value="";
});

function changeZOrder(action){
 const ids=[...multi].filter(id=>state.nodes.some(n=>n.id===id));
 if(!ids.length){notify('Sélectionnez une ou plusieurs formes.');return;}
 const updated=reorderShapes(state.nodes,ids,action);
 if(updated.every((node,index)=>node===state.nodes[index])){notify('Ordre déjà atteint.');return;}
 saveUndo();state.nodes=updated;paint();notify('Ordre de superposition modifié.');
}
for(const action of ['front','forward','backward','back']){
 const button=$('zOrder'+action[0].toUpperCase()+action.slice(1));
 button?.addEventListener('click',()=>changeZOrder(action));
}
// v41.0 : aperçu explicite, aucune mutation avant confirmation, annulation via historique.
$("autoGridLayout")?.addEventListener("click",()=>{
 const nodes=selectedNodes().filter(n=>editableNode(state,n));
 if(nodes.length<2){notify("Sélectionnez au moins deux formes modifiables.");return;}
 let plan;
 try{plan=planCollisionFreeGrid(nodes,{gap:24});}
 catch(error){notify("Placement impossible : "+error.message);return;}
 const changed=plan.some(p=>{const n=nodes.find(n=>n.id===p.id);return n.x!==p.x||n.y!==p.y;});
 if(!changed){notify("Les formes sont déjà placées sur cette grille.");return;}
 const preview=plan.slice(0,5).map(p=>String(p.id)+" → ("+Math.round(p.x)+", "+Math.round(p.y)+")").join("\n");
 if(!confirm("Aperçu du placement automatique ("+nodes.length+" formes) :\n"+preview+(plan.length>5?"\n…":"")+"\n\nAppliquer ? Annuler reste disponible."))return;
 saveUndo();applyGridPlan(nodes,plan);paint();notify("Placement automatique appliqué. Annuler pour revenir en arrière.");
});
function alignOrDistribute(mode){
 const ns=selectedNodes().filter(n=>editableNode(state,n));
 const minimum=(mode==="distributeX"||mode==="distributeY")?3:2;
 if(ns.length<minimum){notify(`Sélectionnez au moins ${minimum} formes modifiables.`);return;}
 saveUndo();arrangeNodes(ns,mode,{grid:snapEnabled?GRID:0,gap:24});paint();
}
for(const mode of ["alignLeft","alignTop","alignCenterX","alignCenterY","distributeX","distributeY","distributeSafeX","distributeSafeY","stackX","stackY"]){
 const btn=$(mode);if(!btn)continue;btn.disabled=false;btn.addEventListener("click",()=>alignOrDistribute(mode));
}

for(const [buttonId,axis] of [['alignRight','right'],['alignBottom','bottom'],['alignReferenceX','centerX'],['alignReferenceY','centerY']]){
 $(buttonId)?.addEventListener('click',()=>{
  const nodes=selectedNodes().filter(n=>editableNode(state,n));
  if(nodes.length<2){notify('Sélectionnez au moins deux formes modifiables.');return;}
  const reference=state.selected&&nodes.some(n=>n.id===state.selected)?state.selected:nodes[0].id;
  saveUndo();alignToReference(nodes,reference,axis);paint();notify('Alignement effectué sur la forme de référence.');
 });
}
for(const [buttonId,mode] of [['uniformWidth','width'],['uniformHeight','height'],['uniformBoth','both']]){
 $(buttonId)?.addEventListener('click',()=>{
  const nodes=selectedNodes().filter(n=>editableNode(state,n));
  if(nodes.length<2){notify('Sélectionnez au moins deux formes modifiables.');return;}
  const reference=nodes.find(n=>n.id===state.selected)||nodes[0];
  const changed=uniformDimensions(nodes,reference.id,mode);
  if(!changed)return;
  saveUndo(); // restore original values to history, then apply resized values
  for(const [node,dimensions] of changed) {node.w=dimensions.w;node.h=dimensions.h;}
  paint();notify('Dimensions harmonisées.');
 });
}
$('magneticGuides')?.addEventListener('change',e=>{magneticEnabled=e.target.checked;notify(magneticEnabled?'Guides magnétiques activés.':'Guides magnétiques désactivés.');});
function applyVectorTransform(operation,degrees=90){
 const selected=selectedNodes().filter(n=>editableNode(state,n));
 if(!selected.length){notify('Sélectionnez une forme modifiable.');return;}
 const updated=transformNodes(selected,operation,{degrees});
 saveUndo();const byId=new Map(updated.map(n=>[n.id,n]));
 state.nodes=state.nodes.map(n=>byId.get(n.id)||n);
 paint();notify('Transformation vectorielle appliquée.');
}
for(const [id,op,angle] of [['rotateLeft','rotate',-90],['rotateRight','rotate',90],['flipHorizontal','flipH',0],['flipVertical','flipV',0],['resetTransform','reset',0]]){
 $(id)?.addEventListener('click',()=>applyVectorTransform(op,angle));
}
function renderLayers(){const host=$("layerList");host.replaceChildren();for(const layer of state.layers){const row=document.createElement("div");row.className="layer-row";const name=document.createElement("span");name.textContent=layer.name;const visible=document.createElement("button");visible.textContent=layer.visible?"◉":"○";visible.title="Afficher/masquer";visible.addEventListener("click",()=>{saveUndo();layer.visible=!layer.visible;paint();});const locked=document.createElement("button");locked.textContent=layer.locked?"🔒":"🔓";locked.title="Verrouiller/déverrouiller";locked.addEventListener("click",()=>{saveUndo();layer.locked=!layer.locked;paint();});row.append(name,visible,locked);host.append(row);}}
function renderMultiInspector(){
 const host=$("inspectorContent");host.replaceChildren();
 const nodes=selectedNodes();const editable=nodes.filter(n=>editableNode(state,n));
 const heading=document.createElement("h3");heading.textContent=`${nodes.length} formes sélectionnées`;host.append(heading);
 const bounds=selectionBounds(nodes);const info=document.createElement("p");info.className="multi-inspector-summary";
 info.textContent=`Types : ${selectionKinds(nodes).join(", ")}${bounds?` · Zone : ${Math.round(bounds.width)} × ${Math.round(bounds.height)}`:""} · Modifiables : ${editable.length}/${nodes.length}`;host.append(info);
 const wrapper=document.createElement("div");wrapper.className="multi-inspector";host.append(wrapper);
 for(const [key,label,type] of [["fill","Fond","color"],["stroke","Contour","color"],["subtitle","Sous-titre","text"]]){
  const l=document.createElement("label");l.textContent=label;const input=document.createElement("input");input.type=type;
  const common=commonValue(nodes,key);
  if(type==="color"){
   input.value=common.mixed?"#ffffff":(/^#[0-9a-f]{6}$/i.test(common.value||"")?common.value:"#ffffff");
   if(common.mixed)input.title="Valeurs différentes — choisir une couleur pour uniformiser";
  }else{input.value=common.mixed?"":(common.value??"");input.placeholder=common.mixed?"Valeurs différentes":"";}
  input.disabled=!editable.length;
  input.addEventListener("change",()=>{if(!editable.length||editable.every(n=>n[key]===input.value))return;saveUndo();editable.forEach(n=>n[key]=input.value);paint();});
  l.append(input);wrapper.append(l);
 }
 const label=document.createElement("label");label.textContent="Affecter au calque";
 const select=document.createElement("select");const layerValue=commonValue(nodes,"layerId");
 if(layerValue.mixed){const mixed=document.createElement("option");mixed.value="";mixed.textContent="— Calques différents —";select.append(mixed);}
 for(const layer of state.layers){const opt=document.createElement("option");opt.value=layer.id;opt.textContent=layer.name;select.append(opt);}
 select.value=layerValue.mixed?"":(layerValue.value||"default");select.disabled=!editable.length;
 select.addEventListener("change",()=>{if(!select.value||!editable.length||editable.every(n=>(n.layerId||"default")===select.value))return;saveUndo();setLayer(state,editable.map(n=>n.id),select.value);paint();});
 label.append(select);wrapper.append(label);
}
$("groupBtn").addEventListener("click",()=>{if(multi.size<2){notify("Sélectionnez au moins deux formes.");return;}saveUndo();groupNodes(state,[...multi]);paint();notify("Groupe créé.");});
$("ungroupBtn").addEventListener("click",()=>{saveUndo();const count=ungroupNodes(state,[...multi]);paint();notify(count?"Groupe dissocié.":"Aucun groupe sélectionné.");});
$("newLayerBtn").addEventListener("click",()=>{const name=prompt("Nom du nouveau calque :","Nouveau calque");if(!name?.trim())return;saveUndo();createLayer(state,name.trim());paint();});

document.addEventListener("keydown",e=>{const tag=e.target?.tagName?.toLowerCase();if(["input","textarea","select"].includes(tag)||e.target?.isContentEditable)return;if(e.key==="Escape"){state.tool="select";connectFrom=null;state.selected=null;clearMulti();setActiveTool();paint();}if((e.ctrlKey||e.metaKey)&&!e.altKey&&e.key.toLowerCase()==="z"){e.preventDefault();$(e.shiftKey?"redoBtn":"undoBtn").click();}if((e.ctrlKey||e.metaKey)&&!e.altKey&&e.key.toLowerCase()==="y"){e.preventDefault();$("redoBtn").click();}if(e.key.toLowerCase()==="f"&&!e.ctrlKey){e.preventDefault();$("toggleLibraries").click();}
 if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="a"){e.preventDefault();clearMulti();state.nodes.forEach(n=>multi.add(n.id));state.selected=state.nodes[0]?.id||null;paint();}
 if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="d"){e.preventDefault();duplicateSelected();}
 if((e.key==="Delete"||e.key==="Backspace")&&state.selected){e.preventDefault();removeSelected();}});
try{const raw=localStorage.getItem("openvisio-v82");if(raw){const restored=restore(raw);state.nodes=restored.nodes;state.edges=restored.edges;state.groups=restored.groups||[];state.layers=restored.layers?.length?restored.layers:state.layers;state.guides=normalizeGuides(restored.guides??[]);}}catch{}
// Initial rendering is deferred until persisted document state is restored.
// Galerie de modèles : insérée dans le ruban existant sans dépendance supplémentaire.
const templatePicker=document.createElement("select");
templatePicker.setAttribute("aria-label","Créer un diagramme depuis un modèle");
templatePicker.title="Modèles d'infrastructure";
const placeholder=document.createElement("option");placeholder.value="";placeholder.textContent="Modèles d’infrastructure…";templatePicker.append(placeholder);
for(const t of TEMPLATES){const opt=document.createElement("option");opt.value=t.id;opt.textContent=t.name;templatePicker.append(opt);}
templatePicker.addEventListener("change",()=>{
 if(!templatePicker.value)return;
 if(state.nodes.length&&!window.confirm("Remplacer le diagramme actuel par ce modèle ?")){templatePicker.value="";return;}
 saveUndo();const graph=createTemplate(templatePicker.value);state.nodes=graph.nodes;state.edges=graph.edges;state.selected=null;clearMulti();paint();notify("Modèle chargé : "+TEMPLATES.find(t=>t.id===templatePicker.value).name);templatePicker.value="";
});
const ribbon=document.querySelector(".ribbon")||document.querySelector("header")||document.body;
ribbon.append(templatePicker);

const snapButton=document.createElement("button");
snapButton.type="button";snapButton.textContent="Aimantation : OFF";snapButton.title="Activer la grille magnétique de 10 unités";
snapButton.setAttribute("aria-pressed","false");
snapButton.addEventListener("click",()=>{snapEnabled=!snapEnabled;snapButton.textContent=`Aimantation : ${snapEnabled?"ON":"OFF"}`;snapButton.setAttribute("aria-pressed",String(snapEnabled));notify(snapEnabled?"Grille magnétique activée.":"Grille magnétique désactivée.");});
(document.querySelector(".edit-controls")||document.querySelector(".canvas-toolbar")||document.body).append(snapButton);


// Raccourci de recherche : Ctrl+K / Cmd+K, sans détourner la saisie dans l'inspecteur.
document.addEventListener("keydown",event=>{
 if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="k"){
  event.preventDefault();
  const library=$("libraryPanel");
  if(library.classList.contains("hidden-panel"))$("toggleLibraries").click();
  $("shapeSearch").focus();
  $("shapeSearch").select();
 }
});

// v12.0 : panneau global de câblage et exports CSV.
const zoningEditor=$("zoningEditor");
function readZones(){return declaredZones;}
function persistZones(){persist();}
try{declaredZones=validateZones(JSON.parse(localStorage.getItem("openvisio-zones-v1")||"[]"));}catch{declaredZones=[];}
let pendingSanImport=null;
function persistSanImport(){persist();}
try{lastSanImport=validateSanImport(JSON.parse(localStorage.getItem('openvisio-san-import-v1')||'null'));}catch{lastSanImport=null;}
// Migration non destructive : le document unifié prime sur les trois anciennes clés.
let unifiedDocumentInvalid=false;
// v21.3 : panneau de diagnostic accessible à la demande, sans restauration automatique.
function refreshRecoveryStatus(){
 const result=inspectRecovery(localStorage,DOCUMENT_KEY,{restoreGraph:restore,validateZones,validateSanImport});
 const labels={valid:'Valide',invalid:'Corrompu / illisible',absent:'Absent'};
 $('recoveryPrimaryStatus').textContent=labels[result.primary];
 $('recoveryBackupStatus').textContent=labels[result.backup];
 $('recoveryStatusSummary').textContent=result.recoverable?'Au moins une version locale est lisible.':'Aucune version locale valide détectée.';
 const list=$('recoveryIssues');list.replaceChildren();
 for(const issue of result.issues){const li=document.createElement('li');li.textContent=issue;list.append(li);}
 return result;
}
$('recoveryStatusBtn').addEventListener('click',()=>{refreshRecoveryStatus();$('recoveryStatusDialog').showModal();});
$('recoveryRefreshBtn').addEventListener('click',refreshRecoveryStatus);
$('recoveryCloseBtn').addEventListener('click',()=>$('recoveryStatusDialog').close());
// v40.7: export et import explicites d'une sauvegarde vérifiée, jamais de restauration silencieuse.
const recoveryExportButton=document.createElement('button');
recoveryExportButton.id='recoveryVerifiedExportBtn';recoveryExportButton.type='button';
recoveryExportButton.textContent='Exporter une copie vérifiable';
$('recoveryCloseBtn').before(recoveryExportButton);
recoveryExportButton.addEventListener('click',async()=>{
 try{
  if(!validateGraph(state)){notify('Export refusé : diagramme invalide.');return;}
  const record=await createRecoveryRecord({graph:snapshot(state),zones:declaredZones,sanImport:lastSanImport});
  downloadText('openvisio-recovery-'+Date.now()+'.json',JSON.stringify(record,null,2),'application/json');
  notify('Copie SHA256 préparée : vérifiez le fichier téléchargé.');
 }catch(error){notify('Export de récupération impossible : '+error.message);}
});
const recoveryImportButton=document.createElement('button');
recoveryImportButton.id='recoveryVerifiedImportBtn';recoveryImportButton.type='button';
recoveryImportButton.textContent='Restaurer une copie vérifiable…';
$('recoveryCloseBtn').before(recoveryImportButton);
const recoveryFileInput=document.createElement('input');recoveryFileInput.type='file';
recoveryFileInput.accept='.json,application/json';recoveryFileInput.hidden=true;
$('recoveryStatusDialog').append(recoveryFileInput);
recoveryImportButton.addEventListener('click',()=>recoveryFileInput.click());
recoveryFileInput.addEventListener('change',async()=>{
 const file=recoveryFileInput.files?.[0];recoveryFileInput.value='';if(!file)return;
 try{
  if(file.size>25*1024*1024)throw new Error('Fichier supérieur à 25 Mio');
  const record=JSON.parse(await file.text());
  const result=await verifyRecoveryRecord(record);
  if(!result.valid)throw new Error('Empreinte invalide : '+result.reason);
  const doc=result.diagram;
  const graph=restore(doc.graph);const zones=validateZones(doc.zones);
  const imported=validateSanImport(doc.sanImport);
  if(!window.confirm('Remplacer le diagramme courant par cette sauvegarde vérifiée ? Les modifications non enregistrées seront perdues.'))return;
  saveUndo();Object.assign(state,graph);declaredZones=zones;lastSanImport=imported;
  nativeFileHandle=null;clearMulti();paint();
  savedFingerprint=documentFingerprint();exportPendingVerification=false;refreshDocumentStatus();
  $('recoveryStatusDialog').close();notify('Copie vérifiée restaurée.');
 }catch(error){notify('Restauration refusée : '+error.message);}
});

const recoveryDiagnostic=inspectRecovery(localStorage,DOCUMENT_KEY,{restoreGraph:restore,validateZones,validateSanImport});
if(recoveryDiagnostic.issues.length)console.warn("Diagnostic de récupération OpenVisio",recoveryDiagnostic);
try{
 const raw=localStorage.getItem(DOCUMENT_KEY);
 if(raw){
  const doc=decodeDocument(raw,{restoreGraph:restore,validateZones,validateSanImport});
  state.nodes=doc.graph.nodes;state.edges=doc.graph.edges;
  state.groups=doc.graph.groups||[];state.layers=doc.graph.layers?.length?doc.graph.layers:state.layers;
  state.guides=normalizeGuides(doc.graph.guides??[]);
  declaredZones=doc.zones;lastSanImport=doc.sanImport;
 }
}catch(error){
 console.warn('Document principal illisible : recherche d’une sauvegarde validée',error);
 unifiedDocumentInvalid=true;
 try{
  const backup=recoverBackup(localStorage,DOCUMENT_KEY,{restoreGraph:restore,validateZones,validateSanImport});
  if(backup&&window.confirm('Le document principal est illisible. Restaurer la dernière sauvegarde valide ?')){
   // Conserver le primaire corrompu tant que l’utilisateur n’a pas confirmé.
   localStorage.setItem(DOCUMENT_KEY,backup.raw);
   const doc=backup.document;
   state.nodes=doc.graph.nodes;state.edges=doc.graph.edges;
   state.groups=doc.graph.groups||[];state.layers=doc.graph.layers?.length?doc.graph.layers:state.layers;
   state.guides=normalizeGuides(doc.graph.guides??[]);
   declaredZones=doc.zones;lastSanImport=doc.sanImport;
   unifiedDocumentInvalid=false;
  }
 }catch(recoveryError){console.warn('Récupération impossible : aucune sauvegarde valide',recoveryError);}
}
if(!unifiedDocumentInvalid){unifiedStorageReady=true;persist();}
else {$("saveState").textContent="Sauvegarde suspendue — document à récupérer";}

let previousSanImport=null;
let sanHistory=[];
try{sanHistory=validateSanHistory(JSON.parse(localStorage.getItem('openvisio-san-history-v1')||'[]'));}catch{sanHistory=[];}
function saveSanHistory(){try{localStorage.setItem('openvisio-san-history-v1',JSON.stringify(sanHistory));}catch{notify('Historique SAN : stockage navigateur indisponible');}}
function refreshSanCockpit(){
 const compliance=compareFabricSnapshots(sanHistory,{maxAgeDays:Number($("sanMaxAge").value)||30,requireBothFabrics:$("sanRequireBoth").checked});
 $("sanComplianceSummary").textContent=`Score indicatif ${compliance.score}/100 · Zones A/B ${compliance.zonesByFabric.A}/${compliance.zonesByFabric.B} · Zonesets A/B ${compliance.setsByFabric.A}/${compliance.setsByFabric.B} · ${compliance.issues.length} alertes`;
 const complianceRows=$("sanComplianceAlerts");complianceRows.replaceChildren();
 for(const issue of compliance.issues){const li=document.createElement('li');li.textContent=`${issue.severity.toUpperCase()} · ${issue.fabric} · ${issue.code} · ${issue.detail}`;complianceRows.append(li);}
 if(!compliance.issues.length){const li=document.createElement('li');li.textContent='Aucune anomalie détectée par les règles activées.';complianceRows.append(li);}

 const fabric=$('sanVisualFabric').value, severity=$('sanVisualSeverity').value;
 const model=visualAuditModel(sanHistory,{fabric,severity,left:$('sanVisualLeft').value||null,right:$('sanVisualRight').value||null,maxAgeDays:Number($('sanMaxAge').value)||30,requireBothFabrics:$('sanRequireBoth').checked});
 for(const [id,chosen] of [['sanVisualLeft',model.left],['sanVisualRight',model.right]]){
  const select=$(id),prior=select.value;select.replaceChildren();const auto=document.createElement('option');auto.value='';auto.textContent='Automatique';select.append(auto);
  for(const entry of model.entries){const option=document.createElement('option');option.value=entry.id;option.textContent=`${entry.at} · ${entry.fabric} · ${entry.label}`;select.append(option);}
  select.value=model.entries.some(e=>e.id===prior)?prior:'';
 }
 const scores=model.timeline.map(t=>t.score);
 $('sanVisualChart').setAttribute('points',sparklinePoints(scores));
 $('sanVisualSummary').textContent=`${model.changes.length} écarts affichés · ${model.timeline.length} points de conformité`;
 const diffRows=$('sanVisualDiffRows');diffRows.replaceChildren();
 for(const change of model.changes){const tr=document.createElement('tr');tr.dataset.severity=change.severity;for(const value of [change.key,change.status,change.severity]){const td=document.createElement('td');td.textContent=value;tr.append(td);}diffRows.append(tr);}
 const summary=cockpitSummary(sanHistory,readZones());
 $("sanCockpitSummary").textContent=`${summary.snapshots} imports · Fabric A : ${summary.fabrics.A} · Fabric B : ${summary.fabrics.B} · ${summary.changed} différences (2 derniers imports) · ${summary.alerts.length} alertes`;
 const rows=$("sanCockpitRows");rows.replaceChildren();
 for(const item of [...sanHistory].reverse()){
  const tr=document.createElement('tr');for(const value of [item.at,item.data.vendor,item.data.fabric,item.data.zonesets.length,item.label]){const td=document.createElement('td');td.textContent=value;tr.append(td);}rows.append(tr);
 }
 const alerts=$("sanCockpitAlerts");alerts.replaceChildren();
 for(const alert of summary.alerts.slice(-30)){const li=document.createElement('li');li.textContent=`${alert.fabric} · ${alert.code} · ${alert.detail}`;alerts.append(li);}
 if(!summary.alerts.length){const li=document.createElement('li');li.textContent='Aucune zone manquante dans les zonesets importés.';alerts.append(li);}
}
for(const id of ['sanVisualFabric','sanVisualSeverity','sanVisualLeft','sanVisualRight'])$(id).addEventListener('change',refreshSanCockpit);
$("sanMaxAge").addEventListener('change',refreshSanCockpit);
$("sanRequireBoth").addEventListener('change',refreshSanCockpit);
$("sanComplianceCsv").addEventListener('click',()=>{const content=complianceCsv(compareFabricSnapshots(sanHistory,{maxAgeDays:Number($("sanMaxAge").value)||30,requireBothFabrics:$("sanRequireBoth").checked}));const url=URL.createObjectURL(new Blob([content],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='openvisio-conformite-san.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('sanVisualHtml').addEventListener('click',()=>{
 const content=comparisonHtmlReport(sanHistory,{fabric:$('sanVisualFabric').value,severity:$('sanVisualSeverity').value,left:$('sanVisualLeft').value||null,right:$('sanVisualRight').value||null,maxAgeDays:Number($('sanMaxAge').value)||30,requireBothFabrics:$('sanRequireBoth').checked});
 const url=URL.createObjectURL(new Blob([content],{type:'text/html;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='openvisio-comparaison-san.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
$("sanComplianceHtml").addEventListener('click',()=>{const content=complianceHtmlReport(sanHistory,{maxAgeDays:Number($("sanMaxAge").value)||30,requireBothFabrics:$("sanRequireBoth").checked});const url=URL.createObjectURL(new Blob([content],{type:'text/html;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='openvisio-audit-conformite-san.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$("sanCockpitBtn").addEventListener('click',()=>{refreshSanCockpit();$("sanCockpitDialog").showModal();});
$("closeSanCockpit").addEventListener('click',()=>$("sanCockpitDialog").close());
$("sanCockpitCsv").addEventListener('click',()=>{
 const content=cockpitCsv(cockpitSummary(sanHistory,readZones()));const url=URL.createObjectURL(new Blob([content],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='openvisio-cockpit-san.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
function renderSanClassification(parsed){
 const target=$("sanRoleRows");target.replaceChildren();
 const wwpns=[...new Set(parsed.zones.flatMap(z=>z.members))].sort();
 for(const w of wwpns){
  const tr=document.createElement('tr');const name=document.createElement('td');name.textContent=w;
  const aliases=document.createElement('td');aliases.textContent=Object.entries(parsed.aliases).filter(([,v])=>v.some(x=>x.replace(/[^0-9a-f]/gi,'').toLowerCase()===w.replace(/:/g,'').toLowerCase())).map(([k])=>k).join(', ');
  const role=document.createElement('td');const select=document.createElement('select');select.dataset.wwpn=w;
  for(const [value,label] of [['','Non classé'],['initiator','Initiateur'],['target','Cible']]){const opt=document.createElement('option');opt.value=value;opt.textContent=label;select.append(opt);}
  role.append(select);tr.append(name,aliases,role);target.append(tr);
 }
 $("sanRoleWarnings").textContent=parsed.warnings.join(' ; ')||'Aucun avertissement de parsing.';
}
$("cancelSanRolesBtn").addEventListener('click',()=>{$("sanRoleDialog").close();pendingSanImport=null;});
$("confirmSanRolesBtn").addEventListener('click',()=>{
 try{
  if(!pendingSanImport)throw Error('Aucun import en cours');
  const assignments={};const roleByWwpn=Object.fromEntries([...$("sanRoleRows").querySelectorAll('select')].map(el=>[el.dataset.wwpn,el.value]));
  for(const z of pendingSanImport.zones){assignments[z.name]=Object.fromEntries(z.members.map(w=>[w,roleByWwpn[w]]));}
  const zones=assignSanRoles(pendingSanImport,assignments);
  const diffs=compareSanZones(zones,declaredZones);zoningEditor.value=JSON.stringify(zones,null,2);
  $("sanRoleDialog").close();pendingSanImport=null;$("zoningDialog").showModal();
  notify(`Import préparé : ${diffs.filter(x=>x.status==='new').length} nouvelles zones, ${diffs.filter(x=>x.status==='changed').length} modifiées. Vérifiez puis validez le JSON.`);
 }catch(err){notify('Classification invalide : '+err.message);}
});
$("importSanConfigBtn").addEventListener('click',()=>$("sanConfigFile").click());
$("sanConfigFile").addEventListener('change',async ev=>{
 const file=ev.target.files?.[0];if(!file)return;
 try{
  if(file.size>2_000_000)throw Error('Fichier supérieur à 2 Mo');
  const parsed=parseSanConfig(await file.text(),$("sanVendor").value,$("sanFabric").value);
  pendingSanImport=parsed;previousSanImport=lastSanImport;const nextSanImport=validateSanImport(parsed);if(JSON.stringify(nextSanImport)!==JSON.stringify(lastSanImport))saveUndo();lastSanImport=nextSanImport;persistSanImport();sanHistory=appendSanSnapshot(sanHistory,lastSanImport,{label:file.name});saveSanHistory();
  renderSanClassification(parsed);
  $("sanRoleDialog").showModal();
  notify(`${parsed.zones.length} zones, ${parsed.zonesets.length} zonesets, ${parsed.activeConfigurations.length} activation(s) déclarées, ${Object.keys(parsed.aliases).length} alias ; ${parsed.warnings.length} avertissement(s).`);
 }catch(err){notify('Import SAN refusé : '+err.message);}
 ev.target.value='';
});
$("editZoningBtn").addEventListener('click',()=>{zoningEditor.value=JSON.stringify(declaredZones,null,2);$("zoningDialog").showModal();});
$("saveZoningBtn").addEventListener('click',()=>{
 try{const data=JSON.parse(zoningEditor.value);if(!Array.isArray(data)||data.length>500)throw Error('Un tableau de 500 zones maximum est attendu');const changed=commitZoningUpdate(declaredZones,data,saveUndo,zones=>{declaredZones=zones;persistZones();});$("zoningDialog").close();if(changed){paint();showWiringReport();}notify(changed?'Zoning déclaré enregistré (annulable).':'Zoning inchangé.');}
 catch(err){notify('Zoning invalide : '+err.message);}
});
$("closeZoningBtn").addEventListener('click',()=>$("zoningDialog").close());
const wiringDialog=$("wiringDialog");
function downloadWiringCsv(kind){
 const report=buildWiringReport(state.nodes,state.edges,readZones());
 const blob=new Blob([reportCsv(report,kind)],{type:'text/csv;charset=utf-8'});
 const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`openvisio-${kind}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 notify('Export CSV '+kind+' préparé.');
}
function showWiringReport(){
 const report=buildWiringReport(state.nodes,state.edges,readZones());
 report.diagnostics.push(...detectCableCrossings(state.nodes,state.edges,renderedCableRoutes(svg)));
 // Analyse du trajet SVG effectif ; aucune mutation ni correction implicite.
 const visibleRoutes=new Map([...renderedCableRoutes(svg)].map(([id,points])=>[id,{points}]));
 const denseAnalysis=analyzeDenseRouteBundles(visibleRoutes);
 const topology=denseAnalysis.segments>1500?null:diagnoseRouteTopology(visibleRoutes);
 const geometricFindings=denseAnalysis.segments>1500?{findings:denseAnalysis.issues,truncated:!denseAnalysis.complete||denseAnalysis.findingsLimited}:locateRouteAnomalies(visibleRoutes);
 const topologySummary=$("wiringTopologySummary");
 topologySummary.textContent=buildDenseTopologySummary(denseAnalysis,topology);
 topologySummary.title='Analyse spatiale en lecture seule ; limites de segments, de paires et de résultats explicites.';
 if(lastSanImport){report.zonesetAudit=auditSanZonesets(lastSanImport,readZones());}
 const summary=$("wiringSummary");summary.textContent=`${report.zonesetAudit?`${report.zonesetAudit.summary.zonesets} zonesets · ${report.zonesetAudit.summary.missing} écarts · `:""}${report.inventory.length} ports · ${report.counts.free} libres · ${report.counts.used} occupés · ${report.counts.conflict} en conflit · ${report.diagnostics.length} alertes`;
 const body=$("wiringTableBody");body.replaceChildren();
 for(const p of report.inventory){const tr=document.createElement('tr');for(const val of [p.nodeTitle,p.port,p.family,p.status,p.edgeIds.join(', ')]){const td=document.createElement('td');td.textContent=val;tr.append(td);}body.append(tr);}
 const fabric=$("fabricMatrixBody");fabric.replaceChildren();
 for(const r of report.matrix){const tr=document.createElement('tr');for(const val of [r.nodeTitle,r.hasA?'✓':'—',r.hasB?'✓':'—',r.redundant?'Oui':'Non']){const td=document.createElement('td');td.textContent=val;tr.append(td);}fabric.append(tr);}
 const sanBody=$("sanPathBody");sanBody.replaceChildren();
 for(const r of report.sanPaths){const tr=document.createElement('tr');for(const val of [r.sourceName,r.targetName,r.hasA?'✓':'—',r.hasB?'✓':'—',r.independent?'Oui':'Non',r.spof.join(', ')||'—',r.status]){const td=document.createElement('td');td.textContent=val;tr.append(td);}sanBody.append(tr);}
 svg.querySelector('#routePreviewOverlay')?.remove();
 const previewArea=$("wiringRoutePreview");previewArea.replaceChildren();
 const previewState={proposal:null};
 const clearPreview=()=>{previewState.proposal=null;previewArea.replaceChildren();svg.querySelector('#routePreviewOverlay')?.remove();};
 const showPreview=edge=>{
  clearPreview();
  const proposal=proposeRouteOffset(edge,state.nodes,visibleRoutes);
  const text=document.createElement('p');text.textContent=proposal.status==='preview'?`Aperçu ${edge.id} : chevauchement ${proposal.before.overlap} → ${proposal.after.overlap}, croisements ${proposal.before.crossings} → ${proposal.after.crossings}, collisions ${proposal.before.collisions} → ${proposal.after.collisions}. Décalage proposé : ${proposal.offset}.`:(proposal.reason||'Aucune amélioration sûre détectée.');previewArea.append(text);
  if(proposal.status!=='preview')return;
  previewState.proposal=proposal;
  const geometry=previewRouteGeometry(proposal,visibleRoutes.get(String(edge.id))?.points);
  const ns='http://www.w3.org/2000/svg';
  const overlay=document.createElementNS(ns,'g');overlay.setAttribute('id','routePreviewOverlay');overlay.setAttribute('pointer-events','none');overlay.setAttribute('aria-label','Aperçu temporaire du routage');
  for(const [key,color,dash] of [['before','#dc2626','8 6'],['after','#16a34a','']]){
   const path=document.createElementNS(ns,'path');path.setAttribute('d',geometry[key]);path.setAttribute('fill','none');path.setAttribute('stroke',color);path.setAttribute('stroke-width','4');path.setAttribute('stroke-linejoin','round');path.setAttribute('stroke-dasharray',dash);path.setAttribute('opacity','.9');overlay.append(path);
  }
  svg.append(overlay);
  const legend=document.createElement('p');legend.textContent='Sur le diagramme : rouge pointillé = tracé actuel ; vert continu = tracé proposé. Fermer le panneau annule l’aperçu.';previewArea.append(legend);
  const apply=document.createElement('button');apply.type='button';apply.textContent='Appliquer (annulable)';
  apply.addEventListener('click',()=>{
   if(previewState.proposal!==proposal)return;
   const current=state.edges.find(e=>String(e.id)===proposal.edgeId);
   if(!current||current.waypoints?.length||!['orthogonal',undefined,null,''].includes(current.style)){notify('Connexion modifiée : aperçu annulé.');clearPreview();return;}
   saveUndo();applyRouteOffset(current,proposal);clearPreview();paint();wiringDialog.close();notify('Routage appliqué ; Ctrl+Z pour annuler.');
  });previewArea.append(apply);
  const cancel=document.createElement('button');cancel.type='button';cancel.textContent='Annuler aperçu';cancel.addEventListener('click',clearPreview);previewArea.append(' ',cancel);
 };
 wiringDialog.addEventListener('close',clearPreview,{once:true});
 const nativeAuditHost=$("sanNativeGeometryAudit");nativeAuditHost.replaceChildren();
 const nativeAuditSummary=$("sanNativeGeometrySummary");
 const visibleNodes=state.nodes.filter(n=>visibleNode(state,n));
 const visibleNodeIds=new Set(visibleNodes.map(n=>n.id));
 const auditedEdges=state.edges.filter(e=>visibleNodeIds.has(e.from)&&visibleNodeIds.has(e.to));
 const routePoints=Object.fromEntries([...renderedCableRoutes(svg)].filter(([id])=>auditedEdges.some(e=>String(e.id)===String(id))));
 // Diagnostic du chemin effectivement affiché, sans modifier le document.
 const nativeAudit=auditedEdges.length>250||visibleNodes.length>500
  ?null:auditSanRoutes(visibleNodes,auditedEdges,routePoints);
 nativeAuditSummary.textContent=nativeAudit
  ?`${nativeAudit.checked} tracés examinés · ${nativeAudit.findings.length} anomalies · contrôle en lecture seule`
  :'Audit géométrique détaillé limité à 250 liens et 500 équipements ; aucun résultat partiel présenté comme complet.';
 for(const finding of (nativeAudit?.findings||[]).slice(0,80)){
  const item=document.createElement('li');
  item.textContent=`${finding.kind} · ${finding.edge}${finding.node?' · obstacle '+finding.node:''}${finding.segment!==undefined?' · segment '+finding.segment:''}`;
  const edge=state.edges.find(e=>String(e.id)===String(finding.edge));
  if(edge){const focus=document.createElement('button');focus.type='button';focus.textContent='Localiser';focus.addEventListener('click',()=>{wiringDialog.close();select(edge.id);svg.focus?.();notify('Anomalie géométrique : '+finding.kind);});item.append(' ',focus);}
  nativeAuditHost.append(item);
 }
 if(nativeAudit?.findings.length>80){const item=document.createElement('li');item.textContent=`${nativeAudit.findings.length-80} autres anomalies non affichées`;nativeAuditHost.append(item);}
 if(nativeAudit?.pass){const item=document.createElement('li');item.textContent='Aucune anomalie détectée dans les tracés examinés.';nativeAuditHost.append(item);}
 const existingFabricAudit=auditExistingFabricClearance(auditedEdges,visibleRoutes,{minimum:8,limit:250});
 const existingFabricSummary=document.createElement('p');
 existingFabricSummary.textContent=`Fabrics A/B existantes : ${existingFabricAudit.findings.length} proximité(s) inférieure(s) à 8 unités SVG · ${existingFabricAudit.skipped.length} paire(s) non vérifiable(s)${existingFabricAudit.truncated?' · analyse tronquée':''}. Audit en lecture seule.`;
 nativeAuditHost.append(existingFabricSummary);
 for(const issue of existingFabricAudit.findings.slice(0,30)){
  const item=document.createElement('li');item.textContent=`Fabrics ${issue.fabricA}/${issue.fabricB} : ${issue.a} / ${issue.b} · distance ${issue.clearance.toFixed(1)} / ${issue.minimum}`;
  const focus=document.createElement('button');focus.type='button';focus.textContent='Localiser';focus.addEventListener('click',()=>{wiringDialog.close();select(issue.a);svg.focus?.();});item.append(' ',focus);nativeAuditHost.append(item);
 }
 const batchHost=$("wiringBatchCorrections");batchHost.replaceChildren();
 const alternateTitle=document.createElement('p');alternateTitle.textContent='Itinéraires alternatifs (aperçu puis validation explicite) :';batchHost.append(alternateTitle);
 let alternateCount=0;
 for(const candidate of auditedEdges.slice(0,12)){
  try{const alternative=proposeSanAlternate(candidate,state.nodes,visibleRoutes,auditedEdges);
   if(alternative.status!=='preview')continue;
   alternateCount++;
   const item=document.createElement('p');item.textContent=`${candidate.id} : trajet ${alternative.before.length.toFixed(0)} → ${alternative.after.length.toFixed(0)} unités · grille ${alternative.step} · collisions ${alternative.before.collisions} → ${alternative.after.collisions}. `;
   const button=document.createElement('button');button.type='button';button.textContent='Voir le trajet';
   button.addEventListener('click',()=>{
    clearPreview();const ns='http://www.w3.org/2000/svg',overlay=document.createElementNS(ns,'g');overlay.id='routePreviewOverlay';overlay.setAttribute('pointer-events','none');
    for(const [points,color,dash] of [[visibleRoutes.get(String(candidate.id)).points,'#dc2626','7 5'],[alternative.points,'#16a34a','']]){
     const path=document.createElementNS(ns,'path');path.setAttribute('d',points.map((pt,i)=>`${i?'L':'M'} ${pt.x} ${pt.y}`).join(' '));path.setAttribute('stroke',color);path.setAttribute('stroke-width','4');path.setAttribute('stroke-dasharray',dash);path.setAttribute('fill','none');overlay.append(path);
    }svg.append(overlay);
    const message=document.createElement('p');message.textContent='Rouge : existant ; vert : itinéraire alternatif. Simulation uniquement : aucun changement enregistré.';previewArea.append(message);
   });item.append(button);
   const apply=document.createElement('button');apply.type='button';apply.textContent='Valider cet itinéraire (Ctrl+Z)';
   apply.addEventListener('click',()=>{try{
    const live=state.edges.find(e=>String(e.id)===String(candidate.id));
    if(!live)throw Error('Connexion supprimée');
    const plan=prepareAlternateCommit(alternative,live,state.nodes,state.edges,visibleRoutes);
    const draft={...live,waypoints:live.waypoints?.map(p=>({...p}))};
    commitAlternateRoute(draft,plan,state.nodes,state.edges,visibleRoutes);
    const verification=verifyCommittedAlternate(draft,plan,state.nodes,state.edges,visibleRoutes);
    const lifecycle=qualifyAlternateLifecycle(state,plan,visibleRoutes);
    if(!lifecycle.qualified)throw Error('Recette transactionnelle échouée');
    saveUndo();live.waypoints=draft.waypoints;clearPreview();paint();wiringDialog.close();notify(`Itinéraire vérifié et appliqué : ${verification.before.length.toFixed(0)} → ${verification.after.length.toFixed(0)} unités ; Ctrl+Z pour annuler.`);
   }catch(error){notify('Application refusée : '+error.message);}});
   item.append(' ',apply);batchHost.append(item);
  }catch(error){const warning=document.createElement('p');warning.textContent=`Alternative ${candidate.id} indisponible : ${error.message}`;batchHost.append(warning);}
 }
 if(!alternateCount){const message=document.createElement('p');message.textContent='Aucun itinéraire alternatif améliorant les critères conservateurs sur les 12 premiers liens.';batchHost.append(message);}

 const batch=prepareRouteBatch(auditedEdges,state.nodes,visibleRoutes,{limit:30,fabricClearance:8});
 const batchSummary=document.createElement('p');batchSummary.textContent=`${batch.proposals.length} propositions · ${batch.conflicts.length} conflits entre propositions · ${batch.skipped.length} non éligibles${batch.truncated?' · analyse limitée à 30 liens':''}. Aucune correction automatique.`;batchHost.append(batchSummary);
 const optimization=optimizeRouteBatch(batch);
 const globalSummary=document.createElement('p');globalSummary.textContent=`Optimisation globale : ${optimization.selectedIds.length} corrections compatibles · gain estimé ${optimization.estimatedGain} · ${optimization.excludedIds.length} propositions écartées. Mode ${optimization.mode} · ${optimization.exactComponents} groupes exacts / ${optimization.heuristicComponents} groupes heuristiques. Prévisualisation uniquement, validation humaine obligatoire.`;batchHost.append(globalSummary);
 const showBatchConflictPreview=(edgeIds,{compare=false}={})=>{
  clearPreview();
  const ns='http://www.w3.org/2000/svg';
  const overlay=document.createElementNS(ns,'g');overlay.id='routePreviewOverlay';overlay.setAttribute('pointer-events','none');
  let rendered=0,alternatives=0;
  for(const id of edgeIds){
   const route=visibleRoutes.get(String(id));
   if(!route?.points?.length)continue;
   const path=document.createElementNS(ns,'path');
   path.setAttribute('d',route.points.map((pt,i)=>`${i?'L':'M'} ${pt.x} ${pt.y}`).join(' '));
   path.setAttribute('stroke','#e11d48');path.setAttribute('stroke-width','6');path.setAttribute('stroke-opacity','0.85');path.setAttribute('fill','none');
   overlay.append(path);rendered++;
   if(compare){
    const proposal=batch.proposals.find(p=>p.edgeId===id);
    const edge=auditedEdges.find(e=>String(e.id)===id);
    if(!proposal||!edge)continue;
    try{
     const candidate={...edge,offset:proposal.offset};
     const a=state.nodes.find(n=>n.id===candidate.from),b=state.nodes.find(n=>n.id===candidate.to);
     if(!a||!b)continue;
     const proposed=routeEdge(a,b,candidate.style||'orthogonal',candidate.offset,candidate.fromPort||'auto',candidate.toPort||'auto');
     if(!proposed?.points?.length)continue;
     const after=document.createElementNS(ns,'path');
     after.setAttribute('d',proposed.points.map((pt,i)=>`${i?'L':'M'} ${pt.x} ${pt.y}`).join(' '));
     after.setAttribute('stroke','#16a34a');after.setAttribute('stroke-width','4');after.setAttribute('stroke-dasharray','9 5');after.setAttribute('fill','none');
     overlay.append(after);alternatives++;
    }catch{/* An unavailable candidate must never prevent the original preview. */}
   }
  }
  if(rendered){svg.append(overlay);const message=document.createElement('p');message.textContent=compare?`${rendered} route(s) avant (rose) · ${alternatives} proposition(s) après (vert pointillé) — aperçu sans modification.`:`${rendered} connexion(s) surlignée(s) en rose — aperçu sans modification.`;previewArea.append(message);}
  else notify('Aucun tracé disponible pour ces connexions.');
 };
 const focusBatchConflictGroup=(edgeIds,{fit=false}={})=>{
  const paths=[...svg.querySelectorAll('[data-edge-id]')].filter(el=>edgeIds.includes(el.getAttribute('data-edge-id')));
  if(!paths.length){notify('Aucune connexion visible à localiser dans ce groupe.');return false;}
  const viewport=$('canvasViewport');
  const bounds=paths.map(el=>el.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0);
  if(!bounds.length){notify('Connexions hors de la zone visible.');return false;}
  const left=Math.min(...bounds.map(r=>r.left)),top=Math.min(...bounds.map(r=>r.top));
  const right=Math.max(...bounds.map(r=>r.right)),bottom=Math.max(...bounds.map(r=>r.bottom));
  if(fit){const z=fitConflictGroupZoom(viewport.getBoundingClientRect(),{width:right-left,height:bottom-top},state.zoom);if(z!==null)setZoom(z);}
  const updated=paths.map(el=>el.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0);
  const newLeft=Math.min(...updated.map(r=>r.left)),newTop=Math.min(...updated.map(r=>r.top));
  const newRight=Math.max(...updated.map(r=>r.right)),newBottom=Math.max(...updated.map(r=>r.bottom));
  const target=edgeViewportTarget(viewport.getBoundingClientRect(),{left:newLeft,top:newTop,right:newRight,bottom:newBottom,width:newRight-newLeft,height:newBottom-newTop},viewport.scrollLeft,viewport.scrollTop);
  if(target)viewport.scrollTo?.({...target,behavior:'smooth'});
  notify(`${paths.length} connexion(s) localisée(s) dans le groupe SAN.`);return true;
 };
 const checkboxes=new Map();
 for(const p of batch.proposals){const label=document.createElement('label');label.style.display='block';const cb=document.createElement('input');cb.type='checkbox';cb.checked=optimization.selectedIds.includes(p.edgeId);checkboxes.set(p.edgeId,cb);label.append(cb,document.createTextNode(` ${p.edgeId} · décalage ${p.offset} · score ${p.before.score} → ${p.after.score}`));batchHost.append(label);}
 const conflictPanel=document.createElement('section');conflictPanel.setAttribute('aria-label','Groupes de conflits SAN');batchHost.append(conflictPanel);
 const refreshConflictPanel=()=>{
  const ids=new Set([...checkboxes].filter(([,cb])=>cb.checked).map(([id])=>id));
  const summary=describeRouteBatchConflicts(batch,ids);conflictPanel.replaceChildren();
  const status=document.createElement('p');status.setAttribute('role','status');status.textContent=`Sélection : ${summary.selectedCount} liens · ${summary.groups.length} groupes · ${summary.activeConflicts.length} conflits actifs ${summary.valid?'— validation possible':'— corriger avant validation'}`;conflictPanel.append(status);
  for(const group of summary.groups){
   const details=document.createElement('details');details.open=group.conflicts>0&&group.id<=3;
   const heading=document.createElement('summary');heading.textContent=`Groupe ${group.id} · ${group.edgeIds.length} liens · ${group.conflicts} conflits · ${group.selected} sélectionnés`;details.append(heading);
   const lines=document.createElement('p');lines.textContent=`Connexions : ${group.edgeIds.join(', ')}`;details.append(lines);
   for(const c of summary.conflicts.filter(c=>group.edgeIds.includes(c.a))){const line=document.createElement('p');line.textContent=`${c.active?'⚠ Conflit actif':'✓ Compatible avec la sélection'} : ${c.a} ↔ ${c.b}${c.crossFabric?' · Fabric A/B':''}`;details.append(line);}
   const actions=document.createElement('div');
   const highlight=document.createElement('button');highlight.type='button';highlight.textContent='Surligner ce groupe';
   highlight.addEventListener('click',()=>showBatchConflictPreview(group.edgeIds));actions.append(highlight);
   const selectGroup=document.createElement('button');selectGroup.type='button';selectGroup.textContent='Sélectionner les liens du groupe';
   selectGroup.addEventListener('click',()=>{for(const id of group.edgeIds){const cb=checkboxes.get(id);if(cb)cb.checked=true;}refreshConflictPanel();});actions.append(selectGroup);
   const clearGroup=document.createElement('button');clearGroup.type='button';clearGroup.textContent='Désélectionner ce groupe';
   clearGroup.addEventListener('click',()=>{for(const id of group.edgeIds){const cb=checkboxes.get(id);if(cb)cb.checked=false;}refreshConflictPanel();});actions.append(clearGroup);
   const locate=document.createElement('button');locate.type='button';locate.textContent='Cadrer le groupe';
   locate.addEventListener('click',()=>{showBatchConflictPreview(group.edgeIds);focusBatchConflictGroup(group.edgeIds,{fit:true});});actions.append(locate);
   const compare=document.createElement('button');compare.type='button';compare.textContent='Comparer avant / après';
   compare.addEventListener('click',()=>showBatchConflictPreview(group.edgeIds,{compare:true}));actions.append(compare);
   const previous=document.createElement('button');previous.type='button';previous.textContent='← Groupe précédent';previous.disabled=group.id===summary.groups[0]?.id;
   previous.addEventListener('click',()=>{const index=summary.groups.findIndex(g=>g.id===group.id);const target=summary.groups[index-1];if(target){showBatchConflictPreview(target.edgeIds,{compare:true});focusBatchConflictGroup(target.edgeIds,{fit:true});}});actions.append(previous);
   const next=document.createElement('button');next.type='button';next.textContent='Groupe suivant →';next.disabled=group.id===summary.groups.at(-1)?.id;
   next.addEventListener('click',()=>{const index=summary.groups.findIndex(g=>g.id===group.id);const target=summary.groups[index+1];if(target){showBatchConflictPreview(target.edgeIds,{compare:true});focusBatchConflictGroup(target.edgeIds,{fit:true});}});actions.append(next);
   const gain=document.createElement('p');const measures=summarizeSanConflictGroup(group,batch.proposals,summary.conflicts,ids);gain.textContent=`Gain estimé du groupe : ${measures.gain.toFixed(2)} points · ${measures.selected} corrections sélectionnées · ${measures.activeConflicts} conflits actifs.`;details.append(gain);
   const metrics=document.createElement('p');metrics.textContent=`Séparation Fabric A/B : ${measures.fabricConflicts} conflit(s) potentiel(s) · ${measures.activeFabricConflicts} actif(s) · ${measures.valid?'sélection compatible':'validation bloquée'}.`;details.append(metrics);
   details.append(actions);
   conflictPanel.append(details);
  }
  return summary.valid;
 };
 for(const cb of checkboxes.values())cb.addEventListener('change',refreshConflictPanel);
 refreshConflictPanel();
 if(batch.proposals.length){const button=document.createElement('button');button.type='button';button.textContent='Valider les corrections sélectionnées (Ctrl+Z pour annuler)';button.addEventListener('click',()=>{
  try{const ids=new Set([...checkboxes].filter(([,cb])=>cb.checked).map(([id])=>id));
   if(!describeRouteBatchConflicts(batch,ids).valid)throw Error('Conflits actifs dans la sélection');
   if(batchFingerprint(auditedEdges,state.nodes)!==batch.fingerprint)throw Error('Topologie modifiée depuis l’aperçu');
   // Vérification sur copie avant enregistrement de l’unique état Undo.
   const draft=auditedEdges.map(e=>({...e,waypoints:e.waypoints?[...e.waypoints]:undefined}));
   const changes=commitRouteBatch(draft,state.nodes,batch,ids);
   saveUndo();for(const c of changes){const edge=state.edges.find(e=>String(e.id)===c.edgeId);edge.offset=c.after;}
   clearPreview();paint();wiringDialog.close();notify(`${changes.length} connexions corrigées ; Ctrl+Z pour annuler le lot.`);
  }catch(error){notify(`Correction refusée : ${error.message}`);}
 });batchHost.append(button);}
 const geometricList=$("wiringGeometryFindings");geometricList.replaceChildren();
 for(const finding of geometricFindings.findings){const li=document.createElement('li');const edge=state.edges.find(e=>String(e.id)===finding.edgeId);
  li.textContent=`${finding.code==='invalid-route'?'Tracé invalide':finding.code==='route-overlap'?'Segments superposés':'Croisement'} : ${finding.edgeId}${finding.otherEdgeId?' / '+finding.otherEdgeId:''}`;
  if(edge){const button=document.createElement('button');button.type='button';button.textContent='Localiser';button.addEventListener('click',()=>{wiringDialog.close();select(edge.id);svg.focus?.();notify(`Connexion ${edge.id} sélectionnée.`);});li.append(' ',button);const preview=document.createElement('button');preview.type='button';preview.textContent='Aperçu correction';preview.addEventListener('click',()=>showPreview(edge));li.append(' ',preview);}
  geometricList.append(li);
 }
 if(geometricFindings.truncated){const li=document.createElement('li');li.textContent='Analyse limitée : certaines anomalies ne sont pas affichées.';geometricList.append(li);}
 if(!geometricFindings.findings.length){const li=document.createElement('li');li.textContent='Aucune anomalie géométrique localisable dans les limites du contrôle.';geometricList.append(li);}
 const warnings=$("wiringWarnings");
 const counts=summarizeDiagnostics(report.diagnostics);
 $("wiringSeveritySummary").textContent=`Critiques : ${counts.critical} · Avertissements : ${counts.warning} · Informations : ${counts.info}`;
 let findingIndex=-1;
 let navigable=[];
 const locateFinding=(edge)=>{
  wiringDialog.close();select(edge.id);
  const group=[...svg.querySelectorAll('[data-edge-id]')].find(el=>el.getAttribute('data-edge-id')===edge.id);
  if(group){
   group.classList.add('wiring-located');
   const viewport=$('canvasViewport');
   const target=edgeViewportTarget(viewport.getBoundingClientRect(),group.getBoundingClientRect(),viewport.scrollLeft,viewport.scrollTop);
   if(target)viewport.scrollTo?.({...target,behavior:'smooth'});
  }
  svg.focus?.();notify(`Connexion ${edge.id} sélectionnée.`);
 };
 const renderFindings=()=>{
  warnings.replaceChildren();navigable=[];findingIndex=-1;
  const selected=filterDiagnostics(report.diagnostics,$("wiringSeverityFilter").value);
  for(const w of selected){
   const li=document.createElement('li');
   li.textContent=`[${diagnosticLevel(w.code).toUpperCase()}] ${w.edgeId}: ${diagnosticDescription(w)}${w.port?' ('+w.port+')':''}`;
   li.dataset.severity=diagnosticLevel(w.code);
   const edge=resolveDiagnosticEdge(w,state.edges);
   if(edge){
    const button=document.createElement('button');
    button.type='button';button.className='wiring-locate';
    button.textContent='Voir la connexion';
    button.setAttribute('aria-label',`Sélectionner la connexion ${edge.id} sur le canevas`);
    button.addEventListener('click',()=>{
     locateFinding(edge);
    });
    navigable.push(edge);li.append(' ',button);
   }
   warnings.append(li);
  }
  $('wiringPreviousFinding').disabled=navigable.length===0;
  $('wiringNextFinding').disabled=navigable.length===0;
  if(!selected.length){const li=document.createElement('li');li.textContent=report.diagnostics.length?'Aucune anomalie pour ce niveau.':'Aucune anomalie détectée par les règles actuelles.';warnings.append(li);}
 };
 const stepFinding=(delta)=>{
  findingIndex=nextFindingIndex(navigable.length,findingIndex,delta);
  if(findingIndex>=0)locateFinding(navigable[findingIndex]);
 };
 $('wiringPreviousFinding').onclick=()=>stepFinding(-1);
 $('wiringNextFinding').onclick=()=>stepFinding(1);
 $("wiringSeverityFilter").onchange=renderFindings;
 renderFindings();
 wiringDialog.showModal();
}
$("wiringBtn").addEventListener('click',showWiringReport);
$("closeWiring").addEventListener('click',()=>wiringDialog.close());
document.querySelectorAll('[data-wiring-export]').forEach(b=>b.addEventListener('click',()=>downloadWiringCsv(b.dataset.wiringExport)));

// v12.2 : export HTML autonome imprimable, sans dépendance externe.
$("wiringHtmlBtn").addEventListener('click',()=>{
 const report=buildWiringReport(state.nodes,state.edges,readZones());if(lastSanImport)report.zonesetAudit=auditSanZonesets(lastSanImport,readZones());const html=reportHtml(report);
 const url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'}));
 const a=document.createElement('a');a.href=url;a.download='openvisio-audit-san.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 notify('Rapport HTML prêt.');
});

// v12.9 — comparaison entre deux imports successifs, export CSV des écarts.
$("sanDiffCsvBtn").addEventListener('click',()=>{
 const rows=compareSanImports(previousSanImport,lastSanImport);
 const blob=new Blob([sanDiffCsv(rows)],{type:'text/csv;charset=utf-8'});
 const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='openvisio-ecarts-zonesets.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 notify(`${rows.filter(r=>r.status!=='unchanged').length} écart(s) de zonesets exportés.`);
});

// Comparaison de deux versions de diagramme, sans modification du canevas actif.
{
 const dialog=$('topologyDiffDialog'),inputs=[$('topologyBefore'),$('topologyAfter')];let current=null,overlay=null,impact=null,ports=null,apps=null,matrix=null,chains=null,relations=null,zoningCorrelation=null,sanAccess=null;
 $('topologyDiffBtn').addEventListener('click',()=>dialog.showModal());
 let failureResult=null;const failureSelect=$('failureTarget');
 let spofResult=null;
 $('spofRun').addEventListener('click',async()=>{try{const file=$('topologyAfter').files[0];if(!file)throw new Error('Chargez le diagramme cible');const doc=JSON.parse(await file.text());spofResult=analyzeSanSpof(doc);$('spofRows').replaceChildren();for(const r of spofResult.results){const tr=document.createElement('tr');for(const value of [r.kind+' : '+r.label,r.loss,r.degraded,r.applications]){const td=document.createElement('td');td.textContent=String(value);tr.append(td);}$('spofRows').append(tr);}$('spofSummary').textContent=spofResult.spofs.length+' SPOF modélisé(s) / '+spofResult.results.length+' cibles testées. Analyse documentaire.';$('spofCsv').disabled=false;$('spofHtml').disabled=false;}catch(e){spofResult=null;$('spofRows').replaceChildren();$('spofSummary').textContent='Analyse impossible : '+e.message;$('spofCsv').disabled=true;$('spofHtml').disabled=true;}});
 $('spofCsv').addEventListener('click',()=>{if(spofResult)downloadText('openvisio-spof.csv',spofCsv(spofResult),'text/csv;charset=utf-8');});
 $('spofHtml').addEventListener('click',()=>{if(spofResult)downloadText('openvisio-spof.html',spofHtml(spofResult),'text/html;charset=utf-8');});
 let campaignResult=null;
 $('campaignRun').addEventListener('click',async()=>{try{const file=$('topologyAfter').files[0];if(!file)throw new Error('Chargez le diagramme cible');const doc=JSON.parse(await file.text());const selected=[...failureSelect.selectedOptions].map(o=>{const [kind,id]=JSON.parse(o.value);return {kind,id};});if(!selected.length)throw new Error('Sélectionnez au moins une panne');const scenarios=selected.map((f,i)=>({id:'single-'+i,name:'Panne '+f.kind+' : '+f.id,failures:[f]}));if(selected.length>1)scenarios.push({id:'combined',name:'Pannes simultanées',failures:selected});campaignResult=runResilienceCampaign(doc,scenarios);$('campaignRows').replaceChildren();for(const r of campaignResult.results){const tr=document.createElement('tr');for(const value of [r.name,r.failures.length,r.summary.loss,r.summary.degraded,r.summary.applications]){const td=document.createElement('td');td.textContent=String(value);tr.append(td);}$('campaignRows').append(tr);}$('campaignSummary').textContent=campaignResult.results.length+' scénarios comparés ; classement par pertes puis dégradations.';$('campaignCsv').disabled=false;$('campaignHtml').disabled=false;}catch(e){campaignResult=null;$('campaignSummary').textContent='Campagne impossible : '+e.message;$('campaignCsv').disabled=true;$('campaignHtml').disabled=true;}});
 $('campaignCsv').addEventListener('click',()=>{if(campaignResult)downloadText('openvisio-campagne-resilience.csv',campaignCsv(campaignResult),'text/csv;charset=utf-8');});
 $('campaignHtml').addEventListener('click',()=>{if(campaignResult)downloadText('openvisio-campagne-resilience.html',campaignHtml(campaignResult),'text/html;charset=utf-8');});
 $('failureMultiRun').addEventListener('click',async()=>{try{const file=$('topologyAfter').files[0];if(!file)throw new Error('Chargez le diagramme cible');const doc=JSON.parse(await file.text());const chosen=[...failureSelect.selectedOptions].map(o=>{const [kind,id]=JSON.parse(o.value);return {kind,id};});failureResult=simulateMultipleSanFailures(doc,chosen);$('failureSummary').textContent=`Scénario combiné : ${failureResult.targets.length} panne(s), ${failureResult.summary.loss} perte(s), ${failureResult.summary.degraded} dégradation(s), ${failureResult.summary.applications} application(s)`;$('failureRows').replaceChildren();for(const r of failureResult.rows){const tr=document.createElement('tr');if(r.impact==='loss')tr.style.background='#ffd9d9';else if(r.impact==='degraded')tr.style.background='#fff0cc';for(const v of [r.server,r.storage,r.before+' → '+r.after,r.pathsBefore+' → '+r.pathsAfter,r.impact]){const td=document.createElement('td');td.textContent=v;tr.append(td);}$('failureRows').append(tr);}$('failureCsv').disabled=false;$('failureHtml').disabled=false;}catch(e){failureResult=null;$('failureSummary').textContent='Simulation combinée impossible : '+e.message;}});
 $('failureRun').addEventListener('click',async()=>{try{const file=$('topologyAfter').files[0];if(!file)throw new Error('Chargez le diagramme cible');const doc=JSON.parse(await file.text());const [kind,id]=JSON.parse(failureSelect.value);failureResult=simulateSanFailure(doc,{kind,id});$('failureSummary').textContent=`${failureResult.summary.affected} paire(s) affectée(s), ${failureResult.summary.loss} perte(s), ${failureResult.summary.applications} application(s) associée(s)`;$('failureRows').replaceChildren();for(const r of failureResult.rows){const tr=document.createElement('tr');if(r.impact==='loss')tr.style.background='#ffd9d9';else if(r.impact==='degraded')tr.style.background='#fff0cc';for(const value of [r.server,r.storage,r.before+' → '+r.after,r.pathsBefore+' → '+r.pathsAfter,r.impact]){const td=document.createElement('td');td.textContent=value;tr.append(td);}$('failureRows').append(tr);}$('failureCsv').disabled=false;$('failureHtml').disabled=false;}catch(e){failureResult=null;$('failureSummary').textContent='Simulation impossible : '+e.message;$('failureCsv').disabled=true;$('failureHtml').disabled=true;}});
 $('failureCsv').addEventListener('click',()=>{if(failureResult)downloadText('openvisio-simulation-san.csv',(failureResult.targets?multipleFailureCsv(failureResult):failureCsv(failureResult)),'text/csv;charset=utf-8');});
 $('failureHtml').addEventListener('click',()=>{if(failureResult)downloadText('openvisio-simulation-san.html',(failureResult.targets?multipleFailureHtml(failureResult):failureHtml(failureResult)),'text/html;charset=utf-8');});
 $('topologyAfter').addEventListener('change',async()=>{failureResult=null;$('failureRows').replaceChildren();$('failureCsv').disabled=true;$('failureHtml').disabled=true;failureSelect.replaceChildren();try{const f=$('topologyAfter').files[0];if(!f)return;const doc=JSON.parse(await f.text());for(const t of failureTargets(doc)){const option=document.createElement('option');option.value=JSON.stringify([t.kind,t.id]);option.textContent=t.kind+' : '+t.label;failureSelect.append(option);}$('failureSummary').textContent='Choisissez un élément et lancez une simulation sans modification du diagramme.';}catch(e){$('failureSummary').textContent='Fichier invalide : '+e.message;}});
 $('topologyDiffClose').addEventListener('click',()=>dialog.close());
 async function refresh(){current=null;overlay=null;impact=null;ports=null;apps=null;matrix=null;chains=null;relations=null;zoningCorrelation=null,sanAccess=null;$("topologyRelationsRows").replaceChildren();$("topologyRelationsCsv").disabled=true;$("topologyRelationsHtml").disabled=true;$('topologyImpactRows').replaceChildren();$('topologyPortRows').replaceChildren();$('topologyMatrixRows').replaceChildren();$('topologyChainRows').replaceChildren();$('topologyChainCsv').disabled=true;$('topologyChainHtml').disabled=true;$('topologyMatrixCsv').disabled=true;$('topologyMatrixHtml').disabled=true;$('topologyAppRows').replaceChildren();$('topologyPortExport').disabled=true;$('topologyImpactExport').disabled=true;$('topologyOverlay').replaceChildren();$('topologyDiffExport').disabled=true;$('topologyDiffRows').replaceChildren();if(!inputs.every(i=>i.files?.[0]))return;
 try{const [before,after]=await Promise.all(inputs.map(async i=>JSON.parse(await i.files[0].text())));current=diffTopologies(before,after);impact=compareSanConnectivity(before,after);ports=compareFcPorts(before,after);apps=applicationImpact(before,after);matrix=buildSanImpactMatrix(before,after);chains=compareSanChains(before,after);relations=auditSanRelations(after);const imported=after.sanImport||lastSanImport;sanAccess=auditSanAccess(after,imported);const consolidated=validateSanEndToEnd(after,after.sanImport||null);$('topologyEndSummary').textContent=`${consolidated.summary.total} chaîne(s), ${consolidated.summary.high} alerte(s) haute(s), ${consolidated.summary.medium} moyenne(s)`;$('topologyEndRows').replaceChildren();for(const r of consolidated.rows){const tr=document.createElement('tr');for(const value of [r.server,r.storage,r.lun,r.fabrics.join('/'),r.severity,r.issues.join(', ')||'—']){const td=document.createElement('td');td.textContent=value;tr.append(td);}if(r.severity==='high')tr.style.background='#ffe0dc';$('topologyEndRows').append(tr);}$('topologyEndCsv').disabled=false;$('topologyEndHtml').disabled=false;$('topologyAccessRows').replaceChildren();$('topologyAccessSummary').textContent=`${sanAccess.summary.review} à examiner sur ${sanAccess.summary.total} liens SAN`;for(const r of sanAccess.rows){const tr=document.createElement('tr');if(r.issues.length)tr.style.background='#ffe4de';for(const v of [r.source,r.target,r.lun,r.initiator,r.path,r.fabric,r.issues.join(', ')||'OK']){const td=document.createElement('td');td.textContent=v;tr.append(td);}$('topologyAccessRows').append(tr);}$('topologyAccessCsv').disabled=false;$('topologyAccessHtml').disabled=false;if(imported){zoningCorrelation=correlateSanZoning(after,imported);$('topologyZoningSummary').textContent=`${zoningCorrelation.summary.review} à examiner sur ${zoningCorrelation.summary.total} liens renseignés`;for(const r of zoningCorrelation.rows){const tr=document.createElement('tr');if(r.issues.length)tr.style.background='#ffe4de';for(const v of [r.source,r.target,r.zone,r.vsan,r.initiator,r.targetWwpn,r.issues.join(', ')||'OK']){const td=document.createElement('td');td.textContent=v;tr.append(td);} $('topologyZoningRows').append(tr);} $('topologyZoningCsv').disabled=false;$('topologyZoningHtml').disabled=false;}else{$('topologyZoningSummary').textContent='Aucun import SAN disponible dans le diagramme cible ni dans la session.';}$("topologyRelationsSummary").textContent=`${relations.summary.review} connexion(s) à examiner sur ${relations.summary.total}`;for(const r of relations.rows){const tr=document.createElement("tr");if(r.issues.length)tr.style.background="#ffe4de";for(const v of [r.source,r.target,r.initiatorWwpn,r.targetWwpn,r.zoneName,r.lunId,r.pathId,r.issues.join(", ")||"—"]){const td=document.createElement("td");td.textContent=v;tr.append(td);}$("topologyRelationsRows").append(tr);}$("topologyRelationsCsv").disabled=false;$("topologyRelationsHtml").disabled=false;$('topologyChainSummary').textContent=`${chains.summary.total} chaîne(s), ${chains.summary.changed} changement(s), ${chains.summary.review} à examiner`;for(const r of chains.rows){const tr=document.createElement('tr');if(r.risk==='review')tr.style.background='#ffe1df';for(const v of [r.server,r.storage,r.fabrics.join('/')||'—',r.hbas.join(', ')||'—',r.wwpns.join(', ')||'—',r.luns.join(', ')||'—',r.multipath,r.applications.join(', ')||'—',r.changes.join(', ')||'—']){const td=document.createElement('td');td.textContent=v;tr.append(td);}$('topologyChainRows').append(tr);}$('topologyChainCsv').disabled=false;$('topologyChainHtml').disabled=false;$('topologyMatrixSummary').textContent=`${matrix.summary.total} paire(s), ${matrix.summary.high} dégradation(s), ${matrix.summary.affectedApplications} application(s) associée(s)`;for(const r of matrix.rows){const tr=document.createElement('tr');if(r.priority==='high')tr.style.background='#ffe1df';for(const v of [r.server,r.storage,r.applications.join(', ')||'—',r.fabricBefore.join('/')+' → '+r.fabricAfter.join('/'),r.pathsBefore+' → '+r.pathsAfter,r.status]){const td=document.createElement('td');td.textContent=v;tr.append(td);}$('topologyMatrixRows').append(tr);}$('topologyMatrixCsv').disabled=false;$('topologyMatrixHtml').disabled=false;for(const r of ports.rows.filter(x=>x.status!=='stable')){const tr=document.createElement('tr');for(const v of [r.nodeName,r.port,`${r.before} → ${r.after}`,r.status]){const td=document.createElement('td');td.textContent=v;tr.append(td);}$('topologyPortRows').append(tr);}for(const r of apps.filter(x=>x.impactedPairs)){const tr=document.createElement('tr');for(const v of [r.applicationName,r.servers.join(', '),r.impactedPairs,r.affectedTargets.join(', ')]){const td=document.createElement('td');td.textContent=v;tr.append(td);}$('topologyAppRows').append(tr);}$('topologyPortExport').disabled=false;overlay=overlayModel(before,after);renderOverlay();const summary=diffSummary(current);$('topologyDiffSummary').textContent=`${summary.added} ajout(s), ${summary.removed} suppression(s), ${summary.changed} modification(s)`;
 for(const entry of current){const tr=document.createElement('tr');tr.tabIndex=0;tr.style.cursor='pointer';tr.addEventListener('click',()=>{ $('topologyFocus').value=entry.id;renderOverlay(); });tr.style.background=entry.status==='added'?'#dff8e9':entry.status==='removed'?'#ffe4e4':'#fff1d2';for(const value of [entry.kind,entry.after?.title||entry.before?.title||entry.id,entry.status,entry.fields.join(', ')]){const td=document.createElement('td');td.textContent=value;td.style.padding='7px';tr.append(td);}$('topologyDiffRows').append(tr);}for(const finding of impact.findings.filter(f=>f.impact!=='stable')){const tr=document.createElement('tr');for(const val of [finding.sourceName+' → '+finding.targetName,finding.before,finding.after,finding.impact,finding.lostFabrics.join(', ')||'—']){const td=document.createElement('td');td.textContent=val;td.style.padding='6px';tr.append(td);}tr.style.background=['degraded','removed-pair'].includes(finding.impact)?'#ffe0e0':'#dcf6e5';$('topologyImpactRows').append(tr);}$('topologyImpactSummary').textContent=impact.summary.degraded+' paire(s) dégradée(s), '+impact.summary.improved+' améliorée(s). Analyse déclarative uniquement.';$('topologyImpactExport').disabled=false;$('topologyDiffExport').disabled=false;
 }catch(e){$('topologyDiffSummary').textContent='Comparaison refusée : '+e.message;}}
 function renderOverlay(){if(!overlay)return;const filter=$('topologyFilter').value,focus=$('topologyFocus').value.trim()||null;$('topologyOverlay').innerHTML=overlaySvg(overlay,{filter,focus});}
 $('topologyFilter').addEventListener('change',renderOverlay);$('topologyFocus').addEventListener('input',renderOverlay);$('topologyClearFocus').addEventListener('click',()=>{$('topologyFocus').value='';renderOverlay();});
 $('topologyEndCsv').addEventListener('click',()=>{const f=$('topologyAfter').files[0];if(!f)return;f.text().then(t=>{const d=JSON.parse(t);downloadText('openvisio-validation-san.csv',sanEndToEndCsv(validateSanEndToEnd(d,d.sanImport||null)),'text/csv;charset=utf-8');});});$('topologyEndHtml').addEventListener('click',()=>{const f=$('topologyAfter').files[0];if(!f)return;f.text().then(t=>{const d=JSON.parse(t);downloadText('openvisio-validation-san.html',sanEndToEndHtml(validateSanEndToEnd(d,d.sanImport||null)),'text/html;charset=utf-8');});});$('topologyAccessCsv').addEventListener('click',()=>{if(sanAccess)downloadText('openvisio-audit-acces-san.csv',sanAccessCsv(sanAccess),'text/csv;charset=utf-8');});$('topologyAccessHtml').addEventListener('click',()=>{if(sanAccess)downloadText('openvisio-audit-acces-san.html',sanAccessHtml(sanAccess),'text/html;charset=utf-8');});$('topologyZoningCsv').addEventListener('click',()=>{if(zoningCorrelation)downloadText('openvisio-correlation-zoning.csv',zoningCorrelationCsv(zoningCorrelation),'text/csv;charset=utf-8');});$('topologyZoningHtml').addEventListener('click',()=>{if(zoningCorrelation)downloadText('openvisio-correlation-zoning.html',zoningCorrelationHtml(zoningCorrelation),'text/html;charset=utf-8');});$('topologyRelationsCsv').addEventListener('click',()=>{if(relations)downloadText('openvisio-relations-san.csv',sanRelationsCsv(relations),'text/csv;charset=utf-8');});$('topologyRelationsHtml').addEventListener('click',()=>{if(relations)downloadText('openvisio-relations-san.html',sanRelationsHtml(relations),'text/html;charset=utf-8');});$('topologyChainCsv').addEventListener('click',()=>{if(chains)downloadText('openvisio-chaines-san.csv',sanChainsCsv(chains),'text/csv;charset=utf-8');});$('topologyChainHtml').addEventListener('click',()=>{if(chains)downloadText('openvisio-chaines-san.html',sanChainsHtml(chains),'text/html;charset=utf-8');});$('topologyMatrixCsv').addEventListener('click',()=>{if(matrix)downloadText('openvisio-matrice-impact-san.csv',sanImpactMatrixCsv(matrix),'text/csv;charset=utf-8');});$('topologyMatrixHtml').addEventListener('click',()=>{if(matrix)downloadText('openvisio-matrice-impact-san.html',sanImpactMatrixHtml(matrix),'text/html;charset=utf-8');});$('topologyPortExport').addEventListener('click',()=>{if(ports&&apps)downloadText('openvisio-ports-dependances.html',portImpactHtml(ports,apps),'text/html;charset=utf-8');});$('topologyImpactExport').addEventListener('click',()=>{if(impact)downloadText('openvisio-san-impact.html',sanImpactHtml(impact),'text/html;charset=utf-8');});inputs.forEach(i=>i.addEventListener('change',refresh));$('topologyDiffExport').addEventListener('click',()=>{if(current)downloadText('openvisio-topology-diff.html',topologyDiffHtml(current),'text/html;charset=utf-8');});
}

// v18.3: one open tool menu, outside-click and Escape dismissal.
installToolMenus(document);

// v21.6 — palette de commandes : n'exécute que des actions déjà présentes dans l'atelier.
const commandCatalog=[
 ['Sélection','[data-tool="select"]'],['Connecteur','[data-tool="connect"]'],
 ['Ajouter un serveur','[data-shape="server"]'],['Ajouter un stockage','[data-shape="storage"]'],
 ['Ajouter un switch SAN','[data-shape="switch"]'],['Ajouter un cloud','[data-shape="cloud"]'],
 ['Exporter SVG','#exportBtn'],['Enregistrer JSON','#saveJsonBtn'],['Ouvrir JSON','#openJsonBtn'],
 ['Sauvegarde JSON','#portableExportBtn'],['Restaurer JSON','#portableImportBtn'],
 ['État sauvegardes','#recoveryStatusBtn'],['Canevas seul','#focusCanvasBtn'],
 ['Bibliothèque','#toggleLibraries'],['Inspecteur','#toggleInspector'],
 ['Grouper','#groupBtn'],['Dégrouper','#ungroupBtn'],['Nouveau calque','#newLayerBtn'],
 ['Ajuster le zoom','#fitCanvas'],['Annuler','#undoBtn'],['Rétablir','#redoBtn']
];
const commandDialog=$('commandSearchDialog'),commandInput=$('commandSearchInput'),commandResults=$('commandSearchResults');
function refreshCommandSearch(){
 const q=commandInput.value.trim().toLocaleLowerCase('fr');commandResults.replaceChildren();
 const entries=commandCatalog.filter(([label,selector])=>label.toLocaleLowerCase('fr').includes(q)&&document.querySelector(selector));
 for(const [label,selector] of entries){const action=document.createElement('button');action.type='button';action.setAttribute('role','option');action.textContent=label;action.addEventListener('click',()=>{const target=document.querySelector(selector);if(!target||target.disabled)return;commandDialog.close();target.click();});commandResults.append(action);}
 $('commandSearchCount').textContent=entries.length+' commande(s)';
}
function openCommandSearch(){refreshCommandSearch();if(!commandDialog.open)commandDialog.showModal();commandInput.focus();commandInput.select();}
$('commandSearchBtn').addEventListener('click',openCommandSearch);
$('commandSearchClose').addEventListener('click',()=>commandDialog.close());
commandInput.addEventListener('input',refreshCommandSearch);
commandInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();commandResults.querySelector('button:not(:disabled)')?.click();}});
function openSelectionInspector(){const inspector=$('inspectorPanel');if(inspector.classList.contains('hidden-panel'))$('toggleInspector').click();inspector.scrollIntoView({block:'nearest'});inspector.setAttribute('tabindex','-1');inspector.focus({preventScroll:true});}
$('inspectSelectionBtn').addEventListener('click',openSelectionInspector);
document.addEventListener('keydown',e=>{if(!(e.ctrlKey||e.metaKey)||e.altKey)return;const key=e.key.toLowerCase();if(e.shiftKey&&key==='p'){e.preventDefault();openCommandSearch();}else if(!e.shiftKey&&key==='i'){e.preventDefault();openSelectionInspector();}});

installPrimaryShortcuts(document);
// Restore the document before computing its saved state or rendering the canvas.
savedFingerprint=documentFingerprint();
renderLibrary();paint();

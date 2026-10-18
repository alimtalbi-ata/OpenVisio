/** Navigation stable des anomalies, sans mutation du graphe. */
export function nextFindingIndex(length,current,delta){
 if(!Number.isInteger(length)||length<=0)return -1;
 return ((current+delta)%length+length)%length;
}
export function edgeViewportTarget(viewportRect,edgeRect,scrollLeft,scrollTop){
 if(!viewportRect||!edgeRect)return null;
 const x=scrollLeft+edgeRect.left+edgeRect.width/2-viewportRect.left-viewportRect.width/2;
 const y=scrollTop+edgeRect.top+edgeRect.height/2-viewportRect.top-viewportRect.height/2;
 return {left:Math.max(0,x),top:Math.max(0,y)};
}

/** Compute a conservative fit factor from on-screen group bounds, independent of DOM. */
export function fitConflictGroupZoom(viewportRect,groupRect,currentZoom,{padding=48,minZoom=.5,maxZoom=1.5}={}){
 if(!viewportRect||!groupRect||![viewportRect.width,viewportRect.height,groupRect.width,groupRect.height,currentZoom].every(v=>Number.isFinite(v)&&v>0))return null;
 if(!Number.isFinite(padding)||padding<0||!Number.isFinite(minZoom)||!Number.isFinite(maxZoom)||minZoom<=0||maxZoom<minZoom)return null;
 const availableWidth=viewportRect.width-2*padding,availableHeight=viewportRect.height-2*padding;
 if(availableWidth<=0||availableHeight<=0)return null;
 const factor=Math.min(availableWidth/groupRect.width,availableHeight/groupRect.height);
 return Math.min(maxZoom,Math.max(minZoom,currentZoom*factor));
}

/** Read-only, selection-aware metrics for one SAN conflict component. */
export function summarizeSanConflictGroup(group,proposals,conflicts,selectedIds){
 const members=new Set(group?.edgeIds||[]), selected=new Set(selectedIds||[]);
 const validProposals=(proposals||[]).filter(p=>members.has(p.edgeId));
 const gain=validProposals.reduce((total,p)=>{
  if(!selected.has(p.edgeId))return total;
  const before=Number(p.before?.score),after=Number(p.after?.score);
  return total+(Number.isFinite(before)&&Number.isFinite(after)?Math.max(0,before-after):0);
 },0);
 const related=(conflicts||[]).filter(c=>members.has(c.a)&&members.has(c.b));
 const fabric=related.filter(c=>c.crossFabric);
 const active=related.filter(c=>selected.has(c.a)&&selected.has(c.b));
 const activeFabric=active.filter(c=>c.crossFabric);
 return {gain,selected:validProposals.filter(p=>selected.has(p.edgeId)).length,conflicts:related.length,activeConflicts:active.length,fabricConflicts:fabric.length,activeFabricConflicts:activeFabric.length,valid:active.length===0};
}

// Auteur : Abdelhalim Talbi
export function groupNodes(state,ids,name="Groupe") {const chosen=state.nodes.filter(n=>ids.includes(n.id));if(chosen.length<2)return null;const id=`group-${Date.now()}-${Math.random().toString(36).slice(2,7)}`;state.groups??=[];state.groups.push({id,name});chosen.forEach(n=>n.groupId=id);return id;}
export function ungroupNodes(state,ids){const groups=new Set(state.nodes.filter(n=>ids.includes(n.id)).map(n=>n.groupId).filter(Boolean));state.nodes.forEach(n=>{if(groups.has(n.groupId))delete n.groupId});state.groups=(state.groups||[]).filter(g=>!groups.has(g.id));return groups.size;}
export function createLayer(state,name){state.layers??=[];const id=`layer-${Date.now()}-${Math.random().toString(36).slice(2,7)}`;state.layers.push({id,name,visible:true,locked:false});return id;}
export function setLayer(state,ids,layerId){if(!(state.layers||[]).some(l=>l.id===layerId))return false;state.nodes.filter(n=>ids.includes(n.id)).forEach(n=>n.layerId=layerId);return true;}
export function visibleNode(state,n){const layer=(state.layers||[]).find(l=>l.id===n.layerId);return !layer||layer.visible!==false;}
export function editableNode(state,n){const layer=(state.layers||[]).find(l=>l.id===n.layerId);return !layer||layer.locked!==true;}

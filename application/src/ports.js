// Auteur : Abdelhalim Talbi — catalogue de ports logiques configurables.
export const PORT_KINDS = Object.freeze(['ethernet','fibre-channel','management','virtual','other']);
export function parsePorts(raw){
 if(typeof raw!=='string')throw Error('Ports invalides');
 const names=raw.split(/[\n;,]+/).map(x=>x.trim()).filter(Boolean);
 if(names.length>64)throw Error('Maximum 64 ports');
 if(names.some(n=>n.length>40||! /^[\p{L}\p{N}_.:/-]+$/u.test(n)))throw Error('Nom de port invalide');
 if(new Set(names.map(n=>n.toLowerCase())).size!==names.length)throw Error('Port en doublon');
 return names;
}
export function portNames(node){return Array.isArray(node?.ports)?node.ports:[];}
export function validateEdgePort(edge,source,target){return (!edge.sourceInterface||portNames(source).includes(edge.sourceInterface))&&(!edge.targetInterface||portNames(target).includes(edge.targetInterface));}
export function suggestedPorts(type){if(type==='switch')return ['Gi1/0/1','Gi1/0/2','Gi1/0/3','Gi1/0/4'];if(type==='storage')return ['FC0','FC1','eth0'];if(type==='server')return ['eth0','eth1','vmnic0','FC0'];return ['eth0'];}

// Positions visuelles deterministes, limitees pour eviter de surcharger les petites formes.
export function physicalPortMarkers(node,limit=12){
 const names=portNames(node).slice(0,Math.max(0,Math.min(32,limit)));
 const w=Number(node?.w),h=Number(node?.h);
 if(!Number.isFinite(w)||!Number.isFinite(h)||w<=0||h<=0)return [];
 const count=names.length;
 return names.map((name,i)=>({name,x:Math.round(w*(i+1)/(count+1)),y:Math.max(5,h-6)}));
}
export function cableDiagnostics(nodes,edges){
 const byId=new Map(nodes.map(n=>[n.id,n]));const usage=new Map();const findings=[];
 for(const edge of edges){
  const source=byId.get(edge.from),target=byId.get(edge.to);
  if(!source||!target){findings.push({edgeId:edge.id,code:'missing-endpoint'});continue;}
  if(edge.sourceInterface&&edge.targetInterface){
   const compatibility=cableCompatibility(edge.sourceInterface,edge.targetInterface);
   if(compatibility.status==='incompatible'||compatibility.status==='review')findings.push({edgeId:edge.id,code:'interface-'+compatibility.status,...compatibility});
  }
  for(const [node,name,side] of [[source,edge.sourceInterface,'source'],[target,edge.targetInterface,'target']]){
   if(!name)continue;
   if(!portNames(node).includes(name)){findings.push({edgeId:edge.id,code:'unknown-port',side,port:name});continue;}
   const key=JSON.stringify([node.id,name]);
   if(usage.has(key)&&usage.get(key)!==edge.id)findings.push({edgeId:edge.id,code:'port-reused',side,port:name,previousEdgeId:usage.get(key)});
   else usage.set(key,edge.id);
  }
 }
 return findings;
}

// Correspondance physique déterministe : les liens utilisent les mêmes repères que le SVG.
export function namedPortPosition(node,name,limit=12){
 const marker=physicalPortMarkers(node,limit).find(p=>p.name===name);
 return marker?{x:node.x+marker.x,y:node.y+marker.y,name:marker.name}:null;
}
export function interfaceFamily(name){
 if(typeof name!=="string"||!name.trim())return "unknown";
 const n=name.trim().toLowerCase();
 if(/^(fc|fibre|fiber|wwpn|san)[\w/.-]*$/.test(n))return "fibre-channel";
 if(/^(vmnic|vnic|veth|tap|vlan|bond|team|br-|vswitch)/.test(n))return "virtual";
 if(/^(mgmt|management|ilo|idrac|bmc|ipmi)/.test(n))return "management";
 if(/^(eth|enp|ens|eno|em[0-9]|gi|te|xe|ge|ethernet|port-channel)/.test(n))return "ethernet";
 return "unknown";
}
export function cableCompatibility(sourceName,targetName){
 const a=interfaceFamily(sourceName),b=interfaceFamily(targetName);
 if(a==="unknown"||b==="unknown")return {status:"unknown",sourceFamily:a,targetFamily:b};
 if(a===b)return {status:"compatible",sourceFamily:a,targetFamily:b};
 // Virtual ports and management links require topology context: warn rather than reject.
 if(a==="virtual"||b==="virtual"||a==="management"||b==="management")return {status:"review",sourceFamily:a,targetFamily:b};
 return {status:"incompatible",sourceFamily:a,targetFamily:b};
}


// Inventaire de câblage: une entrée par port déclaré, avec occupation et anomalies.
export function portInventory(nodes,edges){
 const findings=cableDiagnostics(nodes,edges);
 // Indexer les liens une seule fois : évite un balayage de tous les câbles par port.
 const byPort=new Map(), byEdge=new Map();
 const add=(id,port,edge)=>{
  if(!port)return;
  const key=JSON.stringify([id,port]);
  if(!byPort.has(key))byPort.set(key,[]);
  // Un lien en boucle sur le même port ne doit pas compter deux fois.
  if(!byPort.get(key).some(e=>e.id===edge.id))byPort.get(key).push(edge);
 };
 for(const edge of edges){add(edge.from,edge.sourceInterface,edge);add(edge.to,edge.targetInterface,edge);}
 for(const finding of findings){if(!byEdge.has(finding.edgeId))byEdge.set(finding.edgeId,[]);byEdge.get(finding.edgeId).push(finding);}
 const inventory=[];
 for(const node of nodes){
  for(const port of portNames(node)){
   const links=byPort.get(JSON.stringify([node.id,port]))||[];
   inventory.push({nodeId:node.id,nodeTitle:node.title||node.id,port,family:interfaceFamily(port),status:links.length===0?'free':links.length===1?'used':'conflict',edgeIds:links.map(e=>e.id),findings:links.flatMap(e=>byEdge.get(e.id)||[])});
  }
 }
 return inventory;
}

// Fabric A/B explicite : les noms seuls ne suffisent pas à établir une redondance.
export function fabricDiagnostics(nodes,edges){
 const byId=new Map(nodes.map(n=>[n.id,n]));const findings=[];
 for(const e of edges){
  const a=byId.get(e.from),b=byId.get(e.to);
  if(!a||!b)continue;
  const fa=String(a.fabric||'').trim().toUpperCase(),fb=String(b.fabric||'').trim().toUpperCase();
  if(fa&&fb&&fa!==fb&&fa!=='SHARED'&&fb!=='SHARED')findings.push({edgeId:e.id,code:'fabric-mismatch',sourceFabric:fa,targetFabric:fb});
 }
 return findings;
}
export function fabricRedundancy(nodes,edges){
 const byId=new Map(nodes.map(n=>[n.id,n]));
 return nodes.filter(n=>n.type==='server'||n.type==='storage').map(n=>{
  const fabrics=new Set();
  for(const e of edges){const other=e.from===n.id?byId.get(e.to):e.to===n.id?byId.get(e.from):null;
   if(other&&['A','B'].includes(String(other.fabric||'').trim().toUpperCase())&&interfaceFamily(e.from===n.id?e.sourceInterface:e.targetInterface)==='fibre-channel')fabrics.add(String(other.fabric).trim().toUpperCase());
  }
  return {nodeId:n.id,nodeTitle:n.title||n.id,fabrics:[...fabrics].sort(),redundant:fabrics.has('A')&&fabrics.has('B')};
 });
}

// V19.8 — analyse non destructive avant modification du catalogue de ports.
export function portChangeImpact(node, nextPorts, edges){
 const oldPorts=portNames(node);
 const next=new Set(nextPorts);
 const removed=oldPorts.filter(port=>!next.has(port));
 const affected=[];
 for(const edge of edges){
  const sides=[];
  if(edge.from===node.id&&edge.sourceInterface&&removed.includes(edge.sourceInterface))sides.push({side:'source',port:edge.sourceInterface});
  if(edge.to===node.id&&edge.targetInterface&&removed.includes(edge.targetInterface))sides.push({side:'target',port:edge.targetInterface});
  if(sides.length)affected.push({edgeId:edge.id,sides});
 }
 return {removed,affected,hasImpact:affected.length>0};
}

// V19.9 — transaction explicite de renommage, sans mutation pendant la prévisualisation.
export function planPortRename(node,oldName,newName,edges){
 const ports=portNames(node);
 if(!ports.includes(oldName))throw Error('Port source introuvable');
 const parsed=parsePorts(newName);
 if(parsed.length!==1||parsed[0]!==newName)throw Error('Nouveau nom de port invalide');
 if(oldName!==newName&&ports.some(p=>p.toLowerCase()===newName.toLowerCase()))throw Error('Nom de port déjà utilisé');
 const affected=[];
 for(const edge of edges){
  const sides=[];
  if(edge.from===node.id&&edge.sourceInterface===oldName)sides.push('sourceInterface');
  if(edge.to===node.id&&edge.targetInterface===oldName)sides.push('targetInterface');
  if(sides.length)affected.push({edgeId:edge.id,sides});
 }
 return {nodeId:node.id,oldName,newName,affected,changed:oldName!==newName};
}
export function applyPortRename(nodes,edges,plan){
 const node=nodes.find(n=>n.id===plan.nodeId);
 if(!node)throw Error('Équipement introuvable');
 const current=planPortRename(node,plan.oldName,plan.newName,edges);
 if(JSON.stringify(current)!==JSON.stringify(plan))throw Error('Plan de renommage périmé');
 if(!plan.changed)return false;
 node.ports=node.ports.map(p=>p===plan.oldName?plan.newName:p);
 for(const edge of edges){
  if(edge.from===node.id&&edge.sourceInterface===plan.oldName)edge.sourceInterface=plan.newName;
  if(edge.to===node.id&&edge.targetInterface===plan.oldName)edge.targetInterface=plan.newName;
 }
 return true;
}

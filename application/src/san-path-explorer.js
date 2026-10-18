// OpenVisio v28.7 — exploration documentaire des chemins FC. Auteur : Abdelhalim Talbi.
const val=x=>String(x??'').trim();
const fabric=e=>{const f=val(e.fabric??e.sanFabric).toUpperCase();return f==='A'||f==='B'?f:'UNKNOWN';};
const kind=n=>val(n.type).toLowerCase();
export function exploreSanPaths(doc,{maxDepth=12,maxPaths=500}={}){
 const nodes=Array.isArray(doc?.nodes)?doc.nodes:[];
 const edges=Array.isArray(doc?.edges)?doc.edges:[];
 const byId=new Map(nodes.filter(n=>n&&n.id!=null).map(n=>[val(n.id),n]));
 const adjacency=new Map([...byId.keys()].map(id=>[id,[]]));
 for(const e of edges){if(!e||!byId.has(val(e.from))||!byId.has(val(e.to)))continue;
  const a=val(e.from),b=val(e.to);adjacency.get(a).push({to:b,edge:e});adjacency.get(b).push({to:a,edge:e});}
 for(const a of adjacency.values())a.sort((x,y)=>val(x.edge.id).localeCompare(val(y.edge.id))||x.to.localeCompare(y.to));
 const paths=[];let truncated=false;
 const servers=[...byId.values()].filter(n=>['server','host'].includes(kind(n))).sort((a,b)=>val(a.id).localeCompare(val(b.id)));
 for(const server of servers){
  const walk=(id,seen,chain)=>{
   if(paths.length>=maxPaths){truncated=true;return;}
   const n=byId.get(id);
   if(id!==val(server.id)&&['storage','array'].includes(kind(n))){
    const fabrics=[...new Set(chain.map(c=>fabric(c.edge)))].sort();
    const switches=chain.map(c=>byId.get(c.to)).filter(n=>['switch','san-switch','fc-switch'].includes(kind(n))).map(n=>val(n.id));
    paths.push({serverId:val(server.id),storageId:id,nodeIds:[val(server.id),...chain.map(c=>c.to)],edgeIds:chain.map(c=>val(c.edge.id)),fabrics,switches,issues:[...(fabrics.length!==1||fabrics[0]==='UNKNOWN'?['FABRIC_UNVERIFIED_OR_CROSSED']:[]),...(switches.length===0?['NO_FC_SWITCH_DOCUMENTED']:[])]});return;
   }
   if(chain.length>=maxDepth)return;
   for(const next of adjacency.get(id)||[]){if(seen.has(next.to))continue;seen.add(next.to);walk(next.to,seen,[...chain,next]);seen.delete(next.to);if(truncated)return;}
  };walk(val(server.id),new Set([val(server.id)]),[]);
 }
 const groups=new Map();
 for(const p of paths){const key=JSON.stringify([p.serverId,p.storageId]);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p);}
 const resilience=[...groups].map(([key,ps])=>{
  const [serverId,storageId]=JSON.parse(key);const a=ps.filter(p=>p.fabrics.length===1&&p.fabrics[0]==='A');const b=ps.filter(p=>p.fabrics.length===1&&p.fabrics[0]==='B');
  const disjoint=a.some(x=>b.some(y=>!x.switches.some(s=>y.switches.includes(s))&&!x.edgeIds.some(e=>y.edgeIds.includes(e))));
  return {serverId,storageId,pathCount:ps.length,fabricA:a.length,fabricB:b.length,disjointDocumented:disjoint,issues:[...(!a.length||!b.length?['FABRIC_AB_NOT_DEMONSTRATED']:[]),...(!disjoint?['DISJOINT_PATHS_NOT_DEMONSTRATED']:[])]};
 }).sort((a,b)=>a.serverId.localeCompare(b.serverId)||a.storageId.localeCompare(b.storageId));
 return {paths,resilience,truncated,scope:'Analyse documentaire seulement ; aucune découverte SAN ou preuve de multipathing effectif.'};
}

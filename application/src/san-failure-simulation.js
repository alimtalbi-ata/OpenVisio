// OpenVisio v28.9 — simulation documentaire, aucune action sur le SAN. Auteur : Abdelhalim Talbi.
import {exploreSanPaths} from './san-path-explorer.js';
export function simulateSanFailure(doc,{failedNodeId=null,failedFabric=null,maxDepth=10,maxPaths=300}={}){
 const fabric=String(failedFabric??'').toUpperCase();
 if(fabric&&!['A','B'].includes(fabric))throw new RangeError('Fabric attendue : A ou B');
 const id=failedNodeId==null?null:String(failedNodeId);
 const original=exploreSanPaths(doc,{maxDepth,maxPaths});
 const nodes=(doc.nodes||[]).filter(n=>String(n.id)!==id);
 const valid=new Set(nodes.map(n=>String(n.id)));
 const edges=(doc.edges||[]).filter(e=>valid.has(String(e.from))&&valid.has(String(e.to))&&(!fabric||String(e.fabric??e.sanFabric??'').toUpperCase()!==fabric));
 const after=exploreSanPaths({nodes,edges},{maxDepth,maxPaths});
 const key=p=>JSON.stringify([p.serverId,p.storageId]);
 const groups=new Map();for(const p of original.paths){const k=key(p);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(p);}
 const affected=[...groups].map(([k,before])=>{const remaining=after.paths.filter(p=>key(p)===k);return {serverId:before[0].serverId,storageId:before[0].storageId,before:before.length,after:remaining.length,lost:before.length-remaining.length,unreachable:remaining.length===0};});
 return {before:original,after,affected,truncated:original.truncated||after.truncated,scope:'Simulation documentaire non destructive ; aucune preuve de disponibilité réelle.'};
}

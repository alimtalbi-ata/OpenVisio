// OpenVisio v13.8 — impact déclaratif ports FC et dépendances. Auteur : Abdelhalim Talbi.
import {validateTopology} from './topology-diff.js';
import {interfaceFamily} from './ports.js';
import {compareSanConnectivity} from './san-impact-diff.js';
const key=(id,port)=>JSON.stringify([id,port]);
const html=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function fcPortInventory(doc){
 validateTopology(doc);const nodes=new Map(doc.nodes.map(n=>[n.id,n]));const result=new Map();
 for(const edge of doc.edges){for(const [id,port] of [[edge.from,edge.sourceInterface],[edge.to,edge.targetInterface]]){
 if(interfaceFamily(port)!=='fibre-channel')continue;
 const k=key(id,port);if(!result.has(k))result.set(k,{nodeId:id,nodeName:nodes.get(id).title||id,port,edges:[]});result.get(k).edges.push(edge.id);
 }}return [...result.values()].sort((a,b)=>a.nodeId.localeCompare(b.nodeId)||a.port.localeCompare(b.port));
}
export function compareFcPorts(before,after){
 const old=new Map(fcPortInventory(before).map(p=>[key(p.nodeId,p.port),p]));const now=new Map(fcPortInventory(after).map(p=>[key(p.nodeId,p.port),p]));
 const rows=[...new Set([...old.keys(),...now.keys()])].sort().map(k=>{const a=old.get(k),b=now.get(k);const x=b||a;const previous=a?.edges.length||0,current=b?.edges.length||0;return {...x,before:previous,after:current,status:!a?'added':!b?'removed':current<previous?'reduced':current>previous?'expanded':'stable'};});
 return {rows,summary:{removed:rows.filter(r=>r.status==='removed').length,reduced:rows.filter(r=>r.status==='reduced').length,added:rows.filter(r=>r.status==='added').length}};
}
export function applicationImpact(before,after){
 validateTopology(before);validateTopology(after);const connectivity=compareSanConnectivity(before,after);
 // Dépendance uniquement si lien explicite entre une application et un serveur.
 const associations=doc=>{const nodes=new Map(doc.nodes.map(n=>[n.id,n]));const links=new Map();for(const e of doc.edges){for(const [app,server] of [[e.from,e.to],[e.to,e.from]])if(nodes.get(app)?.type==='application'&&nodes.get(server)?.type==='server'){if(!links.has(app))links.set(app,new Set());links.get(app).add(server);}}return links;};
 const old=associations(before),now=associations(after),nodes=new Map([...before.nodes,...after.nodes].map(n=>[n.id,n]));const rows=[];
 for(const app of new Set([...old.keys(),...now.keys()])){const servers=[...new Set([...(old.get(app)||[]),...(now.get(app)||[])])];const findings=connectivity.findings.filter(f=>servers.includes(f.sourceId)&&['degraded','removed-pair'].includes(f.impact));
 rows.push({applicationId:app,applicationName:nodes.get(app)?.title||app,servers,impactedPairs:findings.length,affectedTargets:[...new Set(findings.map(f=>f.targetName))],status:findings.length?'review':'no-degradation-detected'});}
 return rows.sort((a,b)=>b.impactedPairs-a.impactedPairs||a.applicationId.localeCompare(b.applicationId));
}
export function portImpactHtml(ports,apps){const tr=ports.rows.filter(r=>r.status!=='stable').map(r=>`<tr><td>${html(r.nodeName)}</td><td>${html(r.port)}</td><td>${html(r.before)} → ${html(r.after)}</td><td>${html(r.status)}</td></tr>`).join('');const ar=apps.map(a=>`<tr><td>${html(a.applicationName)}</td><td>${html(a.servers.join(', '))}</td><td>${html(a.impactedPairs)}</td><td>${html(a.affectedTargets.join(', '))}</td></tr>`).join('');return `<!doctype html><html lang="fr"><meta charset="utf-8"><title>OpenVisio — Ports FC et dépendances</title><style>body{font:15px system-ui;margin:2rem;color:#20334c}table{border-collapse:collapse;width:100%;margin-bottom:2rem}td,th{padding:.55rem;border:1px solid #bcc8d5;text-align:left}</style><h1>Analyse déclarative des ports FC et dépendances applicatives</h1><p>Auteur : Abdelhalim Talbi</p><p>Les ports sont inférés des connexions dessinées. Les applications sont liées aux serveurs par des connexions explicites. Ce rapport ne prouve ni l'état physique des ports, ni la configuration MPIO, ni une interruption applicative.</p><h2>Écarts des ports FC</h2><table><tr><th>Équipement</th><th>Port</th><th>Liens avant → après</th><th>Écart</th></tr>${tr}</table><h2>Applications à examiner</h2><table><tr><th>Application</th><th>Serveurs</th><th>Paires SAN dégradées</th><th>Stockages concernés</th></tr>${ar}</table></html>`;}

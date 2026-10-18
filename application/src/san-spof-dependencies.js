// OpenVisio v29.7 — dépendances communes documentaires. Auteur : Abdelhalim Talbi.
const key = value => String(value ?? '');
export function commonSanDependencies(paths = []) {
  if (!Array.isArray(paths)) return [];
  const groups = new Map();
  for (const path of paths) {
    if (!path || typeof path !== 'object') continue;
    const pair = key(path.pairId ?? path.pair ?? [path.serverId,path.storageId].map(key).join('→'));
    const fabric = key(path.fabric).toUpperCase();
    if (!pair || !['A','B'].includes(fabric)) continue;
    const components = [...new Set([...(Array.isArray(path.nodes)?path.nodes:[]),...(Array.isArray(path.edges)?path.edges:[])].map(key).filter(Boolean))];
    if (!groups.has(pair)) groups.set(pair,{A:[],B:[]});
    groups.get(pair)[fabric].push(new Set(components));
  }
  const findings=[];
  for (const [pair,fabrics] of groups) {
    if (!fabrics.A.length || !fabrics.B.length) continue;
    const a=new Set(fabrics.A.flatMap(s=>[...s]));
    const b=new Set(fabrics.B.flatMap(s=>[...s]));
    for (const id of [...a].filter(id=>b.has(id)).sort()) findings.push({pair,componentId:id,risk:'COMMON_DEPENDENCY',recommendation:'Vérifier indépendance physique et logique des chemins Fabric A/B'});
  }
  return findings.sort((a,b)=>a.pair.localeCompare(b.pair)||a.componentId.localeCompare(b.componentId));
}

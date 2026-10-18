// OpenVisio v31.9 — navigation conservative, matching exact switch identifiers only.
// Auteur : Abdelhalim Talbi.
const norm = value => String(value ?? '').trim().toLowerCase();
export function resolveZoningTargets(entry, snapshot) {
  const names = String(entry?.switch ?? '').split(';').map(norm).filter(x => x && x !== 'non documenté');
  const nodes = Array.isArray(snapshot?.objects) ? snapshot.objects : Array.isArray(snapshot?.nodes) ? snapshot.nodes : [];
  const matches = nodes.filter(node => {
    const values = [node.id,node.name,node.label].map(norm).filter(Boolean);
    return names.some(name => values.includes(name));
  });
  // An ambiguous switch name is not enough evidence for a safe navigation target.
  if (matches.length !== 1 || !matches[0]?.id) return {ids:[],status:matches.length > 1?'AMBIGUOUS':'UNRESOLVED'};
  return {ids:[String(matches[0].id)],status:'EXACT_SWITCH_MATCH'};
}
export function zoningProvenance(entry){
 return `Fabric: ${entry?.fabric||'non documentée'} · VSAN: ${entry?.vsan||'inconnu'} · Zone: ${entry?.zone||'inconnue'} · Lignes source: ${(entry?.sourceLines||[]).join(', ')||'non documentées'}`;
}

// Auteur : Abdelhalim Talbi — diagnostic de câblage exploitable.
export const DIAGNOSTIC_LEVELS=Object.freeze({
 'missing-endpoint':'critical','port-reused':'critical','fabric-mismatch':'critical',
 'interface-incompatible':'critical','unknown-port':'warning',
 'interface-review':'warning','cable-crossing':'info'
});
export function diagnosticLevel(code){return DIAGNOSTIC_LEVELS[code]||'info';}
export function summarizeDiagnostics(diagnostics){
 const counts={critical:0,warning:0,info:0};
 for(const finding of diagnostics)counts[diagnosticLevel(finding.code)]++;
 return counts;
}
export function filterDiagnostics(diagnostics,level='all'){
 if(!['all','critical','warning','info'].includes(level))throw Error('Filtre invalide');
 return level==='all'?[...diagnostics]:diagnostics.filter(item=>diagnosticLevel(item.code)===level);
}
export function diagnosticDescription(finding){
 const messages={
  'missing-endpoint':'Équipement source ou cible introuvable',
  'port-reused':'Port déjà utilisé par une autre connexion',
  'fabric-mismatch':'Connexion entre deux fabrics incompatibles',
  'interface-incompatible':'Familles d’interfaces incompatibles',
  'unknown-port':'Port absent de l’inventaire de l’équipement',
  'interface-review':'Compatibilité des interfaces à vérifier',
  'cable-crossing':`Croisement géométrique potentiel avec ${finding.otherEdgeId||'une autre connexion'} (segments du trajet calculé)`
 };
 return messages[finding.code]||`Contrôle : ${finding.code}`;
}

// Navigation non destructive : ne propose un lien que pour une connexion existante.
export function resolveDiagnosticEdge(finding,edges){
 if(!finding||typeof finding.edgeId!=='string'||!Array.isArray(edges))return null;
 return edges.find(edge=>edge.id===finding.edgeId)||null;
}

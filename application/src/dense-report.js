export function buildDenseTopologySummary(dense,legacy=null){
 const status=dense.complete?'complète':'partielle';
 const crossing=legacy?.crossingPairs??dense.issues.filter(x=>x.code==='route-crossing').length;
 const overlap=legacy?.overlappingSegmentPairs??dense.issues.filter(x=>x.code==='route-overlap').length;
 const suffix=legacy?'':' (anomalies distinctes affichées, non exhaustives)';
 return `Tracés : ${dense.routes} · Segments : ${dense.segments} · Invalides : ${dense.invalidRoutes} · Croisements : ${crossing} · Chevauchements : ${overlap}${suffix} · Paires examinées : ${dense.pairsChecked} · Analyse ${status}${dense.findingsLimited?' · Résultats limités':''}`;
}

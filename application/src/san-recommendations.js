// OpenVisio v27.8 — moteur déterministe de recommandations SAN. Auteur : Abdelhalim Talbi.
// Analyse déclarative en lecture seule : aucune action n'est appliquée au document.
const finite = v => typeof v === 'number' && Number.isFinite(v);
const text = (v, max=120) => String(v ?? '').trim().slice(0,max);
const arr = v => Array.isArray(v) ? v : [];
const SEVERITY = {critical:4, high:3, medium:2, low:1, info:0};
const RISK = {critical:4, high:3, medium:2, low:1, none:0};

function normalize(items) {
  if (!Array.isArray(items) || items.length > 10000) throw new Error('Liste de corrections invalide (maximum 10 000)');
  const seen = new Set();
  return items.map((raw, index) => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new Error(`Correction invalide à l'index ${index}`);
    const id = text(raw.id,160);
    if (!id || seen.has(id)) throw new Error('Identifiant de correction vide ou dupliqué');
    seen.add(id);
    const severity = text(raw.severity || 'medium',20).toLowerCase();
    const risk = text(raw.risk || 'none',20).toLowerCase();
    if (!(severity in SEVERITY) || !(risk in RISK)) throw new Error(`Niveau de sévérité/risque inconnu : ${id}`);
    return {id,groupId:text(raw.groupId || 'sans-groupe',160),title:text(raw.title || id,200),
      gain:finite(raw.gain)&&raw.gain>0?raw.gain:0, severity, risk,
      selected:raw.selected===true, blocked:raw.blocked===true,
      dependsOn:arr(raw.dependsOn).map(x=>text(x,160)).filter(Boolean),
      conflictsWith:arr(raw.conflictsWith).map(x=>text(x,160)).filter(Boolean),
      fabric:text(raw.fabric,10).toUpperCase(), reason:text(raw.reason,500), index};
  });
}
export function analyzeSanRecommendations(input) {
  const items=normalize(input), byId=new Map(items.map(x=>[x.id,x]));
  const issues=[], selected=items.filter(x=>x.selected), selectedIds=new Set(selected.map(x=>x.id));
  for(const x of items){
    for(const dep of x.dependsOn) if(!byId.has(dep)) issues.push({code:'MISSING_DEPENDENCY',id:x.id,relatedId:dep,severity:'high',detail:`Prérequis absent : ${dep}`});
    if(x.selected&&x.blocked) issues.push({code:'BLOCKED_SELECTED',id:x.id,severity:'critical',detail:'Correction sélectionnée mais déclarée bloquée'});
    if(x.selected) for(const dep of x.dependsOn) if(byId.has(dep)&&!selectedIds.has(dep))
      issues.push({code:'DEPENDENCY_NOT_SELECTED',id:x.id,relatedId:dep,severity:'high',detail:`Sélectionner le prérequis ${dep} ou retirer cette correction`});
    if(x.selected) for(const other of selected) {
      if(other.id===x.id) continue;
      const declared=x.conflictsWith.includes(other.id)||other.conflictsWith.includes(x.id);
      if(declared&&x.id.localeCompare(other.id)<0)
        issues.push({code:'SELECTED_CONFLICT',id:x.id,relatedId:other.id,severity:'critical',detail:`Corrections incompatibles : ${x.id} / ${other.id}`});
    }
  }
  // Directed dependency graph; Kahn's algorithm gives stable deterministic order.
  const eligible=items.filter(x=>!x.blocked&&!issues.some(i=>i.id===x.id&&['MISSING_DEPENDENCY','BLOCKED_SELECTED','DEPENDENCY_NOT_SELECTED','SELECTED_CONFLICT'].includes(i.code)));
  const eligibleIds=new Set(eligible.map(x=>x.id)), indegree=new Map(eligible.map(x=>[x.id,0])), next=new Map(eligible.map(x=>[x.id,[]]));
  for(const x of eligible) for(const dep of x.dependsOn) if(eligibleIds.has(dep)){indegree.set(x.id,indegree.get(x.id)+1);next.get(dep).push(x.id);}
  const ready=eligible.filter(x=>indegree.get(x.id)===0).sort((a,b)=>rank(b)-rank(a)||a.id.localeCompare(b.id));
  const ordered=[];
  while(ready.length){const x=ready.shift();ordered.push(x);for(const id of next.get(x.id)){indegree.set(id,indegree.get(id)-1);if(indegree.get(id)===0){ready.push(byId.get(id));ready.sort((a,b)=>rank(b)-rank(a)||a.id.localeCompare(b.id));}}}
  const cycleIds=eligible.filter(x=>indegree.get(x.id)>0).map(x=>x.id).sort();
  if(cycleIds.length) issues.push({code:'DEPENDENCY_CYCLE',id:cycleIds[0],relatedIds:cycleIds,severity:'critical',detail:`Cycle de dépendances : ${cycleIds.join(', ')}`});
  const cycleSet=new Set(cycleIds);
  const applicableSelected=selected.filter(x=>!x.blocked&&!cycleSet.has(x.id)&&!issues.some(i=>i.id===x.id&&['MISSING_DEPENDENCY','BLOCKED_SELECTED','DEPENDENCY_NOT_SELECTED','SELECTED_CONFLICT'].includes(i.code)));
  const conflictSet=new Set(issues.filter(i=>i.code==='SELECTED_CONFLICT').flatMap(i=>[i.id,i.relatedId]));
  const safeSelected=applicableSelected.filter(x=>!conflictSet.has(x.id));
  const gain=safeSelected.reduce((sum,x)=>sum+x.gain,0);
  const recommendations=items.map(x=>{
    const ownIssues=issues.filter(i=>i.id===x.id||i.relatedId===x.id);
    let status=x.blocked?'blocked':cycleSet.has(x.id)?'dependency-cycle':ownIssues.length?'review-required':x.selected?'selected':'available';
    return {id:x.id,groupId:x.groupId,title:x.title,status,selected:x.selected,gain:x.gain,severity:x.severity,risk:x.risk,fabric:x.fabric,
      priorityScore:rank(x),dependsOn:x.dependsOn,conflictsWith:x.conflictsWith,reason:x.reason,
      rationale:ownIssues.map(i=>i.detail)};
  }).sort((a,b)=>b.priorityScore-a.priorityScore||a.groupId.localeCompare(b.groupId)||a.id.localeCompare(b.id));
  return {version:'27.8',readOnly:true,summary:{total:items.length,selected:selected.length,applicableSelected:safeSelected.length,
      blocked:recommendations.filter(x=>x.status==='blocked').length,reviewRequired:recommendations.filter(x=>x.status==='review-required'||x.status==='dependency-cycle').length,
      activeConflicts:issues.filter(x=>x.code==='SELECTED_CONFLICT').length,dependencyCycles:cycleIds.length,estimatedGain:gain},
    priorityOrder:ordered.filter(x=>!cycleSet.has(x.id)).map(x=>x.id),recommendations,issues,
    scope:'Recommandations calculées à partir des données déclarées. Les gains sont estimatifs, non mesurés. Aucun changement n’est appliqué au diagramme ou aux équipements.'};
}
function rank(x){return (SEVERITY[x.severity]||0)*100+(RISK[x.risk]||0)*20+Math.min(x.gain,19)+(x.selected?2:0);}
export function recommendationsCsv(report){
 const esc=v=>{let s=String(v??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
 const rows=[['ID','Groupe','Correction','Statut','Sélectionnée','Gain estimé','Sévérité','Risque','Fabric','Prérequis','Conflits','Motif']];
 for(const r of report.recommendations)rows.push([r.id,r.groupId,r.title,r.status,r.selected?'oui':'non',r.gain,r.severity,r.risk,r.fabric,r.dependsOn.join('; '),r.conflictsWith.join('; '),[r.reason,...r.rationale].filter(Boolean).join(' | ')]);
 return '\uFEFF'+rows.map(row=>row.map(esc).join(';')).join('\r\n')+'\r\n';
}

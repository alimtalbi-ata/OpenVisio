// OpenVisio v28.4 — inspection documentaire en lecture seule. Auteur : Abdelhalim Talbi.
export function inspectSanSelection(state,id){
 const nodes=Array.isArray(state?.nodes)?state.nodes:[];
 const edges=Array.isArray(state?.edges)?state.edges:[];
 if(!id)return {title:'Sélectionnez un équipement ou une connexion',lines:['Analyse Fabric A/B sur les liens déclarés. Aucun équipement réel interrogé.'],related:[]};
 const node=nodes.find(n=>String(n.id)===String(id));
 const edge=edges.find(e=>String(e.id)===String(id));
 if(!node&&!edge)return {title:'Objet introuvable',lines:[],related:[]};
 const relatedEdges=node?edges.filter(e=>e.from===node.id||e.to===node.id):[edge];
 const fabrics={A:0,B:0,inconnue:0};
 for(const e of relatedEdges){const f=String(e.fabric??e.sanFabric??'').trim().toUpperCase();fabrics[f==='A'||f==='B'?f:'inconnue']++;}
 const title=String(node?.label??node?.name??edge?.label??id);
 const lines=[`Identifiant : ${id}`,`Liens déclarés : ${relatedEdges.length}`,`Fabric A : ${fabrics.A} · Fabric B : ${fabrics.B} · inconnue : ${fabrics.inconnue}`];
 if(node&&relatedEdges.length&&(!fabrics.A||!fabrics.B))lines.push('Attention : redondance A/B non démontrée par les liens documentés.');
 if(fabrics.inconnue)lines.push('Fabric non renseignée : diagnostic incomplet.');
 if(edge)lines.push(`Extrémités : ${edge.from} → ${edge.to}`);
 // Métadonnées documentaires : aucune interrogation de ports physiques.
 const metadata=[];
 const validWwpn=value=>typeof value==='string'&&/^(?:[0-9a-f]{2}:){7}[0-9a-f]{2}$/i.test(value);
 const fmt=(name,obj)=>{
  if(!obj)return;
  for(const field of ['port','fcPort','wwpn','portWwpn']){
   const value=obj[field];if(value===undefined||value===null||String(value).trim()==='')continue;
   if(/wwpn/i.test(field)&&!validWwpn(value)){metadata.push(`${name} ${field} : format WWPN invalide`);continue;}
   metadata.push(`${name} ${field} : ${String(value).slice(0,128)}`);
  }
 };
 fmt('Équipement',node);
 for(const e of relatedEdges)fmt(`Lien ${String(e.id).slice(0,64)}`,e);
 lines.push(...metadata);
 const related=[...new Set(node?relatedEdges.map(e=>e.from===id?e.to:e.from):[edge.from,edge.to])].filter(x=>nodes.some(n=>n.id===x));
 return {title,lines,related};
}

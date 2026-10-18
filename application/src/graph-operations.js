// OpenVisio — opérations pures sur les graphes. Auteur : Abdelhalim Talbi.
export function duplicateSubgraph(nodes,edges,selectedIds,{dx=40,dy=40,idFactory}={}){
 const selected=new Set(selectedIds);
 const originals=nodes.filter(n=>selected.has(n.id));
 const used=new Set([...nodes.map(n=>n.id),...edges.map(e=>e.id)]);
 let sequence=0;
 const fresh=(base)=>{let id;do{id=idFactory?idFactory(base,sequence++):`${base}-copy-${++sequence}`;}while(used.has(id));used.add(id);return id;};
 const ids=new Map(originals.map(n=>[n.id,fresh(n.id)]));
 const copies=originals.map(n=>({...n,id:ids.get(n.id),x:Math.max(0,(Number(n.x)||0)+dx),y:Math.max(0,(Number(n.y)||0)+dy),groupId:null,title:`${n.title||n.type||'Objet'} (copie)`}));
 const links=edges.filter(e=>ids.has(e.from)&&ids.has(e.to)).map(e=>({...e,id:fresh(e.id),from:ids.get(e.from),to:ids.get(e.to),waypoints:Array.isArray(e.waypoints)?e.waypoints.map(p=>({x:p.x+dx,y:p.y+dy})):[]}));
 return {nodes:copies,edges:links,idMap:ids};
}

/** Déplacement rigide d'une sélection, borné par le canevas positif.
 * Le même delta est appliqué à chaque forme pour préserver leur espacement.
 * Retourne des coordonnées sans muter les objets du diagramme.
 */
export function moveSelectionRigid(positions,dx,dy,{grid=0}={}){
 if(!Array.isArray(positions)||!positions.length||![dx,dy].every(Number.isFinite))return new Map();
 const valid=positions.filter(p=>p&&typeof p.id==='string'&&Number.isFinite(p.x)&&Number.isFinite(p.y));
 if(valid.length!==positions.length)return new Map();
 const step=Number.isFinite(grid)&&grid>0?grid:0;
 let minX=Infinity,minY=Infinity;for(const p of valid){if(p.x<minX)minX=p.x;if(p.y<minY)minY=p.y;}
 const quantize=v=>step?Math.round(v/step)*step:v;
 const shiftX=Math.max(-minX,quantize(dx)),shiftY=Math.max(-minY,quantize(dy));
 return new Map(valid.map(p=>[p.id,{x:p.x+shiftX,y:p.y+shiftY}]));
}

// OpenVisio — ordre de superposition des formes. Auteur : Abdelhalim Talbi.
export function reorderShapes(nodes, ids, action) {
 if(!Array.isArray(nodes)||!Array.isArray(ids)) throw new TypeError('Sélection invalide');
 const selected=new Set(ids);
 if(!['front','back','forward','backward'].includes(action)) throw new RangeError('Action inconnue');
 const result=[...nodes];
 if(action==='front') return [...result.filter(n=>!selected.has(n.id)),...result.filter(n=>selected.has(n.id))];
 if(action==='back') return [...result.filter(n=>selected.has(n.id)),...result.filter(n=>!selected.has(n.id))];
 if(action==='forward') {for(let i=result.length-2;i>=0;i--)if(selected.has(result[i].id)&&!selected.has(result[i+1].id)) [result[i],result[i+1]]=[result[i+1],result[i]];}
 if(action==='backward') {for(let i=1;i<result.length;i++)if(selected.has(result[i].id)&&!selected.has(result[i-1].id)) [result[i],result[i-1]]=[result[i-1],result[i]];}
 return result;
}

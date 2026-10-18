/** Modèle pur de l’inspecteur multi-sélection. Auteur : Abdelhalim Talbi. */
export function commonValue(nodes,key){
 if(!Array.isArray(nodes)||nodes.length===0)return {mixed:false,value:null};
 const value=nodes[0]?.[key]??null;
 return nodes.every(node=>(node?.[key]??null)===value)?{mixed:false,value}:{mixed:true,value:null};
}
export function selectionBounds(nodes){
 if(!Array.isArray(nodes)||!nodes.length)return null;
 const valid=nodes.filter(n=>[n.x,n.y,n.w,n.h].every(Number.isFinite));
 if(valid.length!==nodes.length)return null;
 const x=Math.min(...valid.map(n=>n.x)),y=Math.min(...valid.map(n=>n.y));
 const right=Math.max(...valid.map(n=>n.x+n.w)),bottom=Math.max(...valid.map(n=>n.y+n.h));
 return {x,y,width:right-x,height:bottom-y,count:valid.length};
}
export function selectionKinds(nodes){
 return [...new Set((nodes||[]).map(n=>String(n.type||n.kind||'forme')))].sort();
}

// Auteur : Abdelhalim Talbi
export const CATEGORIES=[{id:"all",name:"Toutes"},{id:"favorites",name:"Favoris"},{id:"recent",name:"Récentes"},{id:"compute",name:"Calcul"},{id:"storage",name:"Stockage"},{id:"network",name:"Réseau / SAN"},{id:"cloud",name:"Cloud"}];
export function shapeKey(shape){return `${shape.vendor}:${shape.name}:${shape.type}`;}
export function filterShapes(shapes,{query="",vendor="",category="",favorites=[],recent=[]}={}){
 const words=query.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
 const selected=new Set(favorites);
 const recentlyUsed=new Set(recent);
 return shapes.filter(shape=>{
  const haystack=[shape.name,shape.vendor,shape.subtitle,shape.category,shape.type].join(" ").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase();
  return (!vendor||shape.vendor===vendor)&&(!category||category==="all"||category==="favorites"&&selected.has(shapeKey(shape))||category==="recent"&&recentlyUsed.has(shapeKey(shape))||shape.category===category)&&words.every(word=>haystack.includes(word));
 });
}
export function toggleFavorite(favorites,key){const next=new Set(favorites);if(next.has(key))next.delete(key);else next.add(key);return [...next].sort();}
export function readFavorites(raw){try{const parsed=JSON.parse(raw||"[]");return Array.isArray(parsed)?parsed.filter(x=>typeof x==="string").slice(0,200):[];}catch{return [];}}

export function readRecentShapes(raw){try{const parsed=JSON.parse(raw||"[]");return Array.isArray(parsed)?[...new Set(parsed.filter(x=>typeof x==="string"))].slice(0,12):[];}catch{return [];}}
export function trackRecentShape(recent,key){return [key,...recent.filter(item=>item!==key)].slice(0,12);}

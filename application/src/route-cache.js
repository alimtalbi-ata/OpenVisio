// OpenVisio v41.7 — cache de routes isolé, borné et LRU. Auteur : Abdelhalim Talbi.
// Les routes sont des valeurs : aucune référence mutable ne sort du cache.
export function createRouteValueCache({limit=500,onEvict=()=>{}}={}){
 if(!Number.isSafeInteger(limit)||limit<1)throw new RangeError('Invalid route cache limit');
 const entries=new Map();let hits=0,misses=0,evictions=0;
 return Object.freeze({
  get(key){if(typeof key!=='string')throw TypeError('Invalid route key');if(!entries.has(key)){misses++;return undefined;}
   const stored=entries.get(key);entries.delete(key);entries.set(key,stored);hits++;return structuredClone(stored);},
  set(key,route){if(typeof key!=='string'||!key.length)throw TypeError('Invalid route key');
   const safe=structuredClone(route);if(entries.has(key))entries.delete(key);
   else if(entries.size>=limit){const oldest=entries.keys().next().value;entries.delete(oldest);onEvict(oldest);evictions++;}
   entries.set(key,safe);return structuredClone(safe);},
  delete(key){if(typeof key!=='string')throw TypeError('Invalid route key');const removed=entries.delete(key);if(removed)onEvict(key);return removed;},
  clear(){for(const key of entries.keys())onEvict(key);entries.clear();},
  stats(){return {size:entries.size,hits,misses,evictions,limit,hitRate:hits+misses?hits/(hits+misses):0};}
 });
}

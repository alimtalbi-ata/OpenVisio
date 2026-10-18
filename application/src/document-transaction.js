// OpenVisio — transactions documentaires. Auteur : Abdelhalim Talbi.
// Les modifications ne sont publiées qu’après validation complète.
export function applyDocumentTransaction(current, mutate, validate){
 if(!current || typeof current!=="object" || typeof mutate!=="function" || typeof validate!=="function") throw new TypeError("Transaction invalide");
 const draft=structuredClone(current);
 mutate(draft);
 const accepted=validate(draft);
 if(accepted===false)throw new Error("Document refusé par la validation");
 return draft;
}
export function commitDocumentState(target, replacement){
 if(!target || !replacement || typeof target!=="object" || typeof replacement!=="object" || Array.isArray(target)||Array.isArray(replacement))throw new TypeError("État documentaire invalide");
 for(const key of Object.keys(target))if(!Object.hasOwn(replacement,key))delete target[key];
 Object.assign(target,replacement);
 touchDocumentRevision(target);
 return target;
}

// v41.4 — révision documentaire monotone, indépendante des champs sérialisés.
// La révision est attachée à l'objet racine publié, pas à une copie transitoire.
const documentRevisions = new WeakMap();
export function documentRevision(document){
 if(!document || typeof document!=="object" || Array.isArray(document))throw new TypeError("Document invalide");
 return documentRevisions.get(document) ?? 0;
}
export function touchDocumentRevision(document){
 const current=documentRevision(document);
 if(current===Number.MAX_SAFE_INTEGER)throw new RangeError("Révision épuisée");
 const next=current+1;
 documentRevisions.set(document,next);
 return next;
}

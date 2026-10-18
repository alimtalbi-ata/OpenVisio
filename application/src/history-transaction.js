// OpenVisio v20.3 — historique transactionnel, auteur Abdelhalim Talbi.
import {snapshot,restore} from './model.js';
import {commitDocumentState} from './document-transaction.js';
export function createHistory(limit=60,{captureExtras=()=>null,restoreExtras=()=>{},validateExtras=()=>{}}={}){
 if(!Number.isInteger(limit)||limit<1)throw Error('Limite historique invalide');
 const undo=[],redo=[];
 const capture=state=>JSON.stringify({version:2,diagram:snapshot(state),extras:captureExtras()});
 const decode=raw=>{const data=JSON.parse(raw);if(data?.version===2){if(typeof data.diagram!=="string")throw Error("Instantané historique invalide");return {diagram:data.diagram,extras:data.extras};}return {diagram:raw,extras:null};};
 return {
  undo,redo,
  checkpoint(state){undo.push(capture(state));if(undo.length>limit)undo.shift();redo.length=0;},
  travel(state,source,destination){if(source!==undo&&source!==redo||destination!==undo&&destination!==redo||source===destination)throw Error("Direction historique invalide");if(!source.length)return false;const raw=source[source.length-1];const entry=decode(raw);const parsed=JSON.parse(entry.diagram);if(!parsed||!Array.isArray(parsed.nodes)||!Array.isArray(parsed.edges))throw Error("Instantané historique invalide");const restored=restore(entry.diagram);if(entry.extras!==null)validateExtras(entry.extras);const current=capture(state);source.pop();destination.push(current);if(destination.length>limit)destination.shift();commitDocumentState(state,restored);if(entry.extras!==null)restoreExtras(entry.extras);return true;},
  cancelCheckpoint(previousRedo){if(!undo.length)return false;if(!Array.isArray(previousRedo))throw Error("Pile redo invalide");undo.pop();redo.splice(0,redo.length,...previousRedo);return true;},
  reset(){undo.length=0;redo.length=0;}
 };
}

import {validateZones} from './zoning-document.js';

// Préparation pure : aucune mutation ni entrée d’historique avant validation.
export function planZoningUpdate(current, input){
 const next=validateZones(input);
 const previous=validateZones(current);
 return {next,changed:JSON.stringify(previous)!==JSON.stringify(next)};
}
export function commitZoningUpdate(current,input,checkpoint,apply){
 const plan=planZoningUpdate(current,input);
 if(!plan.changed)return false;
 checkpoint();
 apply(plan.next);
 return true;
}

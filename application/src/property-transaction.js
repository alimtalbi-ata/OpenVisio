// OpenVisio v20.0 — validation atomique des modifications d'inspecteur.
// Auteur : Abdelhalim Talbi
import {parseSanProperty} from './san-properties.js';
import {parseLunMasking} from './lun-masking.js';
import {parsePorts,portChangeImpact} from './ports.js';
export function planNodeProperty(node,key,value,edges=[]){
 let next=value;
 if(key==='ports'){
  next=parsePorts(value);
  const impact=portChangeImpact(node,next,edges);
  if(impact.hasImpact)return {ok:false,reason:'connected-ports',impact};
 }else if(key==='lunMasking')next=parseLunMasking(value,node.luns);
 else if(['hbas','wwpns','luns','multipath'].includes(key))next=parseSanProperty(key,value);
 else if(['x','y'].includes(key))next=Number(value)||0;
 const changed=JSON.stringify(node[key])!==JSON.stringify(next);
 return {ok:true,changed,key,value:next};
}
export function applyNodeProperty(node,plan){
 if(!plan?.ok)throw Error('Modification non validée');
 if(plan.changed)node[plan.key]=plan.value;
 return plan.changed;
}

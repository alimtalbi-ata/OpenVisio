import test from 'node:test';
import assert from 'node:assert/strict';
import {planNodeProperty,applyNodeProperty} from '../src/property-transaction.js';
const node=()=>({id:'n1',ports:['FC0','FC1'],x:10,title:'Storage'});
test('transaction : refus de supprimer un port connecté sans mutation',()=>{
 const n=node(),edges=[{id:'e1',from:'n1',to:'n2',sourceInterface:'FC0'}];
 const plan=planNodeProperty(n,'ports','FC1',edges);
 assert.equal(plan.ok,false);assert.deepEqual(n.ports,['FC0','FC1']);
});
test('transaction : validation puis application atomique',()=>{
 const n=node(),plan=planNodeProperty(n,'ports','FC0;FC2');
 assert.equal(plan.ok,true);assert.deepEqual(n.ports,['FC0','FC1']);
 assert.equal(applyNodeProperty(n,plan),true);assert.deepEqual(n.ports,['FC0','FC2']);
});
test('transaction : modification identique sans entrée historique',()=>{
 const n=node();assert.equal(planNodeProperty(n,'x','10').changed,false);
 assert.equal(planNodeProperty(n,'ports','FC0;FC1').changed,false);
});
test('transaction : saisie invalide rejetée avant mutation',()=>{
 const n=node();assert.throws(()=>planNodeProperty(n,'ports','FC0;FC0'));assert.deepEqual(n.ports,['FC0','FC1']);
});
test('transaction : propriété simple sans mutation avant validation',()=>{
 const n=node(),plan=planNodeProperty(n,'title','New storage');
 assert.equal(n.title,'Storage');applyNodeProperty(n,plan);assert.equal(n.title,'New storage');
});
test('transaction : plan refusé non applicable',()=>assert.throws(()=>applyNodeProperty(node(),{ok:false})));

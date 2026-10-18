import test from 'node:test';
import assert from 'node:assert/strict';
import {edgeVisualSignature,nodeVisualSignature} from '../src/renderer.js';

test('v23.3 : signature stable pour des liaisons équivalentes',()=>{
 const e={id:'fc-1',from:'a',to:'b',label:'FC'};
 assert.equal(edgeVisualSignature(e,'M 0 0 L 10 10'),edgeVisualSignature({...e},'M 0 0 L 10 10'));
});
test('v23.3 : modification du tracé invalide la signature',()=>{
 const e={id:'fc-1'};
 assert.notEqual(edgeVisualSignature(e,'M 0 0'),edgeVisualSignature(e,'M 1 0'));
});
test('v23.3 : sélection et alerte invalident la signature',()=>{
 const e={id:'fc-1'};const base=edgeVisualSignature(e,'M 0 0');
 assert.notEqual(base,edgeVisualSignature(e,'M 0 0',true));
 assert.notEqual(base,edgeVisualSignature(e,'M 0 0',false,true));
});
test('v23.3 : changement de libellé invalide la signature',()=>{
 assert.notEqual(edgeVisualSignature({id:'a',label:'A'},'M 0 0'),edgeVisualSignature({id:'a',label:'B'},'M 0 0'));
});
test('v23.3 : les métadonnées CMDB des extrémités ne font pas partie de la signature de liaison',()=>{
 const edge={id:'e',from:'a',to:'b'};const node={id:'a',x:10,metadata:{asset:'x'}};
 const before=edgeVisualSignature(edge,'M 10 10 L 20 20');node.metadata.asset='y';
 assert.equal(before,edgeVisualSignature(edge,'M 10 10 L 20 20'));
});
test('v23.3 : signature de nœud détecte les mutations et la sélection',()=>{
 const n={id:'a',x:1,title:'SW'};const first=nodeVisualSignature(n);
 n.x=2;assert.notEqual(first,nodeVisualSignature(n));
 assert.notEqual(nodeVisualSignature(n),nodeVisualSignature(n,true));
});
test('v23.3 : entrées invalides rejetées',()=>{
 assert.throws(()=>edgeVisualSignature(null,'M 0 0'),TypeError);
 assert.throws(()=>edgeVisualSignature({id:'e'},null),TypeError);
 assert.throws(()=>nodeVisualSignature(null),TypeError);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {buildRouteClearanceView} from '../src/route-clearance-view.js';
test('classe erreurs, examens et routes conformes',()=>{
 const result=buildRouteClearanceView({edges:[{edgeId:'c',errors:0,reviews:0},{edgeId:'b',errors:0,reviews:1},{edgeId:'a',errors:2,reviews:1}]});
 assert.deepEqual(result.items.map(x=>x.severity),['error','review','ok']);
 assert.equal(result.errors,1);assert.equal(result.reviews,1);
});
test('ne modifie pas les diagnostics originaux',()=>{
 const source={edges:[{edgeId:'x',errors:1,issues:[{code:'collision'}]}]};
 const view=buildRouteClearanceView(source);view.items[0].issues[0].code='changed';
 assert.equal(source.edges[0].issues[0].code,'collision');
});
test('rejette une entrée malformée',()=>assert.throws(()=>buildRouteClearanceView({}),TypeError));

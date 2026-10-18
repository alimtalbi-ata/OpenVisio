import test from 'node:test';import assert from 'node:assert/strict';
import {planCollisionFreeGrid,applyGridPlan} from '../src/layout.js';
const nodes=[{id:'a',x:7,y:4,w:120,h:60},{id:'b',x:7,y:4,w:40,h:120},{id:'c',x:2,y:8,w:200,h:30},{id:'d',x:9,y:2,w:50,h:80}];
test('grid does not mutate input and is deterministic',()=>{const before=structuredClone(nodes);const a=planCollisionFreeGrid(nodes,{columns:2});assert.deepEqual(nodes,before);assert.deepEqual(a,planCollisionFreeGrid(nodes,{columns:2}));});
test('grid rectangles never overlap',()=>{const p=planCollisionFreeGrid(nodes,{columns:2,gap:16});for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++){const a=p[i],b=p[j];assert.ok(a.x+a.w<=b.x||b.x+b.w<=a.x||a.y+a.h<=b.y||b.y+b.h<=a.y);}});
test('plan applies by id not order',()=>{const p=planCollisionFreeGrid(nodes,{columns:2});const target=structuredClone(nodes).reverse();applyGridPlan(target,p);for(const n of target)assert.equal(n.x,p.find(v=>v.id===n.id).x);});
test('rejects invalid input',()=>{assert.throws(()=>planCollisionFreeGrid([{id:1,x:0,y:0,w:0,h:2}]));assert.throws(()=>planCollisionFreeGrid([nodes[0],nodes[0]]));assert.throws(()=>planCollisionFreeGrid(nodes,{gap:-1}));});

import test from 'node:test';import assert from 'node:assert/strict';import{readFileSync}from'node:fs';import{planCollisionFreeGrid,applyGridPlan}from'../src/layout.js';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('action de placement accessible dans le canevas',()=>assert.match(html,/id="autoGridLayout"/));
test('aperçu et confirmation avant modification',()=>{assert.match(main,/planGrid|planCollisionFreeGrid/);assert.match(main,/if\(!confirm\(/);assert.match(main,/saveUndo\(\);applyGridPlan/)});
test('calcul pur et application contrôlée',()=>{const nodes=[{id:'a',x:20,y:40,w:50,h:40},{id:'b',x:20,y:40,w:90,h:40}];const p=planCollisionFreeGrid(nodes);assert.equal(nodes[1].x,20);applyGridPlan(nodes,p);assert.notEqual(nodes[1].x,nodes[0].x)});

import test from 'node:test';import assert from 'node:assert/strict';import {duplicateSubgraph} from '../src/graph-operations.js';
const nodes=[{id:'a',x:10,y:20,title:'A',groupId:'g'},{id:'b',x:100,y:20,title:'B'},{id:'c',x:300,y:20,title:'C'}];
const edges=[{id:'e1',from:'a',to:'b',waypoints:[{x:50,y:60}]},{id:'e2',from:'b',to:'c',waypoints:[]}];
test('duplique seulement les noeuds sélectionnés',()=>{const g=duplicateSubgraph(nodes,edges,['a','b']);assert.equal(g.nodes.length,2);assert.equal(g.edges.length,1);assert.equal(g.nodes[0].x,50);assert.equal(g.nodes[0].groupId,null)});
test('préserve la connectivité interne',()=>{const g=duplicateSubgraph(nodes,edges,['a','b']);assert.equal(g.edges[0].from,g.idMap.get('a'));assert.equal(g.edges[0].to,g.idMap.get('b'));assert.equal(g.edges[0].waypoints[0].x,90)});
test('ignore les liens externes',()=>assert.equal(duplicateSubgraph(nodes,edges,['b']).edges.length,0));
test('IDs uniques même si factory produit des collisions',()=>{const g=duplicateSubgraph(nodes,edges,['a','b'],{idFactory:(base,i)=>i<2?'a':base+'-'+i});assert.equal(new Set([...nodes,...g.nodes,...edges,...g.edges].map(x=>x.id)).size,8)});
test('ne modifie pas les objets sources',()=>{const before=JSON.stringify({nodes,edges});duplicateSubgraph(nodes,edges,['a','b']);assert.equal(JSON.stringify({nodes,edges}),before)});

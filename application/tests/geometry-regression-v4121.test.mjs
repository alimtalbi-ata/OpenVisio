import test from 'node:test';
import assert from 'node:assert/strict';
import {compareRoutingGeometry,affectedGraphElements,routingGeometrySignature} from '../src/renderer.js';
const route=(points)=>({points});
test('v41.21 geometry: route equivalent under tolerance',()=>{
 const a=new Map([['fc1',route([{x:0,y:0},{x:50,y:40}])]]);
 const b=new Map([['fc1',route([{x:0,y:0},{x:50.0005,y:40}])]]);
 assert.equal(compareRoutingGeometry(a,b,{tolerance:.001}).equivalent,true);
 assert.deepEqual(compareRoutingGeometry(a,b,{tolerance:.0001}).divergentEdges,['fc1']);
});
test('v41.21 geometry: missing, malformed and nonfinite paths rejected',()=>{
 const a=new Map([['fc1',route([{x:0,y:0}])],['fc2',route([{x:2,y:3}])]]);
 const b=new Map([['fc1',route([{x:NaN,y:0}])]]);
 assert.deepEqual(compareRoutingGeometry(a,b).divergentEdges,['fc1','fc2']);
});
test('v41.21 geometry: equipment movement affects attached edges only',()=>{
 const before={nodes:[{id:'a',x:0,y:0},{id:'b',x:100,y:0},{id:'c',x:200,y:0}],edges:[{id:'ab',from:'a',to:'b'},{id:'bc',from:'b',to:'c'}]};
 const after=structuredClone(before);after.nodes[0].x=10;
 const diff=affectedGraphElements(before,after);
 assert.deepEqual([...diff.nodes],['a']);assert.deepEqual([...diff.edges],['ab']);assert.equal(diff.geometryChanged,true);
});
test('v41.21 geometry: appearance-only changes do not change routing signature',()=>{
 const a={nodes:[{id:'a',x:0,y:0,w:50,h:50,label:'A'}],edges:[]};
 const b=structuredClone(a);b.nodes[0].label='B';
 assert.equal(routingGeometrySignature(a),routingGeometrySignature(b));
});

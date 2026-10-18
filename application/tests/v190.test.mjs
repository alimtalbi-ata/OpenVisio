import test from 'node:test';
import assert from 'node:assert/strict';
import {detectCableCrossings,polylineCrosses,routePolyline} from '../src/cable-crossings.js';
const n=(id,x,y)=>({id,x,y,w:20,h:20});
test('segments orthogonaux: croisement réel',()=>{
 const nodes=[n('a',0,0),n('b',200,100),n('c',80,-40),n('d',80,160)];
 const edges=[{id:'ab',from:'a',to:'b',style:'orthogonal'},{id:'cd',from:'c',to:'d',style:'straight'}];
 assert.equal(detectCableCrossings(nodes,edges).length,1);
});
test('les points de passage modifient le diagnostic',()=>{
 const nodes=[n('a',0,0),n('b',200,0),n('c',100,-100),n('d',100,100)];
 const edges=[{id:'ab',from:'a',to:'b',waypoints:[{x:20,y:-160},{x:220,y:-160}]},{id:'cd',from:'c',to:'d',style:'straight'}];
 assert.equal(detectCableCrossings(nodes,edges).length,0);
});
test('segments colinéaires ne sont pas des croisements stricts',()=>assert.equal(polylineCrosses([{x:0,y:0},{x:10,y:0}],[{x:5,y:0},{x:15,y:0}]),false));
test('liaisons partageant un noeud ignorées',()=>assert.deepEqual(detectCableCrossings([n('a',0,0),n('b',100,0),n('c',0,100)],[{id:'x',from:'a',to:'b'},{id:'y',from:'a',to:'c'}]),[]));
test('géométrie invalide sans crash',()=>assert.equal(routePolyline({from:'a',to:'missing'},new Map([['a',n('a',0,0)]])),null));

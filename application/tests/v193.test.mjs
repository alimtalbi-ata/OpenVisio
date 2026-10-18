import test from 'node:test';
import assert from 'node:assert/strict';
import {detectCableCrossings,svgPathPolyline} from '../src/cable-crossings.js';
const nodes=Array.from({length:500},(_,i)=>({id:`n${i}`,x:i*200,y:0,w:10,h:10}));
test('500 disjoint cables have no crossings',()=>{const edges=Array.from({length:250},(_,i)=>({id:`e${i}`,from:`n${2*i}`,to:`n${2*i+1}`,style:'straight'}));assert.deepEqual(detectCableCrossings(nodes,edges),[])});
test('sweep catches crossed rendered routes',()=>{const edges=[{id:'a',from:'n0',to:'n1'},{id:'b',from:'n2',to:'n3'}];const routes=new Map([['a',[{x:0,y:0},{x:10,y:10}]],['b',[{x:0,y:10},{x:10,y:0}]]]);assert.equal(detectCableCrossings(nodes,edges,routes).length,1)});
test('sweep excludes endpoint contacts',()=>{const edges=[{id:'a',from:'n0',to:'n1'},{id:'b',from:'n2',to:'n3'}];const routes=new Map([['a',[{x:0,y:0},{x:10,y:10}]],['b',[{x:10,y:10},{x:20,y:0}]]]);assert.deepEqual(detectCableCrossings(nodes,edges,routes),[])});
test('SVG parser rejects unsupported curves',()=>assert.equal(svgPathPolyline('M 0 0 Q 1 1 2 2'),null));

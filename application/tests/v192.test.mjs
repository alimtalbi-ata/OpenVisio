import test from 'node:test';
import assert from 'node:assert/strict';
import {svgPathPolyline,detectCableCrossings} from '../src/cable-crossings.js';
test('reject malformed SVG separators',()=>assert.equal(svgPathPolyline('M 0 0 ! L 10 10'),null));
test('reject unsupported SVG relative path',()=>assert.equal(svgPathPolyline('m 0 0 l 10 10'),null));
test('reject broken exponent',()=>assert.equal(svgPathPolyline('M 1e 2 L 3 4'),null));
test('reject huge SVG input',()=>assert.equal(svgPathPolyline('M 0 0 '+ 'L 1 1 '.repeat(20000)),null));
test('accept commas and negative coordinates',()=>assert.deepEqual(svgPathPolyline('M -1,2 L 3,-4'),[{x:-1,y:2},{x:3,y:-4}]));
test('reject tangential bounding boxes',()=>{const nodes=[{id:'a',x:0,y:0,w:2,h:2},{id:'b',x:10,y:10,w:2,h:2},{id:'c',x:10,y:0,w:2,h:2},{id:'d',x:20,y:10,w:2,h:2}];const edges=[{id:'a',from:'a',to:'b'},{id:'b',from:'c',to:'d'}];const routes=new Map([['a',[{x:0,y:0},{x:10,y:10}]],['b',[{x:10,y:0},{x:20,y:10}]]]);assert.equal(detectCableCrossings(nodes,edges,routes).length,0)});

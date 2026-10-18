import test from 'node:test';import assert from 'node:assert/strict';import {buildCanvasSanOverlay} from '../src/san-canvas-overlay.js';
test('projection maps declared object IDs',()=>{const o=buildCanvasSanOverlay([{id:'C1',selected:true,gain:10,affectedObjectIds:['sw1']}],{objects:[{id:'sw1'}],connections:[]});assert.equal(o.marks[0].objectId,'sw1');assert.equal(o.readOnly,true)});
test('unknown objects generate warnings',()=>{const o=buildCanvasSanOverlay([{id:'C1',affectedObjectIds:['missing']}],{objects:[]});assert.equal(o.marks.length,0);assert.ok(o.warnings.length)});
test('source objects unchanged',()=>{const d={objects:[{id:'s'}],connections:[]},c=[{id:'C',affectedObjectIds:['s']}],before=JSON.stringify([d,c]);buildCanvasSanOverlay(c,d);assert.equal(JSON.stringify([d,c]),before)});
test('invalid correction list rejected',()=>assert.throws(()=>buildCanvasSanOverlay({},{})));

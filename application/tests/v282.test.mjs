import test from 'node:test';
import assert from 'node:assert/strict';
import {buildCanvasSanOverlay} from '../src/san-canvas-overlay.js';
test('v28.2 empty overlay is read only',()=>{const r=buildCanvasSanOverlay([],{objects:[],connections:[]});assert.equal(r.readOnly,true);assert.deepEqual(r.connectionMarks,[])});
test('v28.2 invalid connections ignored',()=>{const r=buildCanvasSanOverlay([],{objects:[],connections:[{id:'x',fabric:'A'}]});assert.deepEqual(r.connectionIds,[])});

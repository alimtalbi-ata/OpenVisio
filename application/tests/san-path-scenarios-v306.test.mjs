import test from 'node:test';import assert from 'node:assert/strict';import {buildPathFailureOverlay} from '../src/san-path-scenarios-v306.js';
const doc={nodes:[{id:'h',type:'server'},{id:'a',type:'switch'},{id:'b',type:'switch'},{id:'s',type:'storage'}],edges:[{id:'e1',from:'h',to:'a',fabric:'A'},{id:'e2',from:'a',to:'s',fabric:'A'},{id:'e3',from:'h',to:'b',fabric:'B'},{id:'e4',from:'b',to:'s',fabric:'B'}]};
test('Fabric A loss exposes exact lost and surviving edge IDs',()=>{const r=buildPathFailureOverlay(doc,'h','s','A');assert.deepEqual(r.lostIds,['e1','e2']);assert.deepEqual(r.survivingIds,['e3','e4']);assert.equal(r.summary.lost,1);});
test('Fabric B loss is symmetric',()=>{const r=buildPathFailureOverlay(doc,'h','s','B');assert.deepEqual(r.lostIds,['e3','e4']);assert.deepEqual(r.survivingIds,['e1','e2']);});
test('reject unsupported fabric',()=>assert.throws(()=>buildPathFailureOverlay(doc,'h','s','X'),RangeError));
test('missing pair has no invented paths',()=>{const r=buildPathFailureOverlay(doc,'absent','s','A');assert.equal(r.summary.baseline,0);assert.deepEqual(r.lostIds,[]);});

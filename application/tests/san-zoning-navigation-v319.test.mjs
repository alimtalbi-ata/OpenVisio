import test from 'node:test';import assert from 'node:assert/strict';
import {resolveZoningTargets,zoningProvenance} from '../src/san-zoning-navigation-v319.js';
test('matches unique exact switch',()=>assert.deepEqual(resolveZoningTargets({switch:'SW-A'},{objects:[{id:'sw-1',name:'SW-A'}]}),{ids:['sw-1'],status:'EXACT_SWITCH_MATCH'}));
test('does not guess when ambiguous',()=>assert.equal(resolveZoningTargets({switch:'SW-A'},{objects:[{id:'1',name:'SW-A'},{id:'2',name:'SW-A'}]}).status,'AMBIGUOUS'));
test('does not guess absent switch',()=>assert.deepEqual(resolveZoningTargets({switch:'SW-B'},{objects:[{id:'1',name:'SW-A'}]}).ids,[]));
test('preserves source provenance',()=>assert.match(zoningProvenance({fabric:'A',vsan:'10',zone:'Z1',sourceLines:[3,8]}),/3, 8/));

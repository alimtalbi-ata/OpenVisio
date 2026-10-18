import test from 'node:test';import assert from 'node:assert/strict';import {buildSanContext,correctionObjectIds} from '../src/san-context.js';
const overlay={marks:[{objectId:'h1',correctionId:'c1'},{objectId:'h1',correctionId:'c1'},{objectId:'s1',correctionId:'c1'}],warnings:[]};const diagram={objects:[{id:'h1',name:'Host'},{id:'s1'}],connections:[{id:'fc1',sourceId:'h1',targetId:'s1',fabric:'A'}]};const corrections=[{id:'c1',title:'Zoning',risk:'low'}];
test('context includes corrections and FC peers',()=>{const c=buildSanContext(overlay,corrections,diagram,'h1');assert.equal(c.name,'Host');assert.equal(c.corrections.length,1);assert.equal(c.paths[0].peerId,'s1')});
test('unknown object is explicit',()=>assert.equal(buildSanContext(overlay,corrections,diagram,'missing').found,false));
test('navigation deduplicates object ids',()=>assert.deepEqual(correctionObjectIds(overlay,'c1'),['h1','s1']));
test('input diagram is not modified',()=>{const before=JSON.stringify(diagram);buildSanContext(overlay,corrections,diagram,'h1');assert.equal(JSON.stringify(diagram),before)});

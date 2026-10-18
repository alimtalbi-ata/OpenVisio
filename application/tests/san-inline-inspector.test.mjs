import test from 'node:test';import assert from 'node:assert/strict';import {inspectSanSelection} from '../src/san-inline-inspector.js';
const s={nodes:[{id:'host',label:'Serveur'},{id:'array',label:'Baie'}],edges:[{id:'e1',from:'host',to:'array',fabric:'A'},{id:'e2',from:'host',to:'array',fabric:'B'}]};
test('redondance documentée',()=>{const r=inspectSanSelection(s,'host');assert.match(r.lines.join(' '),/Fabric A : 1 · Fabric B : 1/);assert.equal(r.related[0],'array')});
test('fabric absente détectée',()=>{const r=inspectSanSelection({...s,edges:[s.edges[0]]},'host');assert.match(r.lines.join(' '),/redondance/)});
test('entrée vide',()=>assert.equal(inspectSanSelection(s,null).related.length,0));
test('lien inspectable',()=>assert.match(inspectSanSelection(s,'e1').lines.join(' '),/host → array/));

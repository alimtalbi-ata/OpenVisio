import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('v30.1 UI and package version synchronized',()=>{const v=JSON.parse(read('package.json')).version.replace(/\.0$/,'');assert.ok(read('index.html').includes('<title>OpenVisio v'+v));assert.ok(read('index.html').includes('Atelier d’architecture · v'+v));});
test('v30.1 resilience panel retained',()=>{for(const id of ['sanResiliencePanel','sanResRows','sanResPriority','sanResRun'])assert.ok(read('index.html').includes('id="'+id+'"'));});

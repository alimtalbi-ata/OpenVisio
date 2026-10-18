import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('export recovery explicitly uses signed SHA256 record',()=>{assert.match(source,/recoveryVerifiedExportBtn/);assert.match(source,/await createRecoveryRecord/);});
test('restore checks integrity before decoding and requires confirmation',()=>{const start=source.indexOf("recoveryFileInput.addEventListener('change'");const block=source.slice(start,start+1400);assert.match(block,/await verifyRecoveryRecord/);assert.match(block,/if\(!result.valid\)/);assert.match(block,/window.confirm/);assert.ok(block.indexOf('window.confirm')<block.indexOf('Object.assign'));});
test('restore rejects oversized files and validates graph and zones',()=>{assert.match(source,/file.size>25\*1024\*1024/);assert.match(source,/restore\(doc.graph\)/);assert.match(source,/validateZones\(doc.zones\)/);});

import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
test('v41.47 release metadata consistent across Windows deliverables',()=>{
 const r=spawnSync(process.execPath,['windows/verify-release.mjs'],{cwd:new URL('../',import.meta.url),encoding:'utf8'});
 assert.equal(r.status,0,r.stdout+r.stderr);
});
test('v41.47 build entrypoint is a forwarding wrapper',()=>{
 const s=readFileSync(new URL('../Build-Windows-Installer.cmd',import.meta.url),'utf8');
 assert.match(s,/call.*Build-OpenVisio-Windows\.cmd/i);
});

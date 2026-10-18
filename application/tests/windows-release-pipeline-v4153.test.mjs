import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const ps=readFileSync(new URL('../windows/Invoke-Windows-Release-Pipeline.ps1',import.meta.url),'utf8');
const cmd=readFileSync(new URL('../Qualify-Release-Windows.cmd',import.meta.url),'utf8');
test('pipeline includes build, native/portable startup and installer E2E',()=>{for(const key of ['build_installer_and_portable','native_startup','portable_startup','installer_e2e','artifact_integrity'])assert.ok(ps.includes(key),key)});
test('pipeline produces JSON evidence and fails closed',()=>{assert.match(ps,/pipeline-v' \+ \$version \+ '\.json/);assert.match(ps,/status='FAIL'/);assert.match(ps,/exit 1/)});
test('single Windows qualification entry point delegates to pipeline',()=>assert.match(cmd,/Invoke-Windows-Release-Pipeline\.ps1/));

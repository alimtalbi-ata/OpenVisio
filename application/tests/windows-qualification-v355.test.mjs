import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = p => readFileSync(p,'utf8');
test('v35.8 qualification propagates nested native smoke exit code',()=>assert.match(read('windows/Qualify-Windows-Release.ps1'),/Native smoke exit code \$LASTEXITCODE/));
test('v35.8 qualification propagates nested installer exit code',()=>assert.match(read('windows/Qualify-Windows-Release.ps1'),/Installer E2E exit code \$LASTEXITCODE/));
test('v35.8 qualification records stack trace for failures',()=>assert.match(read('windows/Qualify-Windows-Release.ps1'),/ScriptStackTrace/));
test('v35.8 qualification returns success only for PASS',()=>{const s=read('windows/Qualify-Windows-Release.ps1');assert.match(s,/if \(\$report.status -eq 'FAIL'\) \{ exit 1 \}/);assert.match(s,/if \(\$report.status -eq 'PARTIAL'\) \{ exit 2 \}/);assert.match(s,/exit 0/);});
test('v35.8 build output and Inno filename agree',()=>{const v=JSON.parse(read('package.json')).version.replace(/\.0$/,'');assert.ok(read('Build-OpenVisio-Windows.cmd').includes(`OpenVisio-Setup-v${v}-x64.exe`));assert.ok(read('windows/installer/OpenVisio.iss').includes(`OutputBaseFilename=OpenVisio-Setup-v${v}-x64`));});

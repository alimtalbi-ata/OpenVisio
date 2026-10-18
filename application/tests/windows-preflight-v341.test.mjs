import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read=(p)=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('v34.1 runs source preflight before SDK download',()=>{const s=read('Build-OpenVisio-Windows.cmd');assert.ok(s.indexOf('Preflight-Windows.ps1') < s.indexOf('dotnet-install.ps1'));});
test('v34.1 checks mandatory assets and version',()=>{const s=read('windows/Preflight-Windows.ps1');assert.match(s,/src\/main.js/);assert.match(s,/\$escapedVersion/);});
test('v34.1 installer has installation logging enabled',()=>{assert.match(read('windows/installer/OpenVisio.iss'),/SetupLogging=yes/);});

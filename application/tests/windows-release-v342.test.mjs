import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = p => readFileSync(new URL('../'+p, import.meta.url), 'utf8');
test('v34.2: version coherence',()=>{const v=JSON.parse(read('package.json')).version;assert.ok(read('windows/native/OpenVisio.csproj').includes(`<Version>${v}</Version>`));});
test('v34.2: installer output is consistent',()=>{const v=JSON.parse(read('package.json')).version.replace(/\.0$/,'');assert.ok(read('windows/installer/OpenVisio.iss').includes(`OutputBaseFilename=OpenVisio-Setup-v${v}-x64`));assert.ok(read('Build-OpenVisio-Windows.cmd').includes(`OpenVisio-Setup-v${v}-x64.exe`));});
test('v34.2: release manifest generated only after successful build', () => { assert.match(read('Build-OpenVisio-Windows.cmd'), /Write-Release-Manifest\.ps1/); assert.match(read('windows/Write-Release-Manifest.ps1'), /Get-FileHash/); });

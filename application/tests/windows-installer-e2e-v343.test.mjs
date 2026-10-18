import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=(p)=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('installer E2E exercises install, launch and uninstall',()=>{const s=read('windows/Test-Installer-E2E.ps1');for(const term of ['/VERYSILENT','OpenVisio.exe','wwwroot/index.html','HasExited','unins000.exe','finally']) assert.ok(s.includes(term),term);});
test('Windows workflow runs installer E2E',()=>assert.match(read('.github/workflows/windows-release.yml'),/Test-Installer-E2E\.ps1/));
test('version synchronized',()=>{const v=JSON.parse(read('package.json')).version;assert.ok(read('windows/installer/OpenVisio.iss').includes(`#define AppVersion \"${v}\"`));});

import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('v33.1 launcher connected to main page',()=>{assert.match(read('index.html'),/workspace-command-v331\.js/);assert.match(read('index.html'),/workspace-v331\.css/);});
test('v33.1 keyboard accessible command search',()=>{const s=read('src/workspace-command-v331.js');assert.match(s,/ctrlKey/);assert.match(s,/Escape/);assert.match(s,/aria-modal/);});
test('v33.1 installer run entries correctly placed',()=>{const s=read('windows/installer/OpenVisio.iss');const run=s.split('[Run]')[1].split('[Code]')[0];assert.match(run,/WebView2RuntimeInstallerX64/);assert.match(run,/OpenVisio\.exe/);});
test('v33.1 installer output checked',()=>{const v=JSON.parse(read('package.json')).version.replace(/\.0$/,'');assert.ok(read('Build-OpenVisio-Windows.cmd').includes(`OpenVisio-Setup-v${v}-x64.exe`));});

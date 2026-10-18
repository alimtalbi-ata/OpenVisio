import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=(p)=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('recette v36.3 vérifie noeuds ET liens après réouverture',()=>{
 const s=read('tests/browser-functional-v359.py');
 for(const part of ['before_nodes','before_edges','after_nodes==before_nodes','after_edges==before_edges','json_reopen_graph_fidelity']) assert.ok(s.includes(part),part);
});
test('qualification Windows utilise la recette v36.2',()=>{
 const scripts=['windows/Qualify-Windows-Release.ps1','windows/Test-Graphic-UI.ps1','windows/Test-Functional-UI.ps1'];
 const found=scripts.filter(p=>{try{return read(p).includes('browser-functional-v361.py')}catch{return false}});
 assert.ok(found.length>0,'Le scénario v36.3 doit être relié à la qualification');
});
test('build et installateur sont alignés en v36.2',()=>{const v=JSON.parse(read('package.json')).version;const short=v.replace(/\.0$/,'');assert.ok(read('Build-OpenVisio-Windows.cmd').includes(`OpenVisio-Setup-v${short}-x64.exe`));assert.ok(read('windows/installer/OpenVisio.iss').includes(`#define AppVersion \"${v}\"`));});

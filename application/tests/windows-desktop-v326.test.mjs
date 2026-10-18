import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('version desktop cohérente',()=>{for(const p of ['package.json','windows/native/OpenVisio.csproj','windows/installer/OpenVisio.iss']) assert.match(read(p),new RegExp(JSON.parse(read('package.json')).version.replaceAll('.', '\\.')))});
test('navigation native attend chargement',()=>assert.match(read('windows/native/Program.cs'),/editorReady = e.IsSuccess/));
test('publication inclut les ressources',()=>assert.match(read('Build-Windows-EXE.cmd'),/wwwroot\\src/));
test('installateur signale WebView2 absent',()=>assert.match(read('windows/installer/OpenVisio.iss'),/HasWebView2/));

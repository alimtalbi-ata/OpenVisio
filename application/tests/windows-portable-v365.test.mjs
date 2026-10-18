import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const read=p=>fs.readFileSync(p,'utf8');
test('portable script checks exe and html',()=>{const s=read('windows/Build-Portable-Windows.ps1');assert.match(s,/OpenVisio.exe/);assert.match(s,/openvisio-assets.zip/);assert.match(s,/ZipArchive/)});
test('single cmd builds portable too',()=>assert.match(read('Build-OpenVisio-Windows.cmd'),/Build-Portable-Windows.ps1/));
test('native file picker advertises only supported types',()=>{const s=read('windows/native/Program.cs');assert.match(s,/\*\.ovjson/);assert.doesNotMatch(s,/\*\.vsdx/)});
test('portable documentation states WebView2 requirement',()=>assert.match(read('DOCUMENTATION-UTILISATEUR-V36.5.md'),/WebView2 Runtime/));

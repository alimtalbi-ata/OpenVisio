import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const cs=fs.readFileSync('windows/native/OpenVisio.csproj','utf8');const code=fs.readFileSync('windows/native/Program.cs','utf8');const ps=fs.readFileSync('windows/Build-Portable-Windows.ps1','utf8');
test('embedded assets conditional for portable publish',()=>{assert.match(cs,/OpenVisioEmbedAssets/);assert.match(cs,/OpenVisio.Assets.zip/)});
test('portable extracts assets to versioned cache',()=>{assert.match(code,/PrepareContentRoot/);assert.match(code,/ZipArchive/);assert.match(code,/Unsafe asset path/)});
test('portable build rejects extra runtime files',()=>{assert.match(ps,/Publication non mono-EXE/);assert.match(ps,/PublishSingleFile=true/)});

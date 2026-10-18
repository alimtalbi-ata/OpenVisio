import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const program=fs.readFileSync('windows/native/Program.cs','utf8');const project=fs.readFileSync('windows/native/OpenVisio.csproj','utf8');const installer=fs.readFileSync('windows/installer/OpenVisio.iss','utf8');
test('native JSON import uses editor-specific input',()=>assert.match(program,/getElementById\('openJsonInput'\)/));
test('recent documents persist to local app data',()=>{assert.match(program,/recent\.json/);assert.match(program,/SaveRecent\(\)/);});
test('published app includes every HTML page',()=>assert.match(project,/\.\.\/\.\.\/\*\.html/));
test('installer registers dedicated extension and startup document',()=>{assert.match(installer,/\.ovjson/);assert.match(program,/startupFile/);});
test('native shell rejects non JSON imports',()=>assert.match(program,/Format non pris en charge/));

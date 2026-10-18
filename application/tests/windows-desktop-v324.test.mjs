import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs';
const cs=fs.readFileSync('windows/native/Program.cs','utf8');
test('dialogue ouverture natif',()=>assert.match(cs,/new OpenFileDialog/));
test('dialogue export natif',()=>assert.match(cs,/new SaveFileDialog/));
test('protection taille import',()=>assert.match(cs,/20 \* 1024 \* 1024/));
test('liste documents récents',()=>assert.match(cs,/RefreshRecentMenu/));

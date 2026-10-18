import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const s=fs.readFileSync(new URL('../windows/native/Program.cs',import.meta.url),'utf8');
test('cache key is archive fingerprint not a static release marker',()=>assert.match(s,/File.WriteAllText\(Path.Combine\(staging, "\.complete"\), fingerprint\)/));
test('cache lock handles abandoned owners',()=>assert.match(s,/catch \(AbandonedMutexException\)/));
test('cache publication validates index and main module',()=>assert.match(s,/CacheValid\(\)/));

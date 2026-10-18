import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const source=fs.readFileSync(new URL('../windows/native/Program.cs',import.meta.url),'utf8');
test('cache marker is SHA256 of embedded archive',()=>{assert.match(source,/SHA256.HashData\(payload\)/);assert.match(source,/ReadAllText\(marker\)\.Trim\(\) != fingerprint/)});
test('cache publication has interprocess mutex',()=>{assert.match(source,/new Mutex\(false/);assert.match(source,/WaitOne\(TimeSpan.FromSeconds\(60\)\)/);assert.match(source,/ReleaseMutex\(\)/)});
test('cache staging is unique and old resources preserved',()=>{assert.match(source,/staging-" \+ Guid.NewGuid/);assert.doesNotMatch(source,/Directory.Delete\(cache, true\)/)});
test('failed replacement restores previous cache',()=>assert.match(source,/Directory.Move\(stale, cache\); throw;/));

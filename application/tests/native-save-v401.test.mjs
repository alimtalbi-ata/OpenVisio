import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const s=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('native save requires API capability',()=>assert.match(s,/typeof window\.showSaveFilePicker!==['"]function['"]/));
test('native save waits for write and close',()=>{assert.match(s,/await writable\.write\(parsed\)/);assert.match(s,/await writable\.close\(\)/)});
test('native save acknowledges after close',()=>{const i=s.indexOf('await writable.close()');assert.ok(s.indexOf('savedFingerprint=documentFingerprint()',i)>i)});
test('open clears previous native file handle',()=>assert.match(s,/nativeFileHandle=null;savedFingerprint=/));

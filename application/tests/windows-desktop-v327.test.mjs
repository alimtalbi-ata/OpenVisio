import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../windows/native/Program.cs',import.meta.url),'utf8');
test('startup waits for actual WebView navigation',()=>assert.match(code,/await WaitForEditorAsync\(\)/));
test('navigation completion resolves startup readiness',()=>assert.match(code,/navigationReady.TrySetResult\(e.IsSuccess\)/));
test('navigation resets readiness on new document',()=>assert.match(code,/navigationReady = new\(TaskCreationOptions.RunContinuationsAsynchronously\)/));
test('startup wait is bounded',()=>assert.match(code,/TimeSpan.FromSeconds\(20\)/));

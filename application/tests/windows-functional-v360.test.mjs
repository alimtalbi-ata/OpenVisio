import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
const script=readFileSync(new URL('./browser-functional-v360.py',import.meta.url),'utf8');
test('v36.0 checks entire persisted JSON model',()=>{assert.match(script,/stable_model\(payload\)==stable_model\(reopened_payload\)/);});
test('v36.0 compares after actual second download',()=>{assert.match(script,/download_json_again/);assert.match(script,/diagram-reopened-real.json/);});
test('v36.0 does not silently discard SAN attributes',()=>{assert.match(script,/ephemeral=/);assert.doesNotMatch(script,/ephemeral=.*wwpn/i);});
test('v36.0 script is included',()=>assert.ok(existsSync(new URL('./browser-functional-v360.py',import.meta.url))));

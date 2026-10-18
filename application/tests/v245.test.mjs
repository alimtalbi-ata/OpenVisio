import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('./browser-san-performance.py',import.meta.url),'utf8');
for(const feature of ['multi-move','routing-integrity','invalid_paths','zoom','selection','interactions'])test('v24.5 scenario '+feature,()=>assert.ok(src.includes(feature)));
test('v24.5 fail-closed',()=>assert.match(src,/if any\(not item\['pass'\]/));

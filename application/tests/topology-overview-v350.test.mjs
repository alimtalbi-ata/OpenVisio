import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { SAN_SUMMARY_ITEMS,sanitizeSummary,getSanSummary } from '../src/topology-overview-v350.js';
test('overview has distinct, grounded analysis targets',()=>{assert.equal(new Set(SAN_SUMMARY_ITEMS.map(x=>x[1])).size,SAN_SUMMARY_ITEMS.length);assert.ok(SAN_SUMMARY_ITEMS.length>=8)});
test('summary normalization is bounded',()=>assert.equal(sanitizeSummary('  hello  \n world '),'hello world'));
test('missing summary stays explicit',()=>assert.match(getSanSummary({getElementById:()=>null})[0].summary,/non disponible/));
test('overview resources linked into HTML',()=>{const h=readFileSync(new URL('../index.html',import.meta.url),'utf8');assert.match(h,/topology-overview-v350.js/);assert.match(h,/topology-overview-v350.css/)});

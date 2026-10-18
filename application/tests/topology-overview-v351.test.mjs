import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterSanSummaries} from '../src/topology-overview-v350.js';
const data=[{name:'Zoning',summary:'Fabric A'},{name:'Chemins',summary:'Multipathing dégradé'}];
test('filter by analysis title',()=>assert.deepEqual(filterSanSummaries(data,'zoning'),[data[0]]));
test('filter by analysis content',()=>assert.deepEqual(filterSanSummaries(data,'MULTIPATHING'),[data[1]]));
test('empty filter preserves all summaries',()=>assert.equal(filterSanSummaries(data,' ').length,2));
test('overview includes accessible live result count and search',()=>{const s=readFileSync(new URL('../src/topology-overview-v350.js',import.meta.url),'utf8');assert.match(s,/aria-live/);assert.match(s,/Filtrer la synthèse SAN/)});

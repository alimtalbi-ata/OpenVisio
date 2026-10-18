import test from 'node:test';import assert from 'node:assert/strict';import {buildZoningMatrix,filterZoningMatrix,zoningMatrixCsv} from '../src/san-zoning-matrix-v318.js';
const data={zones:[{name:'zone1',vsan:10,configurationState:'active',members:['10:00:00:00:00:00:00:01'],fabric:'A',switch:'sw1',line:2},{name:'zone1',vsan:10,configurationState:'configured',members:['10:00:00:00:00:00:00:02'],fabric:'A',switch:'sw1',line:3}]};
test('zoning matrix detects differences and source provenance',()=>{const r=buildZoningMatrix(data);assert.equal(r.counts.different,1);assert.equal(r.entries[0].priority,'P2');assert.deepEqual(r.entries[0].sourceLines,[2,3]);});
test('zoning matrix filter',()=>{const e=buildZoningMatrix(data).entries;assert.equal(filterZoningMatrix(e,'P2').length,1);assert.equal(filterZoningMatrix(e,'P3').length,0);});
test('zoning matrix export has stable header',()=>assert.match(zoningMatrixCsv(buildZoningMatrix(data)),/"priority","fabric","vsan"/));
test('zoning matrix handles empty exports',()=>assert.equal(buildZoningMatrix({zones:[]}).counts.total,0));

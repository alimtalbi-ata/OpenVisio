import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {detectSanVendor,previewSanImport,previewCsv,MAX_IMPORT_BYTES} from '../src/san-config-import-v312-ui.js';
test('Brocade detected and previewed',()=>{const p=previewSanImport('zone: prod 10:00:00:00:00:00:00:01 50:00:00:00:00:00:00:02');assert.equal(p.vendor,'brocade');assert.equal(p.zones.length,1);});
test('Cisco recognized',()=>assert.equal(detectSanVendor('zone name PROD vsan 10'),'cisco'));
test('ESXi recognized',()=>assert.equal(detectSanVendor('Runtime Name: vmhba2:C0:T1:L0'),'esxi'));
test('unknown source remains unknown',()=>assert.equal(detectSanVendor('some unrelated log'),'unknown'));
test('CSV prevents formula injection',()=>assert.match(previewCsv({records:[{type:'Zone',name:'=cmd',count:1,line:2}]}),/"'=cmd"/));
test('UI mounted in main editor',()=>{const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');assert.match(html,/id="sanConfigImportPanel"/);assert.match(html,/san-config-import-v312-ui.js/);assert.equal(MAX_IMPORT_BYTES,5_000_000);});

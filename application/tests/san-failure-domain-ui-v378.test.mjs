import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('v38.0 inspector exposes five editable documentary failure domains',()=>{
 const source=read('src/inspector.js');
 for(const key of ['site','chassis','powerDomain','controller','failureDomain']) assert.match(source,new RegExp("\\['"+key+"','"));
 assert.match(source,/actions\.update\(key,input\.value\)/);
});
test('v38.0 panel renders shared domains without HTML injection',()=>{
 const source=read('src/san-redundancy-panel-v364.js');
 assert.match(source,/commonCriticalDomains\?\.length/);
 assert.match(source,/entry\.textContent=/);
 assert.match(source,/addFocusButton\(entry,domain\.nodeIds/);
});

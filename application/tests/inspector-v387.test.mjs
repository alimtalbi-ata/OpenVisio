import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = p => readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('inspector offers six accessible property categories',()=>{const html=read('index.html');for(const cat of ['all','general','appearance','connections','san','resilience'])assert.match(html,new RegExp(`data-inspector-category="${cat}"`));});
test('category filtering combines with existing search and essential filter',()=>{const js=read('src/workspace-inspector-v335.js');assert.match(js,/fieldCategory\(key\)/);assert.match(js,/categoryMatch/);assert.match(js,/matches&&essential&&categoryMatch/);});
test('category selector supports persisted preference and reset',()=>{const js=read('src/workspace-inspector-v387.js');assert.match(js,/localStorage\.setItem/);assert.match(js,/inspectorClearFilter/);assert.match(js,/inspectorSanFields/);});
test('SAN module script is inside the HTML document',()=>{const html=read('index.html');assert.ok(html.indexOf('src/san-redundancy-panel-v364.js')<html.lastIndexOf('</body></html>'));});

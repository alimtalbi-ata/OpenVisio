import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');const js=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');const css=readFileSync(new URL('../styles/app.css',import.meta.url),'utf8');
test('palette de commandes accessible depuis le ruban',()=>{assert.match(html,/id="commandSearchBtn" type="button"/);assert.match(html,/id="commandSearchDialog"[^>]*aria-labelledby="commandSearchTitle"/);});
test('recherche de commandes et execution par clic',()=>{assert.match(js,/function refreshCommandSearch/);assert.match(js,/commandDialog.close\(\);target.click\(\)/);});
test('raccourcis de recherche et inspecteur',()=>{assert.match(js,/key==='p'/);assert.match(js,/key==='i'/);assert.match(js,/function openSelectionInspector/);});
test('palette adaptative avec focus visible',()=>{assert.match(css,/#commandSearchResults button:focus-visible/);assert.match(css,/width:min\(560px/);});

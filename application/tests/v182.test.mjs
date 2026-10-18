import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../styles/app.css',import.meta.url),'utf8');
for(const name of ['Aligner et répartir','Transformer','Repères et grille','Superposition']) test(`menu ${name}`,()=>assert.ok(html.includes(name)));
test('all original critical controls preserved',()=>{for(const id of ['alignLeft','distributeX','rotateLeft','showRulers','guidePicker','zOrderFront','fitCanvas']) assert.match(html,new RegExp(`id="${id}"`))});
test('menu accessible native HTML',()=>{assert.match(html,/<details class="tool-menu">/);assert.match(html,/<summary>/);assert.match(css,/tool-menu-panel/)});

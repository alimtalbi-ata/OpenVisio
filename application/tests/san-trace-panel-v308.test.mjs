import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../src/san-resilience-v300-ui.js',import.meta.url),'utf8');
test('v30.8 exposes per-row FC trace',()=>assert.match(ui,/textContent='Détail FC'/));
test('v30.8 displays WWPN and ports',()=>{assert.match(ui,/sourceWwpn/);assert.match(ui,/sourcePort/);});
test('v30.8 uses safe textContent for trace metadata',()=>assert.match(ui,/cell.textContent=v/));
test('v30.8 exports trace CSV',()=>assert.match(ui,/pathTraceCsv\(trace\)/));

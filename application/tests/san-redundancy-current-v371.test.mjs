import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const panel=readFileSync(new URL('../src/san-redundancy-panel-v364.js',import.meta.url),'utf8');
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('SAN panel requests current diagram via existing snapshot event',()=>{assert.match(panel,/openvisio:san-snapshot-request/);assert.match(main,/openvisio:san-snapshot-request/);});
test('SAN panel ignores unsolicited snapshot events',()=>assert.match(panel,/if\(!awaitingSnapshot\)return/));
test('SAN panel uses shared analysis for import and current diagram',()=>{assert.match(panel,/analyzeDiagram\(event\.detail\)/);assert.match(panel,/analyzeDiagram\(JSON\.parse/);});
test('SAN panel never mutates source state',()=>{assert.doesNotMatch(panel,/state\.nodes\s*=|state\.edges\s*=/);assert.match(panel,/Données déclaratives/);});

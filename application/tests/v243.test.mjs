import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('./browser-san-performance.py',import.meta.url),'utf8');
test('banc Chromium réalise un rendu SVG',()=>assert.match(src,/renderGraph\(svg,state,handlers\)/));
test('banc compare le rendu avec cache',()=>assert.match(src,/cached_ms/));
test('banc déplace un équipement SAN',()=>assert.match(src,/move_ms/));
test('banc produit des métriques DOM',()=>assert.match(src,/lastRenderStatistics/));
test('banc signale explicitement les erreurs navigateur',()=>assert.match(src,/status='FAIL'/));

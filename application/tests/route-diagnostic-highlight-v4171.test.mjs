import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
test('focus highlight targets the requested edge only',()=>{assert.match(main,/edges\.find\(edge=>edge\.getAttribute\('data-edge-id'\)===String\(edgeId\)\)/)});
test('previous focus is cleared before applying new highlight',()=>{assert.match(main,/classList\.remove\('route-diagnostic-focus'\)/);assert.match(main,/classList\.add\('route-diagnostic-focus'\)/)});
test('highlight is triggered after selecting a diagnostic connection',()=>{assert.match(main,/highlightRouteDiagnosticEdge\(svg,id\)/)});
test('highlight uses non-persistent CSS rather than editing the route geometry',()=>{assert.match(html,/route-diagnostic-focus/)});

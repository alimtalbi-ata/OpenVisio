import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('diagnostic accessible et fermé initialement',()=>{assert.match(html,/id="renderDiagnosticsPanel" hidden/);assert.match(html,/aria-controls="renderDiagnosticsPanel"/);});
test('diagnostic montre les percentiles sans telemetry externe',()=>{assert.match(main,/interactionMetrics.snapshot\(\)/);assert.match(main,/m.p95Ms.toFixed/);assert.match(html,/pas de FPS mesurés/);});
test('bouton de remise à zéro des mesures',()=>{assert.match(main,/interactionMetrics.reset\(\)/);assert.match(html,/id="renderDiagnosticsReset"/);});

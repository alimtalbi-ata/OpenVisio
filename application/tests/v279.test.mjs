import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {analyzeSanRecommendations} from '../src/san-recommendations.js';
const html=readFileSync(new URL('../san-recommendations.html',import.meta.url),'utf8');const ui=readFileSync(new URL('../src/san-recommendations-ui.js',import.meta.url),'utf8');
test('cockpit page exposes navigation and sections',()=>{for(const v of ['index.html','metrics','rows','issues','filter','source'])assert.ok(html.includes(v))});
test('UI imports deterministic SAN engine',()=>assert.match(ui,/analyzeSanRecommendations/));
test('UI avoids HTML injection with textContent',()=>{assert.match(ui,/textContent/);assert.doesNotMatch(ui,/innerHTML/)});
test('selected incompatible corrections excluded from gain',()=>{const r=analyzeSanRecommendations([{id:'a',selected:true,gain:10,conflictsWith:['b']},{id:'b',selected:true,gain:20}]);assert.equal(r.summary.estimatedGain,0)});
test('UI export is gated on a valid report',()=>assert.match(ui,/if\(report\)download/));

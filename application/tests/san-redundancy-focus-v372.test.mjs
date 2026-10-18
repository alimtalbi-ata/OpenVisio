import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/san-redundancy-panel-v364.js',import.meta.url),'utf8');
test('v37.3 localisation exploite le canal de surbrillance existant',()=>{assert.match(src,/openvisio:san-path-overlay/);assert.match(src,/survivingIds/);assert.match(src,/edgeIds/);});
test('v37.3 actions par chemin et anomalie',()=>{assert.match(src,/addFocusButton\(action,\[p.hostId,p.arrayId\]\)/);assert.match(src,/addFocusButton\(li,\[issue.nodeId,issue.hostId,issue.arrayId,\.\.\.\(issue.nodeIds/);});
test('v37.3 localisation ne modifie pas les donnees',()=>{assert.doesNotMatch(src,/state\.(nodes|edges)\s*=/);assert.match(src,/button.disabled=/);});

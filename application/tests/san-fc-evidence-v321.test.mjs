import test from 'node:test';import assert from 'node:assert/strict';
import {evaluateFcEvidence,fcEvidenceCsv} from '../src/san-fc-evidence-v321.js';
const w='10:00:00:00:00:00:00:01';
test('WWPN port et Fabric concordants corroborent le chemin documenté',()=>{const r=evaluateFcEvidence({wwpns:[w],port:'fc1',fabric:'A'},{edges:[{id:'e1',sourceWwpn:w,fromPort:'fc1',fabric:'A'}]});assert.equal(r.status,'CORROBORATED');assert.equal(r.results[0].portEvidence,'MATCH');});
test('conflit de Fabric identifié sans masquer la correspondance WWPN',()=>{const r=evaluateFcEvidence({wwpns:[w],fabric:'B'},{edges:[{id:'e1',sourceWwpn:w,fabric:'A'}]});assert.equal(r.status,'CONFLICT');});
test('port absent reste inconnu et ne devient pas une confirmation',()=>{const r=evaluateFcEvidence({wwpns:[w],port:'fc1',fabric:'A'},{edges:[{id:'e1',sourceWwpn:w,fabric:'A'}]});assert.equal(r.status,'PARTIAL');assert.equal(r.results[0].portEvidence,'UNKNOWN');});
test('aucun WWPN ne produit aucune correspondance',()=>{assert.equal(evaluateFcEvidence({port:'fc1'},{edges:[{id:'e'}]}).status,'NO_WWPN_EVIDENCE');});
test('ISL conservé dans le rapport',()=>{const r=evaluateFcEvidence({wwpns:[w]},{edges:[{id:'isl1',sourceWwpn:w,type:'isl'}]});assert.equal(r.results[0].isl,true);});
test('export CSV protège les formules',()=>{const csv=fcEvidenceCsv([{results:[{status:'PARTIAL',edgeId:'=evil',matchedWwpns:[],portEvidence:'UNKNOWN',fabricEvidence:'UNKNOWN',isl:false}]}]);assert.match(csv,/"'=evil"/);});

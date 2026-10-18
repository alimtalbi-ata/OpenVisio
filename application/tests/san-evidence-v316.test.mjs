import test from 'node:test';import assert from 'node:assert/strict';import {filterSanEvidence,evidenceRecommendation,sanCorrelationCsv} from '../src/san-import-correlation-v313.js';
test('filtrage par preuve active',()=>assert.equal(filterSanEvidence([{evidenceConfidence:'NONE'},{evidenceConfidence:'ACTIVE_DECLARED'}],'ACTIVE_DECLARED').length,1));
test('filtre ALL conserve les résultats',()=>assert.equal(filterSanEvidence([{evidenceConfidence:'NONE'}]).length,1));
test('preuve manquante ne conclut pas à une panne',()=>assert.match(evidenceRecommendation({status:'PAIR_NOT_IN_IMPORT',evidenceConfidence:'NONE'}),/avant de conclure/));
test('preuve configurée demande zoning effectif',()=>assert.match(evidenceRecommendation({evidenceConfidence:'CONFIGURED_OR_UNKNOWN'}),/effectif/));
test('CSV inclut preuve et recommandation',()=>assert.match(sanCorrelationCsv({findings:[{path:1,serverId:'s',storageId:'t',status:'DOCUMENTED_PAIR',initiatorWwpn:'',targetWwpn:'',zoneNames:[],edgeIds:[],evidenceConfidence:'NONE'}]}),/evidence_confidence/));

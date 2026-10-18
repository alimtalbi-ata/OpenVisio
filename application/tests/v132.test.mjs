import test from 'node:test';import assert from 'node:assert/strict';import {complianceHtmlReport,complianceTimeline,remediationForIssue} from '../src/san-compliance-report.js';
test('rapport HTML autonome et échappement',()=>{const html=complianceHtmlReport([]);assert.match(html,/<!doctype html>/);assert.match(html,/Score indicatif/);assert.match(html,/Abdelhalim Talbi/);});
test('aucun import : historique vide',()=>assert.deepEqual(complianceTimeline([]),[]));
test('recommandation Fabric absente',()=>assert.match(remediationForIssue({code:'FABRIC_MISSING'}),/Fabric/));
test('recommandation import périmé',()=>assert.match(remediationForIssue({code:'SNAPSHOT_STALE'}),/Rafraîchir/));
test('recommandation zone absente',()=>assert.match(remediationForIssue({code:'ZONE_UNDEFINED'}),/zoneset/));
test('recommandation code inconnu',()=>assert.match(remediationForIssue({code:'UNKNOWN'}),/manuellement/));
test('rapport sans scripts distants',()=>{const html=complianceHtmlReport([]);assert.doesNotMatch(html,/<script|https?:\/\//);});
test('rapport explique la limite déclarative',()=>assert.match(complianceHtmlReport([]),/Aucun contrôle direct/));

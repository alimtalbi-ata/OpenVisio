import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeSanRecommendations,recommendationsCsv} from '../src/san-recommendations.js';

const c=(id,extra={})=>({id,title:`Correction ${id}`,groupId:'g1',gain:5,severity:'high',risk:'low',...extra});
test('v27.8 only counts positive finite gains of selected compatible corrections',()=>{
 const r=analyzeSanRecommendations([c('a',{selected:true,gain:4}),c('b',{selected:true,gain:-8}),c('c',{selected:true,gain:Infinity}),c('d',{gain:100})]);
 assert.equal(r.summary.estimatedGain,4);assert.equal(r.summary.applicableSelected,3);
});
test('v27.8 detects conflict only when both corrections are selected',()=>{
 let r=analyzeSanRecommendations([c('a',{selected:true,conflictsWith:['b']}),c('b')]);
 assert.equal(r.summary.activeConflicts,0);
 r=analyzeSanRecommendations([c('a',{selected:true,conflictsWith:['b']}),c('b',{selected:true})]);
 assert.equal(r.summary.activeConflicts,1);assert.equal(r.summary.estimatedGain,0);
 r=analyzeSanRecommendations([c('z',{selected:true}),c('a',{selected:true,conflictsWith:['z']})]);assert.equal(r.summary.activeConflicts,1);
});
test('v27.8 reports missing and unselected dependencies',()=>{
 const r=analyzeSanRecommendations([c('a',{selected:true,dependsOn:['b','missing']}),c('b')]);
 assert.ok(r.issues.some(x=>x.code==='DEPENDENCY_NOT_SELECTED'));
 assert.ok(r.issues.some(x=>x.code==='MISSING_DEPENDENCY'));
 assert.equal(r.summary.estimatedGain,0);
});
test('v27.8 provides deterministic prerequisite-first order',()=>{
 const r=analyzeSanRecommendations([c('z',{dependsOn:['a']}),c('a'),c('b')]);
 assert.ok(r.priorityOrder.indexOf('a')<r.priorityOrder.indexOf('z'));
 assert.deepEqual(r.priorityOrder,analyzeSanRecommendations([c('z',{dependsOn:['a']}),c('a'),c('b')]).priorityOrder);
});
test('v27.8 identifies dependency cycles and does not count selected cyclic work',()=>{
 const r=analyzeSanRecommendations([c('a',{selected:true,dependsOn:['b']}),c('b',{selected:true,dependsOn:['a']})]);
 assert.equal(r.summary.dependencyCycles,2);assert.equal(r.summary.estimatedGain,0);
 assert.ok(r.issues.some(x=>x.code==='DEPENDENCY_CYCLE'));
});
test('v27.8 rejects duplicate identifiers and unknown risk levels',()=>{
 assert.throws(()=>analyzeSanRecommendations([c('x'),c('x')]),/dupliqué/);
 assert.throws(()=>analyzeSanRecommendations([c('x',{risk:'extreme'})]),/inconnu/);
});
test('v27.8 analysis is non-mutating and CSV formula-safe',()=>{
 const input=[c('x',{selected:true,reason:'=1+1'})], before=JSON.stringify(input);
 const r=analyzeSanRecommendations(input);assert.equal(JSON.stringify(input),before);
 assert.ok(recommendationsCsv(r).includes("'=1+1"));
});

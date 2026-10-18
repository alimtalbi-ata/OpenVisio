import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeSanRedundancy} from '../src/san-redundancy-v363.js';
const nodes=[{id:'h',type:'server',multipath:true},{id:'x',type:'san-switch',zoneset:'z',zoning:['a']},{id:'y',type:'san-switch',zoneset:'z',zoning:['b']},{id:'s',type:'storage'}];
const e=(id,source,target,fabric)=>({id,source,target,fabric});
test('disjoint A/B transit is independent',()=>{const p=analyzeSanRedundancy({nodes,edges:[e('a1','h','x','A'),e('a2','x','s','A'),e('b1','h','y','B'),e('b2','y','s','B')]}).paths[0];assert.equal(p.independence,'INDEPENDENT');assert.deepEqual(p.sharedTransitIds,[]);});
test('shared transit is flagged even with both fabrics available',()=>{const r=analyzeSanRedundancy({nodes,edges:[e('a1','h','x','A'),e('a2','x','s','A'),e('b1','h','x','B'),e('b2','x','s','B')]});assert.equal(r.paths[0].independence,'SHARED_RISK');assert.deepEqual(r.paths[0].sharedTransitIds,['x']);assert.ok(r.issues.some(i=>i.code==='SHARED_FABRIC_TRANSIT'));});
test('missing fabric is incomplete, not independent',()=>{const p=analyzeSanRedundancy({nodes,edges:[e('a1','h','x','A'),e('a2','x','s','A')]}).paths[0];assert.equal(p.independence,'INCOMPLETE');});
test('input topology remains unchanged',()=>{const d={nodes,edges:[e('a1','h','x','A'),e('a2','x','s','A')]};const before=JSON.stringify(d);analyzeSanRedundancy(d);assert.equal(JSON.stringify(d),before);});

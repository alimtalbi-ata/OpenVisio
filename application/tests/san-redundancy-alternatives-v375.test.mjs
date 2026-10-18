import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeSanRedundancy} from '../src/san-redundancy-v363.js';
const diagram=()=>({nodes:[{id:'h',type:'server',multipath:true},{id:'a',type:'storage'},...['x','y','z','b'].map(id=>({id,type:'san-switch',zoneset:'Z',zoning:['ok']}))],edges:[['h','x','A'],['x','a','A'],['h','y','A'],['y','a','A'],['h','b','B'],['b','a','B']].map(([source,target,fabric],i)=>({id:'e'+i,source,target,fabric}))});
test('v37.5 discovers alternative A path and B critical transit',()=>{const r=analyzeSanRedundancy(diagram()).paths[0];assert.equal(r.resilienceA.alternativeRoutes.length>0,true);assert.deepEqual(r.resilienceA.criticalTransitIds,[]);assert.deepEqual(r.resilienceB.criticalTransitIds,['b']);});
test('v37.5 bridge failure is critical despite alternative branches',()=>{const d=diagram();d.edges.push({id:'bridge',source:'a',target:'z',fabric:'A'});const r=analyzeSanRedundancy(d).paths[0];assert.ok(r.resilienceB.criticalEdgeIds.length>0);});
test('v37.5 analysis never mutates diagram',()=>{const d=diagram(),before=JSON.stringify(d);analyzeSanRedundancy(d);assert.equal(JSON.stringify(d),before);});

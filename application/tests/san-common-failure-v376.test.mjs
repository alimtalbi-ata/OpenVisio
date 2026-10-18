import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeSanRedundancy} from '../src/san-redundancy-v363.js';
function graph(routes){const ids=new Set(['h','a']);const edges=[];for(const [fabric,route] of routes){for(const id of route)ids.add(id);const seq=['h',...route,'a'];for(let i=1;i<seq.length;i++)edges.push({id:`${fabric}-${route.join('')}-${i}`,source:seq[i-1],target:seq[i],fabric});}return {nodes:[...ids].map(id=>({id,type:id==='h'?'server':id==='a'?'storage':'san-switch',multipath:id==='h',zoneset:'z',zoning:['ok']})),edges};}
test('v37.7 detects common physical transit even when it is not a shortest-path artifact',()=>{const d=graph([['A',['x','y']],['B',['z','y']]]);const p=analyzeSanRedundancy(d).paths[0];assert.equal(p.independence,'SHARED_RISK');assert.deepEqual(p.commonCriticalNodeIds,['y']);});
test('v37.7 shared node on selected routes but alternative B bypass prevents false positive',()=>{const d=graph([['A',['x']],['B',['x']],['B',['z']]]);const p=analyzeSanRedundancy(d).paths[0];assert.equal(p.independence,'INDEPENDENT');assert.deepEqual(p.commonCriticalNodeIds,[]);assert.deepEqual(p.sharedTransitIds,['x']);});
test('v37.7 separate fabrics have no shared physical single failure',()=>{const p=analyzeSanRedundancy(graph([['A',['x']],['B',['z']]])).paths[0];assert.equal(p.independence,'INDEPENDENT');});
test('v37.7 analysis does not modify source model',()=>{const d=graph([['A',['x']],['B',['x']]]);const before=JSON.stringify(d);analyzeSanRedundancy(d);assert.equal(JSON.stringify(d),before);});

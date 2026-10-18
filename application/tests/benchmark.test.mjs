import test from "node:test";import assert from "node:assert/strict";import {generateTopology,benchmarkRoutes} from "../src/benchmark.js";
for(const n of [100,500,1000]){
 test(`topologie ${n} équipements`,()=>{const g=generateTopology(n);assert.equal(g.nodes.length,n);assert.equal(g.edges.length,n-1);assert.equal(new Set(g.nodes.map(x=>x.id)).size,n);});
 test(`calcul des routes ${n}`,()=>{const r=benchmarkRoutes(n);assert.equal(r.edges,n-1);assert.ok(r.pathBytes>0);assert.ok(r.elapsedMs>=0);});
}
test("rejet d'un nombre d'équipements invalide",()=>assert.throws(()=>generateTopology(1),RangeError));

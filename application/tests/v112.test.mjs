import test from "node:test";import assert from "node:assert/strict";import {countRouteCrossings,routeWithFewerCrossings} from "../src/routing.js";
const line=(...points)=>({points:points.map(([x,y])=>({x,y}))});
test("croisement strict orthogonal",()=>assert.equal(countRouteCrossings([line([0,5],[10,5]),line([5,0],[5,10])]),1));
test("contacts aux extrémités exclus",()=>assert.equal(countRouteCrossings([line([0,5],[5,5]),line([5,0],[5,10])]),0));
test("parallèles exclus",()=>assert.equal(countRouteCrossings([line([0,0],[10,0]),line([0,2],[10,2])]),0));
test("plusieurs croisements comptés",()=>assert.equal(countRouteCrossings([line([0,5],[20,5]),line([5,0],[5,10]),line([15,0],[15,10])]),2));
test("validation des routes",()=>assert.throws(()=>countRouteCrossings([{points:[{x:NaN,y:0}]}])));
test("choix du décalage sans croisements",()=>{const a={x:0,y:0,w:20,h:20},b={x:200,y:0,w:20,h:20};const r=routeWithFewerCrossings(a,b,[]);assert.equal(r.offset,0);assert.equal(r.crossings,0)});
test("validation des décalages",()=>assert.throws(()=>routeWithFewerCrossings({x:0,y:0,w:20,h:20},{x:50,y:0,w:20,h:20},[],[Infinity])));

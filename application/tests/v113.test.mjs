import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";import {routeWithFewerCrossings,countRouteCrossings,routeEdge} from "../src/routing.js";
const source=readFileSync(new URL("../src/renderer.js",import.meta.url),"utf8");
test("renderer wires crossing-aware routing",()=>assert.match(source,/routeWithFewerCrossings\(a,b,placedRoutes\)/));
test("renderer invalidates SVG when computed path changes",()=>assert.match(source,/edgeVisualSignature\(edge,routed\.path,state\.selected===edge\.id/));
test("renderer collects routes even when DOM is reused",()=>assert.ok(source.indexOf('placedRoutes.push(routed)')<source.indexOf('if(prior&&prior.signature===signature)')));
test("crossing optimizer does not mutate original nodes",()=>{const a={x:0,y:0,w:60,h:40},b={x:300,y:200,w:60,h:40};const before=JSON.stringify([a,b]);routeWithFewerCrossings(a,b);assert.equal(JSON.stringify([a,b]),before)});
test("crossing optimizer never worse than default for existing routes",()=>{const a={x:0,y:0,w:60,h:40},b={x:300,y:200,w:60,h:40};const routes=[{points:[{x:180,y:-100},{x:180,y:400}]}];const optimized=routeWithFewerCrossings(a,b,routes);const defaultRoute=routeEdge(a,b);assert.ok(countRouteCrossings([...routes,optimized])<=countRouteCrossings([...routes,defaultRoute]));});

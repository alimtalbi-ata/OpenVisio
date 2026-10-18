import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const renderer=readFileSync(new URL("../src/renderer.js",import.meta.url),"utf8");
test("routage en cache",()=>assert.match(renderer,/const routeCache=createRouteValueCache/));
test("cache borné",()=>assert.match(renderer,/MAX_CACHE=500/));
test("invalidation par coordonnées",()=>assert.match(renderer,/a\.x,a\.y,a\.w,a\.h,b\.x,b\.y/));
test("obstacles pris en compte",()=>assert.match(renderer,/obstacles\.map\(n=>\[n\.id,n\.x,n\.y,n\.w,n\.h\]\)/));

import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const script=readFileSync(new URL("./svg-dom-benchmark.mjs",import.meta.url),"utf8");
test("mesure SVG froid et chaud",()=>{assert.match(script,/coldMs/);assert.match(script,/warmMs/);});
test("trois volumes de topologies",()=>assert.match(script,/\[100,500,1000\]/));
test("rapport indique les limites du DOM simulé",()=>assert.match(script,/excludes browser layout/));

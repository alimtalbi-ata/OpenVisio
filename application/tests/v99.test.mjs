import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const s=readFileSync(new URL("../src/renderer.js",import.meta.url),"utf8");
test("cache par instance SVG",()=>assert.match(s,/const renderStates=new WeakMap\(\)/));
test("réutilisation de noeuds inchangés",()=>assert.match(s,/nextNodes\.set\(n\.id,prior\);continue/));
test("réutilisation de connexions inchangées",()=>assert.match(s,/nextEdges\.set\(edge\.id,prior\);continue/));
test("suppression des éléments retirés",()=>assert.match(s,/if\(!nextNodes\.has\(id\)\)\{entry\.element\.remove\(\)/));
test("remplacement local de la forme modifiée",()=>assert.match(s,/prior\.element\.replaceWith\(g\)/));

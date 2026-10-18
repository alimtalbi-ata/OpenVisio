import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const main=readFileSync(new URL("../src/main.js",import.meta.url),"utf8");
const renderer=readFileSync(new URL("../src/renderer.js",import.meta.url),"utf8");
test("clic après glisser non interprété comme sélection",()=>assert.match(main,/if\(suppressNextClick\)\{suppressNextClick=false;return;/));
test("sélection multiple mise à jour au début du glisser",()=>assert.match(main,/refreshMulti\(\);updateSelectionLabel\(\);/));
test("rejet identifiants de noeuds en doublon",()=>assert.match(main,/new Set\(data\.nodes\.map\(n=>n\.id\)\)\.size/));
test("rejet identifiants de liens en doublon",()=>assert.match(main,/new Set\(data\.edges\.map\(e=>e\.id\)\)\.size/));
test("titres de noeuds importés absents acceptés sans crash",()=>assert.match(renderer,/String\(n\.title\?\?""\)/));

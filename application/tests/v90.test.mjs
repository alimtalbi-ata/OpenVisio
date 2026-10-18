import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const main=readFileSync(new URL("../src/main.js",import.meta.url),"utf8"),renderer=readFileSync(new URL("../src/renderer.js",import.meta.url),"utf8");
test("ajout de point par double clic",()=>assert.match(renderer,/hit\.addEventListener\("dblclick"/));
test("suppression de point par double clic",()=>assert.match(renderer,/handle\.addEventListener\("dblclick"/));
test("grille magnétique configurable",()=>assert.match(main,/let snapEnabled=false/));
test("bouton de grille accessible",()=>assert.match(main,/aria-pressed/));
test("clic de forme délégué",()=>assert.match(renderer,/handlers\.onNodeClick/));

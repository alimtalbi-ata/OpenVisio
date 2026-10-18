import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const inspector=readFileSync(new URL("../src/inspector.js",import.meta.url),"utf8");
const main=readFileSync(new URL("../src/main.js",import.meta.url),"utf8");
const html=readFileSync(new URL("../index.html",import.meta.url),"utf8");
test("inspecteur annonce type d'objet",()=>assert.match(inspector,/inspector-kind/));
test("inspecteur affiche nom d'objet",()=>assert.match(inspector,/objectName\.textContent/));
test("étiquettes accessibles dans inspecteur",()=>assert.match(inspector,/setAttribute\("aria-label",label\)/));
test("raccourci de recherche Ctrl K",()=>assert.match(main,/event\.key\.toLowerCase\(\)==="k"/));
test("version actualisée dans interface",()=>assert.match(html,/OpenVisio v\d+\.\d+/));

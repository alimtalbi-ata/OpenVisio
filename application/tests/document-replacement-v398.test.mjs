import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const code=readFileSync(new URL("../src/main.js",import.meta.url),"utf8");
test("new diagram warns on nodes or edges",()=>assert.match(code,/isDocumentDirty\(\)/));
test("JSON import confirms before replacing active graph",()=>{const ask=code.indexOf("Ouvrir ce fichier remplacera");const replace=code.indexOf("saveUndo();declaredZones=zones",ask);assert.ok(ask>0 && replace>ask);});
test("cancelled JSON import clears input",()=>assert.match(code,/e\.target\.value=""; return;/));

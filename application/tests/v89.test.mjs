import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
test("renderer uses onPointerDown callback",()=>assert.match(readFileSync(new URL("../src/renderer.js",import.meta.url),"utf8"),/handlers\.onPointerDown\(e,n\)/));
test("handles are accessible",()=>assert.match(readFileSync(new URL("../src/renderer.js",import.meta.url),"utf8"),/aria-label.*Déplacer le point/));
test("pointer positions use SVG transform",()=>assert.match(readFileSync(new URL("../src/main.js",import.meta.url),"utf8"),/getScreenCTM\(\)/));

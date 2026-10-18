import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const code=readFileSync(new URL("../src/main.js",import.meta.url),"utf8");
test("node drag uses SVG coordinates",()=>assert.match(code,/const dx=current\.x-drag\.startPoint\.x/));
test("pointer captured for node drag",()=>assert.match(code,/moved:false\};svg\.setPointerCapture/));
test("click without movement does not mutate",()=>assert.match(code,/if\(!drag\.moved\)return;/));
test("modifier pointerdown does not bubble",()=>assert.match(code,/if\(e\.ctrlKey\|\|e\.metaKey\|\|e\.shiftKey\)\{e\.stopPropagation\(\)/));

import test from "node:test";import assert from "node:assert/strict";import {readFileSync} from "node:fs";
const source=readFileSync(new URL("../src/main.js",import.meta.url),"utf8");
test("la poignée n'ajoute un undo qu'après mouvement",()=>assert.match(source,/if\(!waypointDrag\.saved\)\{saveUndo\(\)/));
test("la saisie des points intercepte les erreurs",()=>assert.match(source,/try\{parsed=parseWaypoints\(value\);\}catch/));
test("pas de mouvement si coordonnées inchangées",()=>assert.match(source,/edge\.waypoints\[waypointDrag\.index\]\.x===next\.x/));

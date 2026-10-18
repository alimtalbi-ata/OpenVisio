import test from "node:test";import assert from "node:assert/strict";import {readFileSync,existsSync} from "node:fs";
const ps=readFileSync(new URL("../windows/openvisio.ps1",import.meta.url),"utf8");
const cmd=readFileSync(new URL("../OpenVisio-Windows.cmd",import.meta.url),"utf8");
test("lanceur Windows sans Python",()=>{assert.match(cmd,/powershell\.exe/);assert.doesNotMatch(cmd,/python|py -3/i)});
test("liaison locale",()=>assert.match(ps,/IPAddress\]::Loopback/));
test("rejet des méthodes d'écriture",()=>assert.match(ps,/StatusCode = 405/));
test("restriction des chemins",()=>assert.match(ps,/StartsWith\(\$rootPrefix/));
test("liste blanche extensions",()=>assert.match(ps,/\$mime\.ContainsKey\(\$ext\)/));
test("interface disponible",()=>assert.ok(existsSync(new URL("../index.html",import.meta.url))));

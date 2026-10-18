import test from "node:test";
import assert from "node:assert/strict";
import {CATEGORIES,filterShapes,readRecentShapes,trackRecentShape} from "../src/library.js";
test("recent category is available",()=>assert.ok(CATEGORIES.some(c=>c.id==="recent")));
test("recent shapes retain order without duplicates",()=>assert.deepEqual(trackRecentShape(["a","b","c"],"b"),["b","a","c"]));
test("recent shapes are bounded",()=>assert.equal(trackRecentShape(Array.from({length:20},(_,i)=>String(i)),"new").length,12));
test("invalid storage is safe",()=>assert.deepEqual(readRecentShapes("invalid"),[]));
test("recent category filters shapes",()=>{const shapes=[{vendor:"Generic",name:"Server",type:"server",category:"compute"},{vendor:"Generic",name:"Switch",type:"switch",category:"network"}];assert.deepEqual(filterShapes(shapes,{category:"recent",recent:["Generic:Switch:switch"]}).map(s=>s.name),["Switch"]);});

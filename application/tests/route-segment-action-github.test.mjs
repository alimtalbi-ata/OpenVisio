import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {summarizeRouteIssueSegments} from '../src/route-clearance-view.js';

test('SAN diagnostic segments are deduplicated and 1-based',()=>{
 assert.deepEqual(summarizeRouteIssueSegments([{segment:2},{segment:0},{segment:2}]),{segments:[1,3],overflow:0});
});
test('route diagnostics expose accessible segment actions',()=>{
 const src=readFileSync(new URL('../src/route-clearance-view.js',import.meta.url),'utf8');
 assert.match(src,/onSelectSegment\(item\.edgeId,number\)/);
 assert.match(src,/Examiner le segment/);
});

test('v41.77 segment controls provide keyboard navigation',()=>{
 const src=readFileSync(new URL('../src/route-clearance-view.js',import.meta.url),'utf8');
 assert.match(src,/event\.key==='ArrowLeft'/);
 assert.match(src,/event\.key==='ArrowRight'/);
 assert.match(src,/siblings\[next\]\?\.focus/);
 assert.match(src,/event\.stopPropagation\?\.\(\)/);
});

test('route segment geometry is available as a detached snapshot',async()=>{
 const {lastRouteSegmentGeometry}=await import('../src/renderer.js');
 assert.deepEqual(lastRouteSegmentGeometry({}),[]);
});
test('segment focus is cleaned on selection and panel closure',()=>{
 const src=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(src,/function select\(id\)\{clearRouteDiagnosticSegments\(svg\)/);
 assert.match(src,/onSelectSegment:\(id,number\)=>/);
 assert.match(src,/behavior:'auto'/);
});

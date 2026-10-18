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

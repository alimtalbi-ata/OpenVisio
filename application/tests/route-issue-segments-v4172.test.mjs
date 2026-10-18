import test from 'node:test';
import assert from 'node:assert/strict';
import {summarizeRouteIssueSegments,buildRouteClearanceView} from '../src/route-clearance-view.js';
test('segments are unique sorted and numbered from one',()=>assert.deepEqual(summarizeRouteIssueSegments([{segment:3},{segment:0},{segment:3},{segment:1}]),{segments:[1,2,4],overflow:0}));
test('invalid issue segment indices are excluded',()=>assert.deepEqual(summarizeRouteIssueSegments([{segment:-1},{segment:'2'},{segment:1.5},null]),{segments:[],overflow:0}));
test('large issue sets are truncated for readability',()=>assert.deepEqual(summarizeRouteIssueSegments(Array.from({length:8},(_,segment)=>({segment}))),{segments:[1,2,3,4,5],overflow:3}));
test('diagnostic issue details remain available after classification',()=>{const v=buildRouteClearanceView({edges:[{edgeId:'SAN-1',errors:1,issues:[{segment:2,type:'obstacle-intersection'}]}]});assert.equal(summarizeRouteIssueSegments(v.items[0].issues).segments[0],3)});

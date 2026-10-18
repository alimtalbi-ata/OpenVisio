import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveDistributedRoute} from '../src/renderer.js';
const a={id:'a'},b={id:'b'},c={id:'c'},edge={id:'e',style:'avoid'};
test('route distribuée réutilisée sans fallback',()=>{const route={points:[{x:1,y:2}]};assert.equal(resolveDistributedRoute(edge,a,b,[a,b,c],new Map([['e',route]]),[],()=>{throw Error('fallback appelé')}),route)});
test('fallback avoid exclut les deux terminaux',()=>{let seen;const result=resolveDistributedRoute(edge,a,b,[a,c,b],new Map(),[],(_e,_a,_b,obstacles)=>{seen=obstacles;return {points:[]}});assert.deepEqual(seen,[c]);assert.deepEqual(result,{points:[]})});
test('fallback orthogonal évite de parcourir les obstacles',()=>{let seen;resolveDistributedRoute({...edge,style:'orthogonal'},a,b,[a,b,c],new Map(),[],(_e,_a,_b,obstacles)=>{seen=obstacles;return {}});assert.deepEqual(seen,[])});
test('route absente déclenche le fallback',()=>{let calls=0;resolveDistributedRoute(edge,a,b,[a,b],new Map(),[],()=>{calls++;return {}});assert.equal(calls,1)});
test('entrée map invalide rejetée',()=>assert.throws(()=>resolveDistributedRoute(edge,a,b,[],{},[]),TypeError));

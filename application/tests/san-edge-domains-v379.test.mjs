import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const inspector=readFileSync(new URL('../src/inspector.js',import.meta.url),'utf8');
test('edge inspector exposes five failure domains',()=>{for(const field of ['site','chassis','powerDomain','controller','failureDomain'])assert.match(inspector,new RegExp("\\['"+field+"','"));assert.match(inspector,/edgeDomainSection/);assert.match(inspector,/edge\[key\]/);});
test('edge failure domains use existing update callback and preserve other properties',()=>{assert.match(inspector,/actions\.update\(key,input\.value\)/);assert.match(inspector,/Interface source/);assert.match(inspector,/Interface destination/);assert.match(inspector,/Supprimer la connexion/);});

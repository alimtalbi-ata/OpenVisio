import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
const fixture=JSON.parse(readFileSync('tests/fixtures/san-dual-fabric-v362.json','utf8'));
test('v36.2 synthetic SAN fixture models redundant fabrics and paths',()=>{
 assert.equal(fixture.nodes.length,4);assert.equal(fixture.edges.length,4);
 assert.deepEqual(new Set(fixture.edges.map(e=>e.fabric)),new Set(['A','B']));
 assert.equal(fixture.nodes.find(n=>n.id==='host-a').multipath,true);
});
test('v36.2 fidelity helper detects single-fabric zoning regression with precise path',()=>{
 const code=`import json,importlib.util,copy; s=importlib.util.spec_from_file_location('f','tests/san-fidelity-v361.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);a=json.load(open('tests/fixtures/san-dual-fabric-v362.json'));b=copy.deepcopy(a);b['nodes'][1]['zoning']=['BROKEN'];r=m.compare(a,b);assert not r['equal'] and not r['san_equal'];assert r['san_changed_paths']==['$.nodes[1].zoning'],r`;
 const r=spawnSync('python3',['-c',code],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
});
test('v36.2 fidelity helper detects missing B-fabric link',()=>{
 const code=`import json,importlib.util,copy;s=importlib.util.spec_from_file_location('f','tests/san-fidelity-v361.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);a=json.load(open('tests/fixtures/san-dual-fabric-v362.json'));b=copy.deepcopy(a);b['edges']=[e for e in b['edges'] if e['id']!='a4'];r=m.compare(a,b);assert not r['equal'];assert r['san_changed_paths'],r`;
 const r=spawnSync('python3',['-c',code],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
});

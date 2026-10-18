import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {createRecoveryRecord,verifyRecoveryRecord,pruneRecoveryRecords} from '../src/recovery-integrity-v403.js';
test('recovery roundtrip validates SHA256 and restores the original object', async()=>{const obj={nodes:[{id:'a'}],edges:[]};const rec=await createRecoveryRecord(obj,{cryptoApi:webcrypto,now:()=>new Date('2026-10-17T10:00:00Z')});assert.equal(rec.sha256.length,64);assert.deepEqual((await verifyRecoveryRecord(rec,webcrypto)).diagram,obj)});
test('tampered snapshot is rejected before parsing',async()=>{const rec=await createRecoveryRecord({nodes:[]},{cryptoApi:webcrypto});rec.payload='{"nodes":[1]}';assert.equal((await verifyRecoveryRecord(rec,webcrypto)).reason,'CHECKSUM_MISMATCH')});
test('malformed recovery data is rejected',async()=>{assert.equal((await verifyRecoveryRecord({schema:'bad'},webcrypto)).valid,false);await assert.rejects(()=>createRecoveryRecord([],{cryptoApi:webcrypto}),TypeError)});
test('retention sorts by timestamp and applies limit',()=>{const records=[1,3,2].map(n=>({schema:'openvisio-recovery-v1',createdAt:`2026-10-0${n}`}));assert.deepEqual(pruneRecoveryRecords(records,2).map(x=>x.createdAt),['2026-10-03','2026-10-02'])});

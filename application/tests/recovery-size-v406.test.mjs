import test from 'node:test';
import assert from 'node:assert/strict';
import {createRecoveryRecord,verifyRecoveryRecord,MAX_RECOVERY_BYTES} from '../src/recovery-integrity-v403.js';
test('recovery accepts a valid signed payload',async()=>{const r=await createRecoveryRecord({graph:{nodes:[],edges:[]}});assert.equal((await verifyRecoveryRecord(r)).valid,true)});
test('recovery refuses oversized payload before cryptographic processing',async()=>{const r={schema:'openvisio-recovery-v1',algorithm:'SHA-256',sha256:'a'.repeat(64),createdAt:new Date().toISOString(),payload:'x'.repeat(MAX_RECOVERY_BYTES+1)};assert.equal((await verifyRecoveryRecord(r)).reason,'RECOVERY_TOO_LARGE')});
test('recovery rejects invalid creation date',async()=>{const r=await createRecoveryRecord({graph:{nodes:[],edges:[]}});r.createdAt='not-a-date';assert.equal((await verifyRecoveryRecord(r)).reason,'INVALID_TIMESTAMP')});

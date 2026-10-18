/** OpenVisio 40.3 — integrity-checked recovery snapshots. Author: Abdelhalim Talbi.
 * Explicit recovery utility; does not claim that a disk write has happened.
 */
const DEFAULT_LIMIT = 8;
export const MAX_RECOVERY_BYTES = 25 * 1024 * 1024;
export function stableSnapshot(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new TypeError('Diagram object required');
  return JSON.stringify(value);
}
export async function sha256Hex(text, cryptoApi = globalThis.crypto) {
  if (!cryptoApi?.subtle?.digest) throw new Error('SHA-256 unavailable');
  const bytes = new TextEncoder().encode(text);
  const hash = await cryptoApi.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(hash), b => b.toString(16).padStart(2, '0')).join('');
}
export async function createRecoveryRecord(diagram, {now=()=>new Date(), cryptoApi=globalThis.crypto}={}) {
  const payload=stableSnapshot(diagram);
  if(new TextEncoder().encode(payload).byteLength > MAX_RECOVERY_BYTES) throw new RangeError("RECOVERY_TOO_LARGE");
  return {schema:'openvisio-recovery-v1', createdAt:now().toISOString(), algorithm:'SHA-256', sha256:await sha256Hex(payload,cryptoApi), payload};
}
export async function verifyRecoveryRecord(record, cryptoApi=globalThis.crypto) {
  if (!record || record.schema!=='openvisio-recovery-v1' || record.algorithm!=='SHA-256' || typeof record.payload!=='string' || !/^[a-f0-9]{64}$/.test(record.sha256||'')) return {valid:false,reason:'INVALID_RECORD'};
  try { if(new TextEncoder().encode(record.payload).byteLength > MAX_RECOVERY_BYTES) return {valid:false,reason:'RECOVERY_TOO_LARGE'};
    if(!Number.isFinite(Date.parse(record.createdAt)) || typeof record.createdAt !== 'string') return {valid:false,reason:'INVALID_TIMESTAMP'};
    const actual=await sha256Hex(record.payload,cryptoApi); if(actual!==record.sha256) return {valid:false,reason:'CHECKSUM_MISMATCH'};
    const diagram=JSON.parse(record.payload); if(!diagram || typeof diagram!=='object' || Array.isArray(diagram)) return {valid:false,reason:'INVALID_DIAGRAM'};
    return {valid:true,diagram};
  } catch { return {valid:false,reason:'INVALID_PAYLOAD_OR_CRYPTO'}; }
}
export function pruneRecoveryRecords(records,limit=DEFAULT_LIMIT) {
  if(!Array.isArray(records)) throw new TypeError('Records must be an array');
  if(!Number.isInteger(limit)||limit<1||limit>100) throw new RangeError('Limit must be 1..100');
  return [...records].filter(x=>x?.schema==='openvisio-recovery-v1').sort((a,b)=>String(b.createdAt).localeCompare(String(a.createdAt))).slice(0,limit);
}

import test from 'node:test';import assert from 'node:assert/strict';import {execFileSync} from 'node:child_process';
test('documentation cumulative incluse et complete',()=>{assert.doesNotThrow(()=>execFileSync(process.execPath,['scripts/verify-release-docs.mjs'],{cwd:new URL('../',import.meta.url).pathname}));});

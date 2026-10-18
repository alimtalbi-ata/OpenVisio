import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>readFileSync(path.join(root,p),'utf8');
const pkg=JSON.parse(read('package.json'));
const version=pkg.version;
const short=version.replace(/\.0$/,'');
const checks=[
 ['.NET',read('windows/native/OpenVisio.csproj').includes(`<Version>${version}</Version>`)],
 ['Inno version',read('windows/installer/OpenVisio.iss').includes(`#define AppVersion "${version}"`)],
 ['Inno output',read('windows/installer/OpenVisio.iss').includes(`OutputBaseFilename=OpenVisio-Setup-v${short}-x64`)],
 ['CMD output',read('Build-OpenVisio-Windows.cmd').includes(`OpenVisio-Setup-v${short}-x64.exe`)],
 ['CMD portable',read('Build-OpenVisio-Windows.cmd').includes('Build-Portable-Windows.ps1')],
 ['single entry',read('Build-Windows-Installer.cmd').includes('Build-OpenVisio-Windows.cmd')],
 ['portable output verified',read('Build-OpenVisio-Windows.cmd').includes(`dist\\portable\\OpenVisio-v${short}-Windows-x64-Portable.exe`) || read('Build-OpenVisio-Windows.cmd').includes(`dist\\portable\\OpenVisio-v${short}-Windows-x64-Portable.exe`)],
 ['manifest after portable',read('Build-OpenVisio-Windows.cmd').indexOf('Build-Portable-Windows.ps1') < read('Build-OpenVisio-Windows.cmd').indexOf('Write-Release-Manifest.ps1')],
];
for(const [name,ok] of checks) console.log(`${ok?'PASS':'FAIL'} ${name}`);
if(checks.some(([,ok])=>!ok))process.exitCode=1;

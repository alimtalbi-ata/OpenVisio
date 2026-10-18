import {readFileSync,writeFileSync,readdirSync,statSync} from 'node:fs';
import {join,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const base=join(root,'documentation');
const release=JSON.parse(readFileSync(join(root,'package.json'),'utf8')).version;
const files={};
function scan(dir){for(const entry of readdirSync(dir,{withFileTypes:true})){const p=join(dir,entry.name);if(entry.isDirectory())scan(p);else if(entry.isFile()&&!entry.name.startsWith('MANIFEST-SHA256-')){const rel=relative(base,p).replaceAll('\\','/');files[rel]=createHash('sha256').update(readFileSync(p)).digest('hex');}}}
scan(base);
const version=release.split('.').slice(0,2).join('.');
writeFileSync(join(base,`MANIFEST-SHA256-V${version}.json`),JSON.stringify({release,files},null,2)+'\n');
console.log('Manifest generated:',release,Object.keys(files).length,'files');

import {readFileSync,existsSync,statSync} from 'node:fs';
import {join,dirname,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const base=join(root,'documentation');
const release=JSON.parse(readFileSync(join(root,'package.json'),'utf8')).version;
const version=release.split('.').slice(0,2).join('.');
const manifest=JSON.parse(readFileSync(join(base,`MANIFEST-SHA256-V${version}.json`),'utf8'));
if(manifest.release!==release)throw Error('Version du manifeste incorrecte');
const required=[`OpenVisio-v${version}-Addendum.docx`,`OpenVisio-v${version}-Addendum.pdf`,`NOTES-DE-VERSION-V${version}.md`,`CAPTURES-UI-V${version}.md`,'manuel-complet-v38.8/OpenVisio-v38.8-Manuel-Complet.docx','manuel-complet-v38.8/OpenVisio-v38.8-Manuel-Complet.pdf'];
for(const name of required)if(!Object.hasOwn(manifest.files,name))throw Error('Document obligatoire non référencé: '+name);
for(const [name,hash] of Object.entries(manifest.files)){
 const p=resolve(base,name);if(!p.startsWith(resolve(base)+sep))throw Error('Chemin interdit: '+name);
 if(!existsSync(p)||statSync(p).size<20)throw Error('Document manquant ou vide: '+name);
 const data=readFileSync(p);
 if(createHash('sha256').update(data).digest('hex')!==hash)throw Error('SHA256 invalide: '+name);
 if(name.endsWith('.pdf')&&!data.subarray(0,5).equals(Buffer.from('%PDF-')))throw Error('Signature PDF invalide: '+name);
 if(name.endsWith('.docx')&&!data.subarray(0,2).equals(Buffer.from('PK')))throw Error('Signature DOCX invalide: '+name);
}
console.log('PASS documentation',release,Object.keys(manifest.files).length,'files');

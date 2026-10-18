import fs from 'node:fs';import path from 'node:path';
const root=path.resolve(process.argv[2]||'.'); const dir=path.join(root,'src');
const modules=fs.readdirSync(dir).filter(x=>x.endsWith('.js'));
const result={modules:modules.length,version:JSON.parse(fs.readFileSync(path.join(root,'package.json'))).version,notes:'Static inventory only; no automatic deletion'};
console.log(JSON.stringify(result,null,2));

// Auteur : Abdelhalim Talbi — import SAN conservé dans le diagramme.
const fabrics=new Set(['A','B']);
export function validateSanImport(value){
 if(value==null)return null;
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Import SAN invalide');
 const vendor=String(value.vendor||'');if(!['brocade','cisco'].includes(vendor))throw Error('Constructeur invalide');
 const fabric=String(value.fabric||'');if(!fabrics.has(fabric))throw Error('Fabric invalide');
 const checkName=x=>{if(typeof x!=='string'||!x.trim()||x.length>128)throw Error('Nom SAN invalide');return x.trim();};
 const list=(v,max=500)=>{if(!Array.isArray(v)||v.length>max)throw Error('Liste SAN invalide');return v;};
 const zonesets=list(value.zonesets).map(z=>({name:checkName(z.name),vsan:z.vsan==null?null:validateVsan(z.vsan),zones:list(z.zones,1024).map(checkName)}));
 const activeConfigurations=list(value.activeConfigurations).map(z=>({name:checkName(z.name),vsan:z.vsan==null?null:validateVsan(z.vsan),source:String(z.source||'').slice(0,128)}));
 const zones=list(value.zones).map(z=>({name:checkName(z.name),vsan:z.vsan==null?null:validateVsan(z.vsan),members:list(z.members,1024).map(checkName)}));
 const aliases={};for(const [k,v] of Object.entries(value.aliases||{})){if(Object.keys(aliases).length>=1000)throw Error('Trop d’alias');aliases[checkName(k)]=list(v,256).map(checkName);}
 return {vendor,fabric,zonesets,activeConfigurations,zones,aliases,warnings:list(value.warnings||[],1000).map(x=>String(x).slice(0,512)),requiresRoleAssignment:true};
}
function validateVsan(v){if(!Number.isInteger(v)||v<1||v>4094)throw Error('VSAN invalide');return v;}
export function compareSanImports(previous,current){
 const a=validateSanImport(previous),b=validateSanImport(current);
 const rows=[];const map=x=>new Map((x?.zonesets||[]).map(z=>[`${x.fabric}:${z.vsan??'-'}:${z.name}`,z]));const left=map(a),right=map(b);
 for(const key of [...new Set([...left.keys(),...right.keys()])].sort()){
  const before=left.get(key),after=right.get(key);
  const status=!before?'added':!after?'removed':JSON.stringify([...new Set(before.zones)].sort())===JSON.stringify([...new Set(after.zones)].sort())?'unchanged':'changed';
  rows.push({key,status,before:(before?.zones||[]).join(', '),after:(after?.zones||[]).join(', ')});
 }
 return rows;
}
export function sanDiffCsv(rows){const q=x=>'"'+String(x??'').replaceAll('"','""').replace(/^[=+@\-]/,'\'$&')+'"';return '\uFEFF'+[['Zoneset / VSAN','Statut','Avant','Après'],...rows.map(r=>[r.key,r.status,r.before,r.after])].map(row=>row.map(q).join(';')).join('\r\n');}

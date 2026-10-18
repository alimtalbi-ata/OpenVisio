// OpenVisio v14.1 — champs SAN structurés. Auteur : Abdelhalim Talbi.
export const SAN_FIELDS = Object.freeze({
 server:[['hbas','Adaptateurs HBA'],['wwpns','WWPN initiateurs'],['multipath','Multipathing (MPIO/DM-Multipath)']],
 storage:[['luns','LUN / volumes']],
});
export function parseSanList(value,field){
 if(!['hbas','wwpns','luns'].includes(field))throw new Error('Champ SAN inconnu');
 const items=String(value??'').split(/[;\n]/).map(s=>s.trim()).filter(Boolean);
 if(items.length>128)throw new Error('Maximum 128 entrées');
 if(items.some(s=>s.length>128))throw new Error('Entrée trop longue (128 caractères maximum)');
 if(field==='wwpns'&&items.some(s=>!/^(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$/.test(s)))throw new Error('WWPN attendu : 10:00:00:00:00:00:00:01');
 const unique=new Set();return items.filter(s=>{const k=s.toLowerCase();if(unique.has(k))return false;unique.add(k);return true;});
}
export function parseSanProperty(field,value){
 if(['hbas','wwpns','luns'].includes(field))return parseSanList(value,field);
 if(field==='multipath'){const v=String(value??'').trim();if(v.length>128)throw new Error('Multipathing trop long');return v;}
 throw new Error('Champ SAN inconnu');
}
export function sanFieldsForNode(node){const type=String(node?.type??'').toLowerCase();if(type==='server')return SAN_FIELDS.server;if(['storage','storage-array','san-storage','array'].includes(type))return SAN_FIELDS.storage;return [];}

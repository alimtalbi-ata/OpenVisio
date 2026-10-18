// OpenVisio v14.5 — éditeur de masking déclaratif. Auteur : Abdelhalim Talbi.
const clean=v=>String(v??'').trim();
const wwpn=/^(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$/;
export function validateLunMasking(value,luns=[]){
 if(!Array.isArray(value))throw Error('Le masking doit être une liste');
 if(value.length>512)throw Error('Maximum 512 associations');
 const known=new Set((Array.isArray(luns)?luns:[]).map(x=>clean(x).toLowerCase()));
 const seen=new Set();return value.map((row,i)=>{
  if(!row||typeof row!=='object'||Array.isArray(row))throw Error(`Ligne ${i+1} invalide`);
  const lunId=clean(row.lunId),initiatorWwpn=clean(row.initiatorWwpn).toLowerCase();
  if(!lunId||lunId.length>128)throw Error(`LUN invalide ligne ${i+1}`);
  if(!wwpn.test(initiatorWwpn))throw Error(`WWPN invalide ligne ${i+1}`);
  if(known.size&&!known.has(lunId.toLowerCase()))throw Error(`LUN non déclarée : ${lunId}`);
  const key=JSON.stringify([lunId.toLowerCase(),initiatorWwpn]);if(seen.has(key))throw Error(`Association dupliquée ligne ${i+1}`);seen.add(key);
  return {lunId,initiatorWwpn};
 });
}
export function parseLunMasking(text,luns=[]){
 const lines=String(text??'').split(/\r?\n/).map(s=>s.trim()).filter(Boolean);
 if(lines.length>512)throw Error('Maximum 512 associations');
 return validateLunMasking(lines.map((line,i)=>{const cells=line.split(';').map(clean);if(cells.length!==2)throw Error(`Ligne ${i+1} : format LUN ; WWPN attendu`);return {lunId:cells[0],initiatorWwpn:cells[1]};}),luns);
}
export function formatLunMasking(value){return (Array.isArray(value)?value:[]).map(r=>`${clean(r.lunId)} ; ${clean(r.initiatorWwpn)}`).join('\n');}

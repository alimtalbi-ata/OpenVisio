// OpenVisio v28.5 — filtres documentaires sans mutation du modèle.
export function filterSanLines(lines, fabric='all') {
 if (!['all','A','B','unknown'].includes(fabric)) throw new RangeError('Fabric invalide');
 if (!Array.isArray(lines)) return [];
 return lines.filter(line => {
  if (fabric==='all') return true;
  const value=String(line);
  const match=value.match(/\bFabric\s*([AB])\b/i);
  if (fabric==='unknown') return /fabric\s*(?:inconnue|non renseignée|unknown)/i.test(value);
  return match ? match[1].toUpperCase()===fabric : false;
 });
}

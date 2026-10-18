// Mesures de coût de rendu interactif, sans stockage persistant.
// Auteur : Abdelhalim Talbi
export function createInteractionMetrics({capacity=120}={}){
 if(!Number.isInteger(capacity)||capacity<1)throw new RangeError('capacity must be a positive integer');
 const samples=[];let total=0;
 return {
  record(duration){if(!Number.isFinite(duration)||duration<0)return false;samples.push(duration);total+=duration;if(samples.length>capacity)total-=samples.shift();return true;},
  snapshot(){const ordered=[...samples].sort((a,b)=>a-b),n=ordered.length;return {count:n,meanMs:n?total/n:0,p50Ms:n?ordered[Math.ceil(.5*n)-1]:0,p95Ms:n?ordered[Math.ceil(.95*n)-1]:0,maxMs:n?ordered[n-1]:0,over16ms:samples.filter(x=>x>16.67).length};},
  reset(){samples.length=0;total=0;}
 };
}

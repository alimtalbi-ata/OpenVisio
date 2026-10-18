// OpenVisio v41.12 — value-based mutation tracking; Abdelhalim Talbi.
export function edgeMutationSignature(edge){
 if(!edge||typeof edge!=='object')throw new TypeError('Invalid edge');
 return JSON.stringify([edge.from,edge.to,edge.style,edge.offset,edge.waypoints,edge.fromPort,edge.toPort,edge.sourceInterface,edge.targetInterface]);
}
export function changedEdgeIds(previous,edges){
 if(!(previous instanceof Map)||!Array.isArray(edges))throw new TypeError('Invalid mutation snapshot');
 const next=new Map();
 for(const edge of edges){
  if(edge?.id===undefined||edge?.id===null)throw new TypeError('Missing edge id');
  const id=String(edge.id);
  if(next.has(id))throw new Error(`Duplicate edge id: ${id}`);
  next.set(id,edgeMutationSignature(edge));
 }
 const dirty=[];
 for(const [id,signature] of previous)if(next.get(id)!==signature)dirty.push(id);
 for(const id of next.keys())if(!previous.has(id))dirty.push(id);
 return {next,dirty};
}

// v41.13 — mutation transaction: immutable snapshots and explicit affected IDs.
export function createEdgeMutationSession(initialEdges=[]){
 let snapshot=changedEdgeIds(new Map(),initialEdges).next;
 return Object.freeze({
  reconcile(edges){
   const {next,dirty}=changedEdgeIds(snapshot,edges);
   snapshot=next;
   return Object.freeze({dirty:Object.freeze([...dirty]),changed:dirty.length>0});
  },
  snapshot(){return new Map(snapshot);},
  reset(edges=[]){ snapshot=changedEdgeIds(new Map(),edges).next; return new Map(snapshot); }
 });
}

// v41.15 — reconcile edits through a single invalidation callback.
export function reconcileEdgeTransaction(session, edges, invalidate){
 if(!session||typeof session.reconcile!=="function"||typeof invalidate!=="function")throw new TypeError("Invalid transaction");
 const result=session.reconcile(edges);
 if(result.changed)invalidate(result.dirty);
 return result;
}

/** Synthetic SAN topology diagnostic. Read-only: never changes input data. */
export function analyzeSanRedundancy(diagram) {
  const nodes = Array.isArray(diagram?.nodes) ? diagram.nodes : [];
  const edges = Array.isArray(diagram?.edges) ? diagram.edges : [];
  const byId = new Map(nodes.map(n => [n.id, n]));
  const issues = [];
  // Validate model identity before traversing paths. Duplicate IDs otherwise silently
  // overwrite nodes in the lookup and produce misleading redundancy results.
  const seenNodes = new Set();
  for (const node of nodes) {
    if (node.id === undefined || node.id === null || node.id === '') issues.push({code:'MISSING_NODE_ID',severity:'error'});
    else if (seenNodes.has(node.id)) issues.push({code:'DUPLICATE_NODE_ID',nodeId:node.id,severity:'error'});
    else seenNodes.add(node.id);
  }
  const seenEdges = new Set();
  for (const edge of edges) {
    if (edge.id !== undefined && edge.id !== null) {
      if (seenEdges.has(edge.id)) issues.push({code:'DUPLICATE_EDGE_ID',edgeId:edge.id,severity:'error'});
      seenEdges.add(edge.id);
    }
    if (edge.source === edge.target) issues.push({code:'SELF_LOOP',edgeId:edge.id,severity:'warning'});
  }
  const adjacency = new Map(nodes.map(n => [n.id, []]));
  for (const edge of edges) {
    if (!byId.has(edge.source) || !byId.has(edge.target)) {
      issues.push({code:'DANGLING_LINK', edgeId:edge.id, severity:'error'});
      continue;
    }
    const fabric = String(edge.fabric ?? '').toUpperCase();
    if (fabric !== 'A' && fabric !== 'B') {
      issues.push({code:'UNKNOWN_FABRIC', edgeId:edge.id, severity:'warning'});
      continue;
    }
    adjacency.get(edge.source).push({to:edge.target, fabric, edgeId:edge.id});
    adjacency.get(edge.target).push({to:edge.source, fabric, edgeId:edge.id});
    for (const endpoint of [edge.source, edge.target]) {
      const nodeFabric = String(byId.get(endpoint).fabric ?? '').toUpperCase();
      if (nodeFabric && nodeFabric !== fabric) issues.push({code:'FABRIC_MISMATCH', edgeId:edge.id, nodeId:endpoint, severity:'error'});
    }
  }
  const hosts = nodes.filter(n => n.type === 'server' && n.multipath === true);
  const arrays = nodes.filter(n => n.type === 'storage');
  const paths = [];
  // Shortest documented route per fabric, bounded by visited nodes (cycle-safe).
  function trace(source, destination, fabric, blockedNodes = new Set(), blockedEdges = new Set()) {
    if (blockedNodes.has(source) || blockedNodes.has(destination)) return null;
    if (!adjacency.has(source) || !adjacency.has(destination)) return null;
    const queue=[source], visited=new Set([source]), previous=new Map();
    for (let i=0;i<queue.length;i++) {
      const current=queue[i];
      if (current===destination) {
        const nodeIds=[current], edgeIds=[];
        while (previous.has(nodeIds[0])) {
          const step=previous.get(nodeIds[0]);
          edgeIds.unshift(step.edgeId);nodeIds.unshift(step.from);
        }
        return {nodeIds,edgeIds};
      }
      for (const edge of adjacency.get(current) ?? []) {
        if (edge.fabric!==fabric || visited.has(edge.to) || blockedNodes.has(edge.to) || blockedEdges.has(edge.edgeId)) continue;
        visited.add(edge.to);previous.set(edge.to,{from:current,edgeId:edge.edgeId});queue.push(edge.to);
      }
    }
    return null;
  }
  for (const host of hosts) for (const array of arrays) {
    const routeA=trace(host.id,array.id,'A');
    const routeB=trace(host.id,array.id,'B');
    // Assess alternatives without assuming the first shortest route is unique.
    // A transit/edge is critical only when removing it disconnects that fabric.
    function assess(route, fabric) {
      if (!route) return {criticalTransitIds:[],criticalEdgeIds:[],alternativeRoutes:[]};
      const criticalTransitIds=[],criticalEdgeIds=[],alternativeRoutes=[];
      for (const id of route.nodeIds.slice(1,-1)) {
        const alt=trace(host.id,array.id,fabric,new Set([id]));
        if (!alt) criticalTransitIds.push(id); else alternativeRoutes.push(alt);
      }
      for (const id of route.edgeIds) {
        const alt=trace(host.id,array.id,fabric,new Set(),new Set([id]));
        if (!alt) criticalEdgeIds.push(id); else alternativeRoutes.push(alt);
      }
      const unique=new Map(alternativeRoutes.map(r=>[JSON.stringify(r.edgeIds),r]));
      return {criticalTransitIds,criticalEdgeIds,alternativeRoutes:[...unique.values()]};
    }
    const resilienceA=assess(routeA,'A'), resilienceB=assess(routeB,'B');
    const fabricA=!!routeA, fabricB=!!routeB;
    // Compare only intermediate infrastructure; endpoints are necessarily shared.
    const transitA = new Set(routeA?.nodeIds.slice(1,-1) ?? []);
    const transitB = new Set(routeB?.nodeIds.slice(1,-1) ?? []);
    const sharedTransitIds = [...transitA].filter(id=>transitB.has(id));
    const linksA = new Set(routeA?.edgeIds ?? []);
    const sharedEdgeIds = (routeB?.edgeIds ?? []).filter(id=>linksA.has(id));
    // Check shared physical failure domains across ALL available routes, not just
    // the chosen shortest paths. A node/edge is a common single-failure point
    // only if its removal disconnects both fabrics simultaneously.
    const candidateNodeIds = nodes.map(n=>n.id).filter(id=>id!==host.id && id!==array.id);
    const candidateEdgeIds = edges.map(e=>e.id).filter(id=>id!==undefined && id!==null);
    const commonCriticalNodeIds = fabricA && fabricB ? candidateNodeIds.filter(id => {
      const blocked=new Set([id]);
      return !trace(host.id,array.id,'A',blocked) && !trace(host.id,array.id,'B',blocked);
    }) : [];
    const commonCriticalEdgeIds = fabricA && fabricB ? candidateEdgeIds.filter(id => {
      const blocked=new Set([id]);
      return !trace(host.id,array.id,'A',new Set(),blocked) && !trace(host.id,array.id,'B',new Set(),blocked);
    }) : [];
    // Correlated failure domains: all components carrying the same declared
    // domain key fail together. A single member may be non-critical while the
    // simultaneous loss of a shared chassis/site/power domain is critical.
    // Domain values are user-provided topology metadata, not discovered facts.
    const failureDomains = new Map();
    const addDomain = (kind, value, componentKind, id) => {
      if (typeof value !== 'string' || !value.trim()) return;
      const key = `${kind}:${value.trim()}`;
      if (!failureDomains.has(key)) failureDomains.set(key,{kind,value:value.trim(),nodeIds:new Set(),edgeIds:new Set()});
      failureDomains.get(key)[componentKind].add(id);
    };
    const domainKeys = ['site','chassis','powerDomain','controller','failureDomain'];
    for (const node of nodes) for (const key of domainKeys) addDomain(key,node[key],'nodeIds',node.id);
    for (const edge of edges) for (const key of domainKeys) addDomain(key,edge[key],'edgeIds',edge.id);
    const commonCriticalDomains = fabricA && fabricB ? [...failureDomains.values()].flatMap(domain => {
      const blockedNodes=new Set([...domain.nodeIds].filter(id=>id!==host.id && id!==array.id));
      const blockedEdges=new Set(domain.edgeIds);
      // Endpoints are shared by definition and are excluded from domain
      // independence checks; their availability is a separate concern.
      if (!blockedNodes.size && !blockedEdges.size) return [];
      if (trace(host.id,array.id,'A',blockedNodes,blockedEdges) || trace(host.id,array.id,'B',blockedNodes,blockedEdges)) return [];
      return [{kind:domain.kind,value:domain.value,nodeIds:[...blockedNodes],edgeIds:[...blockedEdges]}];
    }) : [];
    const independence = !fabricA || !fabricB ? 'INCOMPLETE' :
      (commonCriticalNodeIds.length || commonCriticalEdgeIds.length || commonCriticalDomains.length ? 'SHARED_RISK' : 'INDEPENDENT');
    paths.push({hostId:host.id,arrayId:array.id,fabricA,fabricB,routeA,routeB,sharedTransitIds,sharedEdgeIds,independence,resilienceA,resilienceB,commonCriticalNodeIds,commonCriticalEdgeIds,commonCriticalDomains});
    if (independence === 'SHARED_RISK') issues.push({code:'SHARED_FABRIC_TRANSIT',hostId:host.id,arrayId:array.id,nodeIds:commonCriticalNodeIds,edgeIds:commonCriticalEdgeIds,domains:commonCriticalDomains,severity:'error'});
    if (!fabricA || !fabricB) issues.push({code:'REDUNDANCY_LOST',hostId:host.id,arrayId:array.id,missingFabrics:[...(!fabricA?['A']:[]),...(!fabricB?['B']:[])],severity:'error'});
  }
  for (const node of nodes.filter(n=>n.type==='san-switch')) {
    if (!node.zoneset || !Array.isArray(node.zoning) || node.zoning.length===0) issues.push({code:'ZONING_INCOMPLETE',nodeId:node.id,severity:'warning'});
  }
  return {ok: !issues.some(i=>i.severity==='error'),paths,issues};
}

import test from "node:test";
import assert from "node:assert/strict";
import {intersectsObstacle,routeAvoidingObstacles} from "../src/routing.js";
const a={x:0,y:100,w:80,h:60},b={x:350,y:100,w:80,h:60},o={x:180,y:80,w:90,h:110};
test("segment traversant obstacle détecté",()=>assert.equal(intersectsObstacle({x:100,y:130},{x:320,y:130},o),true));
test("segment éloigné accepté",()=>assert.equal(intersectsObstacle({x:100,y:20},{x:320,y:20},o),false));
test("routage d'évitement renvoie un chemin",()=>assert.ok(routeAvoidingObstacles(a,b,[o]).path.startsWith("M ")));
test("routage sans obstacle renvoie un chemin",()=>assert.ok(routeAvoidingObstacles(a,b,[]).points.length>=2));

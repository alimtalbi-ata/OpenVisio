import {benchmarkRoutes} from "../src/benchmark.js";
import {writeFileSync} from "node:fs";
const results=[100,500,1000].map(n=>benchmarkRoutes(n));
const report={environment:{node:process.version,platform:process.platform,arch:process.arch},scope:"Node.js route computation only; not browser SVG rendering",results};
writeFileSync(new URL("../BENCHMARK-RESULTS.json",import.meta.url),JSON.stringify(report,null,2));
console.table(results);

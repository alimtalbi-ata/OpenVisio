// OpenVisio — Auteur : Abdelhalim Talbi
export function resizeFromCorner(node, dx, dy, {minWidth=40,minHeight=30,grid=0,proportional=false}={}) {
 if(!node||![node.w,node.h,dx,dy].every(Number.isFinite)) throw new Error('Dimensions invalides');
 const quantize=v=>grid>0?Math.round(v/grid)*grid:v;
 let w=Math.max(minWidth,quantize(node.w+dx));
 let h=Math.max(minHeight,quantize(node.h+dy));
 if(proportional){const ratio=node.w/node.h;if(!Number.isFinite(ratio)||ratio<=0)throw new Error('Ratio invalide');if(Math.abs(dx/node.w)>=Math.abs(dy/node.h))h=Math.max(minHeight,w/ratio);else w=Math.max(minWidth,h*ratio);}
 return {w,h};
}
export function rulerTicks(start,end,step=100){if(![start,end,step].every(Number.isFinite)||step<=0||end<start||end-start>100000)throw new Error('Graduation invalide');const ticks=[];for(let x=Math.ceil(start/step)*step;x<=end&&ticks.length<1000;x+=step)ticks.push(x);return ticks;}

// Regroupe les rafraîchissements demandés pendant une même frame.
// Auteur : Abdelhalim Talbi
export function createFrameScheduler(draw,{request=callback=>requestAnimationFrame(callback),cancel=id=>cancelAnimationFrame(id)}={}){
 let pending=null,disposed=false;
 function flush(){if(disposed)return;pending=null;draw();}
 return {
  schedule(){if(disposed||pending!==null)return false;pending=request(flush);return true;},
  flush(){if(disposed)return false;if(pending===null)return false;cancel(pending);pending=null;draw();return true;},
  cancel(){if(pending===null)return false;cancel(pending);pending=null;return true;},
  dispose(){if(pending!==null)cancel(pending);pending=null;disposed=true;},
  get pending(){return pending!==null;}
 };
}

/* PES mobile Services gesture pacing. Native scroll everywhere else.
 * One vertical touch gesture on the pinned stage travels at most one chapter.
 * No wheel interception, global touch listeners or body lock. The existing
 * chapter engine continues to render every frame from window.scrollY.
 */
const section=document.querySelector('.pes-services-cinema');
const track=section?.querySelector('[data-collection-track]');
const stage=section?.querySelector('[data-collection-stage]');
const tabs=[...section?.querySelectorAll('[data-collection-tab]')||[]];
const mobile=matchMedia('(max-width:767px) and (orientation:portrait) and (prefers-reduced-motion:no-preference)');
let gesture=null,animation=0;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const geometry=()=>{const top=track.getBoundingClientRect().top+scrollY,distance=Math.max(1,track.offsetHeight-stage.offsetHeight);return {top,distance,step:distance/tabs.length};};
const enabled=()=>mobile.matches&&navigator.maxTouchPoints>0&&section?.classList.contains('is-cinema-active')&&tabs.length>1;
const stop=()=>{if(animation)cancelAnimationFrame(animation);animation=0;};
function settle(target){
 stop();
 const start=scrollY,delta=target-start,t0=performance.now();
 const tick=t=>{
  if(!enabled()){animation=0;return;}
  const p=clamp((t-t0)/360,0,1),e=p*p*(3-2*p);
  window.scrollTo({top:start+delta*e,behavior:'instant'});
  animation=p<1?requestAnimationFrame(tick):0;
 };
 animation=requestAnimationFrame(tick);
}
function start(e){
 stop();gesture=null;
 if(!enabled()||e.touches.length!==1)return;
 const t=e.touches[0],g=geometry(),rect=stage.getBoundingClientRect();
 // Include the stage as it enters/leaves, but never grab another section.
 if(rect.bottom<innerHeight*.4||rect.top>innerHeight*.6)return;
 const selected=tabs.findIndex(x=>x.getAttribute('aria-selected')==='true');
 if(selected<0)return;
 const pos=clamp((scrollY-g.top)/g.step,0,tabs.length-.0001);
 gesture={id:t.identifier,x:t.clientX,y:t.clientY,lastY:t.clientY,start:scrollY,selected,pos,g,dir:0,captured:false};
}
function move(e){
 const a=gesture;
 if(!a||!enabled()||e.touches.length!==1){gesture=null;return;}
 const t=[...e.touches].find(t=>t.identifier===a.id);if(!t)return;
 const dy=a.y-t.clientY,dx=t.clientX-a.x;
 a.lastY=t.clientY;
 if(!a.captured){
  if(Math.max(Math.abs(dy),Math.abs(dx))<4)return;
  if(Math.abs(dx)>=Math.abs(dy)||!e.cancelable){gesture=null;return;}
  a.dir=Math.sign(dy);
  const before=a.start<a.g.top-3,after=a.start>a.g.top+a.g.distance+3;
  // Native outward swipe at either boundary; visitors can always leave.
  if((before&&a.dir<0)||(after&&a.dir>0)||(!before&&!after&&((a.selected===0&&a.dir<0)||(a.selected===tabs.length-1&&a.dir>0)))){gesture=null;return;}
  a.targetIndex=before?0:after?tabs.length-1:clamp(a.selected+a.dir,0,tabs.length-1);
  a.captured=true;
 }
 if(!e.cancelable){gesture=null;return;}
 e.preventDefault();
 const g=geometry(),target=g.top+(a.targetIndex+.16)*g.step;
 const low=Math.min(a.start,target),high=Math.max(a.start,target);
 window.scrollTo({top:clamp(a.start+dy,low,high),behavior:'instant'});
}
function end(e){
 const a=gesture;gesture=null;
 if(!a?.captured||!enabled())return;
 if(e.cancelable)e.preventDefault();
 const dy=a.y-a.lastY,g=geometry();
 const index=Math.abs(dy)>=35&&Math.sign(dy)===a.dir?a.targetIndex:a.selected;
 const target=g.top+(index+.16)*g.step;
 settle(target);
}
function cancel(){gesture=null;stop();}
if(stage&&track){
 stage.addEventListener('touchstart',start,{passive:true});
 stage.addEventListener('touchmove',move,{passive:false});
 stage.addEventListener('touchend',end,{passive:false});
 stage.addEventListener('touchcancel',cancel,{passive:true});
 // Direct navigation is always available and cancels any settling gesture.
 stage.addEventListener('click',stop,true);
 stage.addEventListener('keydown',stop,true);
 mobile.addEventListener('change',cancel);
 window.addEventListener('pagehide',cancel);
}

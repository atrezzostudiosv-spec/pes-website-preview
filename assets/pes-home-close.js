/* PES home close: continuous native scroll with stable sticky geometry.
 * No GSAP global refresh, wheel/touch handlers, scroll snap or timers. */
const scene=document.querySelector('#pes-connect');
const stage=scene?.querySelector('.pes-connect-stage');
const footer=document.querySelector('#pes-footer');
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
const short=matchMedia('(max-height:599px)');
const mobile=matchMedia('(max-width:820px)');
const clamp=x=>Math.max(0,Math.min(1,x));
let raf=0,observer=null,active=false;
function draw(){
 raf=0;
 if(!active)return;
 const rect=scene.getBoundingClientRect(), travel=Math.max(1,scene.offsetHeight-stage.offsetHeight);
 const p=clamp(-rect.top/travel);
 scene.dataset.pesConnectProgress=p.toFixed(3);
 scene.style.setProperty('--pes-connect-scale',(1+(mobile.matches?.16:.24)*p).toFixed(4));
 scene.style.setProperty('--pes-connect-dark',(clamp((p-.72)/.28)*.15).toFixed(4));
}
function request(){if(active&&!raf)raf=requestAnimationFrame(draw);}
function sync(){
 active=!!scene&&!!stage&&!reduce.matches&&!short.matches;
 scene?.classList.toggle('is-pes-connect-active',active);
 if(!active){
  if(raf)cancelAnimationFrame(raf);raf=0;
  scene?.style.removeProperty('--pes-connect-scale');
  scene?.style.removeProperty('--pes-connect-dark');
  if(scene)delete scene.dataset.pesConnectProgress;
 }else request();
}
if(scene&&stage){
 window.addEventListener('scroll',request,{passive:true});
 window.addEventListener('resize',request,{passive:true});
 window.addEventListener('pageshow',request);
 reduce.addEventListener('change',sync);short.addEventListener('change',sync);mobile.addEventListener('change',request);
 if('ResizeObserver' in window){observer=new ResizeObserver(request);observer.observe(scene);observer.observe(stage);}
 document.fonts?.ready.then(request).catch(()=>{});
 sync();
}
if(footer&&'IntersectionObserver' in window){
 const light=footer.querySelector('.pes-footer-light');
 const io=new IntersectionObserver(entries=>{
  if(entries.some(e=>e.isIntersecting)&&!reduce.matches){footer.classList.add('is-neon-lit');io.disconnect();}
 },{threshold:0});
 if(light)io.observe(light);
}

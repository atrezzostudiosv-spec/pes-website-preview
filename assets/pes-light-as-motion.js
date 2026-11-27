/* PES Light as Motion V1.1. Frame geometry only; no pin, transform, timer,
   ScrollTrigger refresh, scroll interception, or vendor animation changes. */
const clamp=n=>Math.max(0,Math.min(1,n));
const smooth=n=>{const x=clamp(n);return x*x*(3-2*x);};
const configs=[
 {track:'#pes-featured-project',stage:'.ats-stage',enter:.88,clear:.12,exit:1.12,end:.42,enabled:t=>!!t.closest('.ats-enhanced')&&!t.closest('.ats-manual-reduced')},
 {track:'#pes-services [data-collection-track]',stage:'.collection-stage',enter:.95,clear:.08,pinReveal:.32,exit:1.12,end:.40,enabled:t=>!!t.closest('.is-cinema-active')},
 {track:'#ats2-handoff',stage:'.ats2-stage',enter:.90,clear:.10,pinReveal:.32,exit:1.14,end:.40,enabled:t=>!!t.closest('.ats2-enhanced')}
];
const scenes=configs.map(c=>{const track=document.querySelector(c.track);return {...c,track,stage:track?.querySelector(c.stage)};}).filter(c=>c.stage);
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const short=matchMedia('(max-height:599px)');
let raf=0;
function reset(stage){
 if(!stage.hasAttribute('data-pes-light-ready'))return;
 stage.removeAttribute('data-pes-light-ready');
 stage.style.removeProperty('--pes-light-in');stage.style.removeProperty('--pes-light-out');
}
function draw(){
 raf=0;
 const vh=window.innerHeight||document.documentElement.clientHeight;
 const updates=scenes.map(c=>{
  if(reduced.matches||short.matches||!c.enabled(c.track))return {stage:c.stage,active:false};
  const track=c.track.getBoundingClientRect(),stage=c.stage.getBoundingClientRect();
  // Keep a fully black upper edge until sticky arrival. Reveal over the
  // first 0.32 viewport of existing pinned travel, never before it.
  const enter=c.pinReveal
   ? 1-smooth(-track.top/(vh*c.pinReveal))
   : smooth((stage.top/vh-c.clear)/(c.enter-c.clear));
  const exit=smooth((c.exit-track.bottom/vh)/(c.exit-c.end));
  return {stage:c.stage,active:true,enter,exit};
 });
 for(const u of updates){
  if(!u.active){reset(u.stage);continue;}
  const a=u.enter.toFixed(4),b=u.exit.toFixed(4);
  if(u.stage.style.getPropertyValue('--pes-light-in')!==a)u.stage.style.setProperty('--pes-light-in',a);
  if(u.stage.style.getPropertyValue('--pes-light-out')!==b)u.stage.style.setProperty('--pes-light-out',b);
  if(!u.stage.hasAttribute('data-pes-light-ready'))u.stage.setAttribute('data-pes-light-ready','');
 }
}
function request(){if(!raf)raf=requestAnimationFrame(draw);}
if(scenes.length){
 window.addEventListener('scroll',request,{passive:true});
 window.addEventListener('resize',request,{passive:true});
 window.addEventListener('pageshow',request);
 window.addEventListener('load',request,{once:true});
 reduced.addEventListener('change',request);short.addEventListener('change',request);
 if('ResizeObserver' in window){const ro=new ResizeObserver(request);for(const c of scenes){ro.observe(c.track);ro.observe(c.stage);}}
 if('MutationObserver' in window){
  const mo=new MutationObserver(request);
  const targets=new Set(scenes.flatMap(c=>[c.track,c.track.parentElement,c.track.closest('.ats-scope,.ats2-scope,.collection-section')]).filter(Boolean));
  for(const t of targets)mo.observe(t,{attributes:true,attributeFilter:['class']});
 }
 document.fonts?.ready.then(request).catch(()=>{});
 request();
}

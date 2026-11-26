/* ATZ-SCR-007 — PES Cinematic Variant V1.0.
 * Original Codrops/ATREZZO files preserved under vendor/atz-scr-007-original.
 * Explicit client variation: shorter scroll, mobile scale and final black fade.
 */
import {mountScene} from './vendor/atz-scr-007-original/runtime/lifecycle.js';
const root=document.querySelector('[data-pes-cinematic="ATZ-SCR-007"]');
const media=matchMedia('(max-width:700px)');
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
let instance;
function mount(){
 if(!root)return;
 instance?.destroy();instance=undefined;
 root.classList.remove('pes-cinematic-animated');
 const gsap=window.gsap,ScrollTrigger=window.ScrollTrigger;
 if(reduce.matches||!gsap||!ScrollTrigger)return;
 root.classList.add('pes-cinematic-animated');
 try{
  const compact=media.matches;
  const animate=(scope,gsap)=>{
   const grid=scope.querySelector('[data-grid-sixth]');
   const gridImages=grid.querySelectorAll('.grid__img');
   const title=scope.querySelector('.content__title');
   // Original edge stagger, group scale/skew and reversible scrub.
   const tl=gsap.timeline({paused:true,defaults:{ease:'none'}});
   tl.fromTo(gridImages,{scale:compact ? .88 : .7,autoAlpha:0},{scale:1,autoAlpha:1,stagger:{amount:.03,from:'edges',grid:[3,3]},duration:.5},0)
     .fromTo(grid,{scale:compact ? .88 : .7,skewY:compact ? 2 : 5},{scale:1,skewY:0,duration:.5},0);
   // The title has a single coordinated entrance and remains spatially stable.
   tl.fromTo(title,{opacity:0},{opacity:1,duration:.22},.08);
   const zoomEnd=tl.duration();
   // Final fade is part of the same scrub timeline, not a separate effect.
   tl.to(grid,{opacity:0,duration:.22},zoomEnd)
     .to(title,{opacity:0,duration:.18},zoomEnd+.02);
   // Bind the completed timeline; avoid invalidating from() start values during refresh.
   ScrollTrigger.create({animation:tl,trigger:root,start:'top top',end:()=>'+='+Math.round(window.innerHeight*(compact ? .58 : 1)),pin:root,scrub:.5,anticipatePin:1});
  };
  instance=mountScene(root,'[data-grid-sixth]',animate,{gsap,ScrollTrigger,mobileMax:0});
  if(instance.mode!=='animated')root.classList.remove('pes-cinematic-animated');
 }catch(e){root.classList.remove('pes-cinematic-animated');instance?.destroy();console.warn('PES cinematic static fallback',e);}
}
media.addEventListener('change',mount);reduce.addEventListener('change',mount);
window.addEventListener('load',()=>{if(!instance)mount();else window.ScrollTrigger?.refresh();},{once:true});
if(document.readyState==='complete')mount();else if(window.gsap&&window.ScrollTrigger)mount();

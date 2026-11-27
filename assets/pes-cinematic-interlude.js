/* PES V1.4 — original ATZ-SCR-007, unchanged.
 * Only readiness, geometry refresh and independent transition layers are client code.
 */
import {nativeComponentsReady} from './mount-component.js?v=handoff-reading-1';
import {mount as mountOriginal} from './vendor/atz-scr-007-original/scroll/ATZ-SCR-007.js';
const root=document.querySelector('[data-pes-cinematic="ATZ-SCR-007"]');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
let instance,pin,readyPromise,observer,geometry='',refreshFrame=0,paintFrame=0,restoreUpdate;
const clamp=n=>Math.min(1,Math.max(0,n));
const backdrop=root?.querySelector('.pes-cinematic-backdrop');
const veil=root?.querySelector('.pes-cinematic-veil');
const entryVeil=root?.querySelector('.pes-cinematic-entry-veil');
const smooth=n=>{const x=clamp(n);return x*x*(3-2*x);};
// The entrance veil hides the stationary scene before pinning. Release it against
// the actual scrubbed timeline, not the raw scroll target. The exit veil remains
// independent. No writes to tile transforms, alpha, scale, title, or timing.
function paint(){
 paintFrame=0;
 if(!instance||instance.mode!=='animated'||!pin||!backdrop||!veil||!entryVeil)return;
 const p=clamp(pin.animation.progress());
 const exit=clamp((scrollY-pin.end)/Math.max(1,root.clientHeight*.85));
 // Keep a dark gradient until motion is already occurring; fully release by
 // 32% of the original timeline. Smoothstep avoids a visible start/stop edge.
 entryVeil.style.opacity=String(1-smooth((p-.015)/.305));
 backdrop.style.opacity=String(1-smooth(p/.30));
 veil.style.opacity=String(exit);
}
function queuePaint(){
 if(!paintFrame)paintFrame=requestAnimationFrame(paint);
}
function unmount(){
 restoreUpdate?.();restoreUpdate=undefined;
 if(paintFrame)cancelAnimationFrame(paintFrame);paintFrame=0;
 instance?.destroy();instance=undefined;pin=undefined;
 root?.classList.remove('pes-cinematic-animated');
 if(backdrop)backdrop.style.opacity='0';
 if(veil)veil.style.opacity='0';
 if(entryVeil)entryVeil.style.opacity='0';
}
function mount(){
 if(!root||instance||reduced.matches||!window.gsap||!window.ScrollTrigger)return;
 const grid=root.querySelector('[data-grid-sixth]');
 if(!grid||grid.querySelectorAll('.grid__img').length!==9)return;
 try{
  root.classList.add('pes-cinematic-animated');
  // Invoke the byte-identical original module. Explicitly enable it on mobile
  // via its documented lifecycle option; do not change the animation parameters.
  instance=mountOriginal(root,{gsap:window.gsap,ScrollTrigger:window.ScrollTrigger,mobileMax:0});
  pin=window.ScrollTrigger.getAll().find(t=>t.pin===root);
  if(instance.mode!=='animated'||!pin){unmount();return;}
  // Listen to rendered animation updates, including the .5 s scrub tail
  // after a wheel/touch gesture stops. Preserve any existing callback.
  const timeline=pin.animation;
  const previous=timeline.eventCallback('onUpdate');
  const params=timeline.vars.onUpdateParams;
  timeline.eventCallback('onUpdate',function(...args){previous?.apply(this,args);queuePaint();},params);
  restoreUpdate=()=>timeline.eventCallback('onUpdate',previous||null,params);
  paint();
 }catch(error){unmount();console.warn('PES original cinematic static fallback',error);}
}
function upstream(){
 const nodes=[document.querySelector('.hero-film'),document.querySelector('.pes-specialty'),document.querySelector('.pes-featured-split')].filter(Boolean);
 return {nodes,signature:nodes.map(n=>[n.offsetWidth,n.offsetHeight,n.offsetTop].join(':')).join('|')};
}
function scheduleRefresh(force=false){
 if(!pin)return;
 const signature=upstream().signature;
 if(!force&&signature===geometry)return;
 geometry=signature;
 if(refreshFrame)return;
 refreshFrame=requestAnimationFrame(()=>{
  refreshFrame=0;
  if(pin){window.ScrollTrigger.refresh();queuePaint();}
 });
}
function observeUpstream(){
 if(observer||!('ResizeObserver' in window))return;
 const {nodes,signature}=upstream();geometry=signature;
 observer=new ResizeObserver(()=>scheduleRefresh());
 nodes.forEach(n=>observer.observe(n));
}
async function ready(){
 if(!readyPromise)readyPromise=(async()=>{
  await nativeComponentsReady;
  if(document.fonts?.ready)await document.fonts.ready;
  await frame();await frame();
 })();
 await readyPromise;
 if(reduced.matches){unmount();return;}
 if(!instance)mount();else scheduleRefresh(true);
 observeUpstream();
}
if(root){
 reduced.addEventListener('change',()=>{unmount();ready();});
 window.addEventListener('scroll',queuePaint,{passive:true});
 window.addEventListener('pageshow',()=>ready());
 window.addEventListener('load',()=>ready(),{once:true});
 // ScrollTrigger owns resize handling. Avoid a second refresh on every mobile
 // toolbar resize; upstream ResizeObserver handles actual geometry changes.
 ready().catch(error=>{unmount();console.error('PES cinematic readiness failed',error);});
}

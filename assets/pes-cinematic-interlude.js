/* ATZ-SCR-007 — PES Cinematic Refinement V1.2.
 * Original reference and lifecycle preserved in vendor. This instance uses its own
 * GSAP context because entry, pin and exit have distinct scroll ranges.
 */
import {nativeComponentsReady} from './mount-component.js';
const root=document.querySelector('[data-pes-cinematic="ATZ-SCR-007"]');
const compact=matchMedia('(max-width:700px)');
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
let context, mounted=false, initializing=false, readyPromise, refreshFrame=0;
let geometryObserver, lastGeometry='';
const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
function unmount(){
 context?.revert();context=undefined;mounted=false;
 root?.classList.remove('pes-cinematic-animated');
}
function mount(){
 if(!root||initializing)return;
 initializing=true;
 try{
  unmount();
  const {gsap,ScrollTrigger}=window;
  if(reduce.matches||!gsap||!ScrollTrigger)return;
  gsap.registerPlugin(ScrollTrigger);
  const mobile=compact.matches;
  const grid=root.querySelector('[data-grid-sixth]');
  const tiles=[...grid.querySelectorAll('.grid__img')];
  const title=root.querySelector('.content__title');
  const services=root.nextElementSibling;
  if(tiles.length!==9||!title||!services?.classList.contains('art-atlas'))return;
  root.classList.add('pes-cinematic-animated');
  // Stable small viewport height: browser toolbar movement cannot shorten the pin.
  const distance=()=>Math.round(root.clientHeight*(mobile?1:1.5));
  context=gsap.context(()=>{
   // ENTRY: edge stagger and distinct directional movement before pinning.
   // Keep images visible at entry and keep scale/skew owned solely by PIN.
   // Original edge stagger order, but expanded across the preceding viewport.
   const entry=gsap.timeline({paused:true,defaults:{ease:'none'}});
   entry.fromTo(tiles,{opacity:.55,xPercent:i=>(i%3-1)*(mobile?7:10),yPercent:i=>(Math.floor(i/3)-1)*(mobile?7:10)},{opacity:1,xPercent:0,yPercent:0,duration:.64,stagger:{amount:.36,from:'edges',grid:[3,3]}},0);
   ScrollTrigger.create({id:'pes-cinematic-entry',animation:entry,trigger:root,start:'top bottom',end:'top top',scrub:true});
   // PIN: only scale/skew and independent title opacity; no tile alpha/position animation.
   const motion=gsap.timeline({paused:true,defaults:{ease:'none'}});
   const scale=mobile ? .72 : .70;
   motion.fromTo(tiles,{scale},{scale:1,duration:.62,stagger:{amount:.12,from:'edges',grid:[3,3]}},0)
    .fromTo(grid,{scale,skewY:mobile ? 3 : 5},{scale:1,skewY:0,duration:.74},0)
    .fromTo(title,{opacity:0},{opacity:1,duration:.18},.04);
   // Deliberate hold after completing the zoom. No black fade while pinned.
   motion.to({hold:0},{hold:1,duration:.26},.74);
   ScrollTrigger.create({id:'pes-cinematic-pin',animation:motion,trigger:root,start:'top top',end:()=>'+='+distance(),pin:root,scrub:true,anticipatePin:1});
   // EXIT: neutral black overlay, independent of tile/title properties.
   // The services section physically enters the viewport while the mosaic exits.
   const exit=gsap.fromTo(root,{'--pes-cinematic-black':0},{'--pes-cinematic-black':1,ease:'none',paused:true});
   ScrollTrigger.create({id:'pes-cinematic-exit',animation:exit,trigger:services,start:'top bottom',end:'top 15%',scrub:true});
  },root);
  mounted=true;
  ScrollTrigger.refresh();
 }catch(e){unmount();console.warn('PES cinematic static fallback',e);}
 finally{initializing=false;}
}
// Observe only upstream layout, never a pin-spacer or a GSAP-animated child.
function upstreamGeometry(){
 const nodes=[document.querySelector('.hero-film'),document.querySelector('.pes-specialty'),document.querySelector('.pes-featured-split')].filter(Boolean);
 return {nodes, signature:nodes.map(n=>[n.offsetWidth,n.offsetHeight,n.offsetTop].join(':')).join('|')};
}
function scheduleRefresh(force=false){
 if(!mounted)return;
 const signature=upstreamGeometry().signature;
 if(!force&&signature===lastGeometry)return;
 lastGeometry=signature;
 if(refreshFrame)return;
 refreshFrame=requestAnimationFrame(()=>{
  refreshFrame=0;
  if(mounted)window.ScrollTrigger?.refresh();
 });
}
function observeUpstream(){
 if(geometryObserver||!('ResizeObserver' in window))return;
 const {nodes,signature}=upstreamGeometry();
 lastGeometry=signature;
 geometryObserver=new ResizeObserver(()=>scheduleRefresh());
 nodes.forEach(n=>geometryObserver.observe(n));
}
async function ready(remount=false){
 // Wait on the actual native mount promises, not the load event or an arbitrary delay.
 if(!readyPromise)readyPromise=(async()=>{
   await nativeComponentsReady;
   if(document.fonts?.ready)await document.fonts.ready;
   // Flush layout and the native engines' first scheduled render.
   await frame();await frame();
 })();
 await readyPromise;
 if(remount||!mounted)mount();else scheduleRefresh(true);
 observeUpstream();
}
compact.addEventListener('change',()=>ready(true));
reduce.addEventListener('change',()=>ready(true));
window.addEventListener('pageshow',()=>ready());
window.addEventListener('load',()=>ready(),{once:true});
window.addEventListener('resize',()=>scheduleRefresh(true),{passive:true});
ready().catch(error=>{unmount();console.error('PES cinematic readiness failed',error);});

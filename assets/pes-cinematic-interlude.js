/* ATZ-SCR-007 — PES Cinematic Refinement V1.1.
 * Original reference and lifecycle preserved in vendor. This instance uses its own
 * GSAP context because entry, pin and exit have distinct scroll ranges.
 */
const root=document.querySelector('[data-pes-cinematic="ATZ-SCR-007"]');
const compact=matchMedia('(max-width:700px)');
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
let context, mounted=false, initializing=false;
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
   // ENTRY: alpha only. At least 55% visible from the first pixel of the section.
   // Original edge stagger order, but expanded across the preceding viewport.
   const entry=gsap.timeline({paused:true,defaults:{ease:'none'}});
   entry.fromTo(tiles,{opacity:.55},{opacity:1,duration:.52,stagger:{amount:.36,from:'edges',grid:[3,3]}},0);
   ScrollTrigger.create({id:'pes-cinematic-entry',animation:entry,trigger:root,start:'top bottom',end:'top top',scrub:true});
   // PIN: only scale/skew and independent title opacity; no tile alpha animation.
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
function ready(){if(!mounted)mount();else window.ScrollTrigger?.refresh();}
compact.addEventListener('change',mount);
reduce.addEventListener('change',mount);
window.addEventListener('pageshow',ready);
window.addEventListener('load',ready,{once:true});
if(document.readyState==='complete')ready();
else if(window.gsap&&window.ScrollTrigger)mount();
document.fonts?.ready.then(()=>{if(mounted)window.ScrollTrigger?.refresh();});

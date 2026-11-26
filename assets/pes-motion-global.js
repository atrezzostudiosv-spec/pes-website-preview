/* PES global editorial opt-in. Only coordination; vendor animation formulas stay intact. */
import {mountEditorialMotion} from './pes-editorial-motion.js';
import {mount as textReveal} from './vendor/pes-motion/motion/ATZ-MOT-001.js';
import {mount as groupStagger} from './vendor/pes-motion/typography/ATZ-MOT-013.js';
const media=matchMedia('(prefers-reduced-motion: reduce)');
const excluded='.hero-film,.ats2-scope,.ss03,[data-atz-id],form,fieldset,.review-note,.historical-listing,.job-columns,.role-index,.site-header,.menu-dialog';
const titleClean=h=>h.textContent.trim().length<=90 && [...h.children].every(e=>e.matches('br,strong,em,b,i,span')&&!e.querySelector('a,button,svg,img')) && !h.querySelector('a,button,svg,img');
const visible=(e)=>{const r=e.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight*.85;};
const active=new Set();
const regionTasks=new WeakMap();
function register(region,finish){active.add(finish);let tasks=regionTasks.get(region);if(!tasks)regionTasks.set(region,tasks=new Set());tasks.add(finish);}
function unregister(region,finish){active.delete(finish);regionTasks.get(region)?.delete(finish);}
const make=(tag,cls)=>{const el=document.createElement(tag);if(cls)el.className=cls;return el;};
function watch(el,run){
 let observer;
 const stop=()=>observer?.disconnect();
 observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){stop();run();}},{rootMargin:'0px 0px -15% 0px',threshold:0});
 (Array.isArray(el)?el:[el]).forEach(e=>observer.observe(e));return stop;
}
function revealHeading(h,region){
 const nodes=[...h.childNodes], source=make('span','pes-global-title-source'), overlay=make('span','pes-global-title-overlay');
 overlay.setAttribute('aria-hidden','true');
 const initialPosition=getComputedStyle(h).position, addedPosition=initialPosition==='static';
 const instances=[],targets=[];let closed=false,timer,mo,stop,delay;
 const finish=()=>{if(closed)return;closed=true;clearTimeout(timer);clearTimeout(delay);stop?.();mo?.disconnect();instances.reverse().forEach(i=>{try{i.destroy();}catch{}});overlay.remove();if(source.isConnected){h.prepend(...nodes);source.remove();}if(addedPosition)h.classList.remove('pes-global-title-active');h.dataset.pesMotionDone='true';unregister(region,finish);};
 function segment(value,parent){
  if(!value.trim()){parent.append(document.createTextNode(value));return;}
  const r=make('span','atz-motion-v1 pes-global-segment');r.dataset.atzId='ATZ-MOT-001';r.dataset.pesMotion='';
  const t=make('span');t.dataset.amText='';t.textContent=value;r.append(t);parent.append(r);targets.push(t);
 }
 function clone(n,p){if(n.nodeType===Node.TEXT_NODE){segment(n.textContent,p);return;}if(n.nodeType!==Node.ELEMENT_NODE)return;if(n.matches('br')){p.append(make('br'));return;}const c=n.cloneNode(false);c.removeAttribute('id');c.removeAttribute('aria-label');p.append(c);[...n.childNodes].forEach(x=>clone(x,c));}
 try{
  nodes.forEach(n=>clone(n,overlay));
  if(!targets.length)return;
  register(region,finish);
  const play=()=>{if(closed||media.matches){finish();return;}try{
   if(addedPosition)h.classList.add('pes-global-title-active');
   source.append(...nodes);h.append(source,overlay);
   targets.forEach(t=>instances.push(textReveal(t.parentElement)));
   const done=()=>{if(targets.every(t=>t.classList.contains('am-inview'))){mo?.disconnect();clearTimeout(timer);timer=setTimeout(finish,1200+Math.max(...targets.map(t=>t.querySelectorAll('.am-char').length))*5+80);}};
   mo=new MutationObserver(done);targets.forEach(t=>mo.observe(t,{attributes:true,attributeFilter:['class']}));done();
   // Fail open on fast scroll, interrupted transitions or unavailable observer.
   // Watchdog is armed when the heading enters the viewport.
  }catch(e){finish();console.warn('PES heading fallback',e);}};
  play();
  // The original observer controls entry; watchdog starts only in view.
  stop=watch(h,()=>{if(!timer)timer=setTimeout(finish,2000);});
 }catch(e){finish();}
}
function animateGroup(units,region){
 if(!units.length)return;
 let root,instance,animations=[],stop,timer,closed=false;
 const finish=()=>{if(closed)return;closed=true;stop?.();clearTimeout(timer);animations.forEach(a=>a.cancel());try{instance?.destroy();}catch{}root?.remove();units.forEach(e=>e.dataset.pesMotionDone='true');unregister(region,finish);};
 try{
  // Original MOT-013 creates the exact WAAPI keyframes, easing and stagger on a
  // temporary group. Retarget the resulting KeyframeEffects to the original DOM
  // nodes (no wrapping, no grid/flex changes). Native observer coordinates entry.
  root=make('div','atz-ty pes-motion-staging');root.dataset.atzId='ATZ-MOT-013';root.dataset.pesMotion='';root.setAttribute('aria-hidden','true');
  const group=make('div');group.dataset.group='';const proxies=units.map(()=>make('span'));group.append(...proxies);root.append(group);document.body.append(root);
  instance=groupStagger(root);
  animations=proxies.map(p=>p.getAnimations()[0]);
  if(animations.some(a=>!a?.effect||!('target' in a.effect)))throw Error('Animation targeting unsupported');
  animations.forEach((a,i)=>{a.effect.target=units[i];});
  root.remove();
  register(region,finish);
  const play=()=>{if(media.matches){finish();return;}animations.forEach(a=>a.play());timer=setTimeout(finish,700+120*(units.length-1)+100);};
  stop=watch(units,play);
 }catch(e){finish();console.warn('PES group fallback',e);}
}
function eligible(e,region){return e.closest('[data-pes-editorial]')===region&&!e.closest(excluded)&&!e.closest('[data-pes-motion-off]')&&e.getClientRects().length>0;}
function mountRegion(region){
 if(region.dataset.pesEditorialReady||region.closest(excluded)||region.hasAttribute('data-pes-motion-off'))return;
 region.dataset.pesEditorialReady='true';
 const headings=[...region.querySelectorAll('h1,h2')].filter(e=>eligible(e,region));
 const protagonist=headings.find(titleClean);
 if(protagonist)revealHeading(protagonist,region);
 const candidates=[...region.querySelectorAll('h1,h2,h3,p,.eyebrow,.button,.text-link,.line-link,.project-back,.feature-action,.feature-scope,.tile-link,.phone,figcaption')].filter(e=>e!==protagonist&&eligible(e,region)&&e.textContent.trim()&&!e.querySelector('input,select,textarea,button'));
 const units=candidates.filter(e=>!candidates.some(p=>p!==e&&p.contains(e))&&!e.getAnimations().some(a=>a.playState==='running'));
 // Group only nearby siblings / text blocks, max three; no long cascading delays.
 let batch=[];
 const flush=()=>{if(batch.length)animateGroup(batch,region);batch=[];};
 for(const el of units){const last=batch.at(-1);if(last&&(batch.length>=3||last.parentElement!==el.parentElement||Math.abs(el.getBoundingClientRect().top-last.getBoundingClientRect().bottom)>140))flush();batch.push(el);}flush();
}
function stopAll(){[...active].forEach(f=>f());}
function start(){
 if(media.matches||!('IntersectionObserver' in window)||!Element.prototype.animate)return;
 const special=document.querySelector('.pes-specialty');if(special)mountEditorialMotion(special);
 document.querySelectorAll('[data-pes-editorial]').forEach(mountRegion);
}
document.addEventListener('focusin',e=>{const region=e.target.closest('[data-pes-editorial]');if(region)[...(regionTasks.get(region)||[])].forEach(f=>f());});
media.addEventListener('change',e=>{if(e.matches)stopAll();});
window.addEventListener('pagehide',stopAll);
if(document.fonts?.ready)document.fonts.ready.then(start).catch(start);else start();

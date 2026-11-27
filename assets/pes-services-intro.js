/* Services intro: PES V1 sequence, original MOT-001 + MOT-013.
 * Measure the native glyph positions instead of allowing split characters to reflow.
 * Original animation timing, easing, transforms and vendor files remain unchanged.
 */
import {mount as reveal} from './vendor/pes-motion/motion/ATZ-MOT-001.js';
import {mount as stagger} from './vendor/pes-motion/typography/ATZ-MOT-013.js';

export function mountServicesIntro(region){
 const media=matchMedia('(prefers-reduced-motion: reduce)');
 if(!region||media.matches||!('IntersectionObserver' in window)||!Element.prototype.animate||region.dataset.pesServicesMotion)return;
 const heading=region.querySelector('h2'),lines=[...heading.querySelectorAll('.pes-services-title-line')];
 const label=region.querySelector('.eyebrow'),rule=region.querySelector('.pes-services-intro-rule'),copy=region.querySelector(':scope > p');
 if(lines.length!==2||!label||!rule||!copy)return;
 const groups=[label,rule,copy],instances=[],timers=[];
 let observer,overlay,done=false,measuredLayout;
 const signature=()=>[heading.clientWidth,...lines.map(l=>{const c=getComputedStyle(l);return [l.clientWidth,l.clientHeight,c.fontSize,c.fontWeight,c.letterSpacing].join(':');})].join('|');
 const onResize=()=>{if(measuredLayout&&signature()!==measuredLayout)finish();};
 const make=(tag,cls)=>{const e=document.createElement(tag);if(cls)e.className=cls;return e;};
 const later=(ms,fn)=>timers.push(setTimeout(()=>{if(!done)try{fn();}catch(error){finish();console.warn('PES services intro fallback',error);}},ms));
 function finish(){
  if(done)return;done=true;observer?.disconnect();timers.forEach(clearTimeout);
  instances.reverse().forEach(i=>{try{i.destroy();}catch{}});
  overlay?.remove();groups.forEach(e=>{delete e.dataset.pesServicesPending;e.dataset.pesMotionDone='true';});
  heading.dataset.pesMotionDone='true';region.dataset.pesServicesMotion='complete';
  window.removeEventListener('resize',onResize);window.removeEventListener('pagehide',finish);media.removeEventListener('change',onMedia);
 }
 const onMedia=()=>{if(media.matches)finish();};
 // Retarget original MOT-013 keyframes onto the unwrapped static DOM elements.
 function enterGroup(element){
  const staging=make('div','atz-ty pes-motion-staging');staging.dataset.atzId='ATZ-MOT-013';staging.dataset.pesMotion='';
  staging.setAttribute('aria-hidden','true');const group=make('div');group.dataset.group='';const proxy=make('span');group.append(proxy);staging.append(group);document.body.append(staging);
  try{
   const instance=stagger(staging);instances.push(instance);
   const animation=proxy.getAnimations()[0];if(!animation?.effect||!('target' in animation.effect))throw Error('Missing group animation');
   animation.effect.target=element;animation.play();delete element.dataset.pesServicesPending;
  }finally{staging.remove();}
 }
 function revealTitle(){
  measuredLayout=signature();
  const base=heading.getBoundingClientRect();
  overlay=make('span','pes-services-title-overlay');overlay.setAttribute('aria-hidden','true');
  const specs=lines.map(line=>{
   const rect=line.getBoundingClientRect(),style=getComputedStyle(line),text=line.firstChild;
   const offsets=[];let offset=0;
   for(const char of [...text.textContent]){
    const range=document.createRange();range.setStart(text,offset);offset+=char.length;range.setEnd(text,offset);
    if(!/\s/u.test(char))offsets.push(range.getBoundingClientRect().left-rect.left);
   }
   const root=make('span','atz-motion-v1 pes-services-title-segment');root.dataset.atzId='ATZ-MOT-001';root.dataset.pesMotion='';
   Object.assign(root.style,{left:(rect.left-base.left)+'px',top:(rect.top-base.top)+'px',width:rect.width+'px',height:rect.height+'px',fontWeight:style.fontWeight,lineHeight:style.lineHeight});
   const target=make('span');target.dataset.amText='';target.textContent=text.textContent;root.append(target);overlay.append(root);
   return {root,target,offsets};
  });
  heading.append(overlay);
  let duration=0;
  specs.forEach(({root,target,offsets})=>{
   instances.push(reveal(root));
   const chars=[...target.querySelectorAll('.am-char')];if(chars.length!==offsets.length)throw Error('Character geometry mismatch');
   chars.forEach((char,i)=>{char.style.left=offsets[i]+'px';});
   duration=Math.max(duration,1200+chars.length*5+80);
  });
  // Finish only after the native entry class has fired; fail open if interrupted.
  const started=()=>specs.every(s=>s.target.classList.contains('am-inview'));
  const watcher=new MutationObserver(()=>{if(started()){watcher.disconnect();later(duration,finish);}});
  specs.forEach(s=>watcher.observe(s.target,{attributes:true,attributeFilter:['class']}));
  instances.push({destroy:()=>watcher.disconnect()});
  if(started()){watcher.disconnect();later(duration,finish);}
  later(2400,finish);
 }
 try{
  region.dataset.pesServicesMotion='waiting';groups.forEach(e=>e.dataset.pesServicesPending='');
  observer=new IntersectionObserver(entries=>{
   if(!entries.some(e=>e.isIntersecting))return;
   observer.disconnect();region.dataset.pesServicesMotion='playing';
   try{enterGroup(label);later(120,revealTitle);later(320,()=>enterGroup(rule));later(440,()=>enterGroup(copy));}
   catch(error){finish();console.warn('PES services intro fallback',error);}
  },{rootMargin:'0px 0px -15% 0px',threshold:0});
  observer.observe(label);
  window.addEventListener('resize',onResize,{passive:true});window.addEventListener('pagehide',finish);media.addEventListener('change',onMedia);
 }catch(error){finish();console.warn('PES services intro fallback',error);}
 return {destroy:finish};
}

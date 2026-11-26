/* PES Motion V1 — coordination only. Original motors are unmodified. */
import {mount as reveal} from './vendor/pes-motion/motion/ATZ-MOT-001.js';
import {mount as stagger} from './vendor/pes-motion/typography/ATZ-MOT-013.js';

export function mountEditorialMotion(section) {
  const media=matchMedia('(prefers-reduced-motion: reduce)');
  if(!section || media.matches || !('IntersectionObserver' in window) || !Element.prototype.animate || section.dataset.pesMotionState) return;
  const label=section.querySelector('.pes-specialty-label');
  const heading=section.querySelector('h2');
  const copy=section.querySelector('.pes-specialty-copy');
  const bold=heading?.querySelector('strong');
  const br=heading?.querySelector('br');
  if(!label || !heading || !copy || !bold || !br) return;
  const instances=[],timers=[],originalNodes=[...heading.childNodes];
  let observer, titleObserver, finished=false, overlay, source, ruleRoot;
  const oldLabel=heading.getAttribute('aria-label');
  const make=(tag,cls)=>{const e=document.createElement(tag);e.className=cls;return e;};
  const root=(tag,id,cls)=>{const e=make(tag,cls);e.dataset.atzId=id;e.dataset.pesMotion='';return e;};
  const group=(tag,children,where)=>{
    const r=root(tag,'ATZ-MOT-013','atz-ty pes-motion-group');
    const g=make(tag,'pes-motion-units');g.dataset.group='';
    where(r);g.append(...children);r.append(g);r.dataset.pending='';return r;
  };
  const showTitle=()=>{
    titleObserver?.disconnect();
    if(overlay){overlay.remove();overlay=null;}
    heading.classList.remove('pes-motion-title-active');
    if(source){heading.prepend(...originalNodes);source.remove();source=null;}
    if(oldLabel===null)heading.removeAttribute('aria-label');else heading.setAttribute('aria-label',oldLabel);
  };
  const finish=()=>{
    if(finished)return;finished=true;
    observer?.disconnect();titleObserver?.disconnect();timers.forEach(clearTimeout);
    instances.splice(0).reverse().forEach(x=>{try{x.destroy();}catch{}});
    showTitle();
    section.querySelectorAll('[data-pending]').forEach(e=>delete e.dataset.pending);
    section.removeEventListener('focusin',finish);media.removeEventListener('change',onMedia);
    section.dataset.pesMotionState='complete';
  };
  const onMedia=()=>{if(media.matches)finish();};
  const later=(ms,fn)=>timers.push(setTimeout(()=>{if(!finished)try{fn();}catch(e){finish();console.warn('PES motion fallback',e);}},ms));
  const playGroup=r=>{instances.push(stagger(r));delete r.dataset.pending;};
  try{
    const labelRoot=group('div',[label],r=>label.before(r));
    const copyRoot=group('div',[...copy.children],r=>copy.append(r));
    // Keep the approved H2 as the layout and accessibility source.
    source=make('span','pes-motion-source');source.append(...originalNodes);heading.append(source);
    heading.setAttribute('aria-label',source.textContent.replace(/behindthe/,'behind the').trim());
    overlay=make('span','pes-motion-overlay');overlay.setAttribute('aria-hidden','true');overlay.dataset.pending='';
    const segment=(value,heavy)=>{
      const r=root('span','ATZ-MOT-001','atz-motion-v1 pes-motion-segment');
      const t=make(heavy?'strong':'span','pes-motion-text');t.dataset.amText='';t.textContent=value;r.append(t);return r;
    };
    const lightText=originalNodes.slice(0,originalNodes.indexOf(br)).map(n=>n.textContent).join('');
    const lines=[segment(lightText,false),segment(bold.textContent,true)];
    overlay.append(lines[0],document.createElement('br'),lines[1]);heading.append(overlay);
    const rule=make('span','pes-motion-rule');
    ruleRoot=group('span',[rule],r=>{r.classList.add('pes-motion-rule-group');heading.append(r);});
    heading.classList.add('pes-motion-title-active','pes-motion-rule-real');
    section.dataset.pesMotionState='waiting';
    section.addEventListener('focusin',finish);media.addEventListener('change',onMedia);
    const playTitle=()=>{
      const targets=lines.map(r=>r.querySelector('[data-am-text]'));
      lines.forEach(r=>instances.push(reveal(r)));
      delete overlay.dataset.pending;
      const complete=()=>{
        if(targets.every(t=>t.classList.contains('am-inview'))){
          titleObserver.disconnect();
          // Original 1200ms transition + original 5ms per-character delay.
          later(1200+Math.max(...targets.map(t=>t.querySelectorAll('.am-char').length))*5+80,showTitle);
        }
      };
      titleObserver=new MutationObserver(complete);
      targets.forEach(t=>titleObserver.observe(t,{attributes:true,attributeFilter:['class']}));
      complete();
    };
    observer=new IntersectionObserver(entries=>{
      if(!entries.some(e=>e.isIntersecting))return;
      observer.disconnect();section.dataset.pesMotionState='playing';
      try{
        playGroup(labelRoot);
        later(120,playTitle);
        later(320,()=>playGroup(ruleRoot));
        later(440,()=>playGroup(copyRoot));
      }catch(e){finish();console.warn('PES motion fallback',e);}
    },{rootMargin:'0px 0px -15% 0px',threshold:0});
    observer.observe(label);
  }catch(e){finish();console.warn('PES motion fallback',e);}
  return {destroy:finish};
}

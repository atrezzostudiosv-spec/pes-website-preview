import {mount} from './ATZ-MOT-003.js';
const review=new URLSearchParams(location.search).get('review')==='1';
if(review){
 document.body.classList.add('pv4-review');
 document.querySelectorAll('[data-review-only]').forEach(e=>e.hidden=false);
 document.querySelectorAll('[data-review-link]').forEach(e=>e.hidden=true);
 const targets=new Set(['portfolio','hillside','laurel-way','st-cloud']);
 document.querySelectorAll('main a[href]').forEach(a=>{
  const url=new URL(a.getAttribute('href'),location.href);
  if(url.origin===location.origin&&targets.has(url.pathname.split('/').filter(Boolean).at(-1))&&!a.matches('[data-review-only]')&&a.getAttribute('href')!=='?'){url.searchParams.set('review','1');a.href=url.href;}
 });
}
const figure=document.querySelector('.pv4-gallery-item:first-child');
if(figure&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
 const img=figure.querySelector('img');
 if(img){
  const frame=document.createElement('div');frame.className='pv4-parallax-frame';frame.dataset.amParallax='';
  img.replaceWith(frame);frame.append(img);figure.dataset.atzId='ATZ-MOT-003';
  try{const instance=mount(figure);window.addEventListener('pagehide',()=>instance.destroy(),{once:true});}
  catch(e){frame.replaceWith(img);delete figure.dataset.atzId;}
 }
}

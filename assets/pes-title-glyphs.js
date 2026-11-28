/* PES adapter: align animated glyphs with the native, kerned text.
 * ATZ-MOT-001 retains its original opacity, transform, easing and timing.
 * The source stays in normal flow; relative offsets only affect the visual clone.
 */
function glyphRanges(root){
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 const result=[];let node;
 while((node=walker.nextNode())){
  let offset=0;
  for(const char of node.data){
   const start=offset;offset+=char.length;
   if(/\s/u.test(char))continue;
   const range=document.createRange();range.setStart(node,start);range.setEnd(node,offset);
   result.push({char,rect:range.getBoundingClientRect()});
  }
 }
 return result;
}
export function alignTitleGlyphs(source,overlay){
 const native=glyphRanges(source),chars=[...overlay.querySelectorAll('.am-char')];
 if(!chars.length||native.length!==chars.length||chars.some((c,i)=>c.textContent!==native[i].char))throw Error('PES glyph mapping mismatch');
 // All measurements happen synchronously before the first animation paint.
 // Disable transitions only while measuring; restore the original initial state.
 chars.forEach(c=>{c.style.position='relative';c.style.left='0px';c.style.top='0px';c.style.setProperty('transition','none','important');c.style.setProperty('transform','none','important');});
 const offsets=chars.map((c,i)=>{
  const visual=glyphRanges(c)[0]?.rect,real=native[i].rect;
  if(!visual||!Number.isFinite(real.left+real.top+visual.left+visual.top))throw Error('PES glyph geometry unavailable');
  return [real.left-visual.left,real.top-visual.top];
 });
 chars.forEach((c,i)=>{c.style.left=offsets[i][0]+'px';c.style.top=offsets[i][1]+'px';c.style.removeProperty('transform');});
 // Flush the original starting transform with transitions still disabled.
 overlay.getBoundingClientRect();
 chars.forEach(c=>c.style.removeProperty('transition'));
 overlay.dataset.pesGlyphAligned='true';
}
export function titleLayoutSignature(h){
 const s=getComputedStyle(h),r=h.getBoundingClientRect();
 return [r.width,r.height,s.fontFamily,s.fontSize,s.fontWeight,s.letterSpacing,s.lineHeight,innerWidth].join('|');
}

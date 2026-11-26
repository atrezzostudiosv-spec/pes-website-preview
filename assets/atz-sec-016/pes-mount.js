// PES lifecycle adapter. ATZ-SEC-016 engine.original.js remains literal and unmodified.
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
initHeader();
if(document.querySelector('[data-hero-video]'))initFilm();
const menu=document.getElementById('menu-dialog');
document.querySelector('[data-open="menu-dialog"]').addEventListener('click',()=>openDialog('menu-dialog'));
menu.querySelector('[data-close]').addEventListener('click',()=>closeDialog(menu));
menu.addEventListener('close',()=>{if(!document.querySelector('dialog[open]'))document.body.style.overflow='';});
menu.addEventListener('click',e=>{if(e.target.closest('a'))closeDialog(menu);});

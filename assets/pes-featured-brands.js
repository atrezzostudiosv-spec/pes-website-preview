/* Use the unmodified ATREZZO library motion: 700ms, 120ms stagger, 20px rise. */
import {mount} from './vendor/pes-motion/typography/ATZ-MOT-013.js';
const section=document.getElementById('pes-featured-brands');
if(section && Element.prototype.animate){
 try{mount(section);}catch(error){console.warn('PES featured brands: static fallback',error);}
}

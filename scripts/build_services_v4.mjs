import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
function renderServices(files){
 const E=v=>String(v??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
 const blocks=s=>s.trim().split(/\n\s*\n/).map(b=>{const [h,...p]=b.trim().split("\n");return [h.trim(),p.map(t=>t.trim()).join(" ")]});
 const data=JSON.parse(files["data/editorial-v3.json"]).pages;
 const get=r=>data.find(p=>p.route===`/${r}/`);
 const config=[
 ["lighting-systems","System lighting","upgrade.","Electrical distribution and control equipment","034","037","Electrical installation detail","technical"],
 ["automated-window-coverings","Automated window","coverings.","Automated window coverings in a residence","039",null,null,"shade"],
 ["lighting-design","Lighting design","and installation.","Integrated ceiling and architectural lighting in a residence with an open terrace","010",null,null,"light"],
 ["power-quality-and-energy-management","Power quality","and energy management.","Electrical distribution equipment","035",null,null,"technical"],
 ["ev-charging","EV charger","installations.","Electric vehicle connected to charging equipment","048","022","Wall-mounted electric vehicle charging equipment","ev"]
 ];
 const wrap=(old,html,p,pre)=>{const m=old.match(/<main\b[^>]*>/);if(!m)throw Error("Missing main");let out=old.replace(/<main\b[^>]*>[\s\S]*?<\/main>/,()=>m[0]+"\n"+html+"\n</main>").replace(/<title>[\s\S]*?<\/title>/,()=>`<title>${E(p.seo_title)}</title>`).replace(/<meta name="description"[^>]*>/,()=>`<meta name="description" content="${E(p.seo_description)}">`).replace(/<body class="pes-site(?: sv4-page)?">/,'<body class="pes-site sv4-page">');out=out.replace(/\s*<link rel="stylesheet" href="(?:\.\.\/)+assets\/pes-services-v4\.css[^"]*">\s*/g,"\n");return out.replace("</head>",`  <link rel="stylesheet" href="${pre}assets/pes-services-v4.css?v=1">\n</head>`);};
 const image=(id,alt,pre,hero=false)=>`<img src="${pre}assets/media/PES-${id}.jpg" alt="${E(alt)}" ${hero?'fetchpriority="high"':'loading="lazy"'} decoding="async">`;
 const extractScene=(old,id)=>{const start=old.indexOf(`<div aria-label=`);const pos=old.indexOf(`data-atz-id="${id}"`,start);if(start<0||pos<0)throw Error("Missing ATZ scene "+id);const end=old.indexOf("\n</div>",pos);if(end<0)throw Error("Missing end "+id);return old.slice(start,end+7);};
 const close=(pre,h="Let’s discuss your project.",p="Share the electrical requirements of your property with our team.")=>`<section class="ui sv4-close" data-pes-editorial><div class="wrap sv4-close-grid"><div><p class="eyebrow">PES / LET’S CONNECT</p><h2>${E(h)}</h2><span class="sv4-rule"></span><p>${E(p)}</p></div><div class="sv4-actions"><a class="button" href="${pre}contact/">Discuss Your Project <span aria-hidden="true">↗</span></a><a href="tel:+12135873257">213-587-3257</a></div></div></section>`;
 const output={};
 const hub="capabilities/index.html", hp=get("capabilities"), hb=blocks(hp.editorial_approved);
 if(hb.length!==6)throw Error("Unexpected master hub blocks");
 const hubItems=hb.slice(1).map(([title,body],i)=>{const c=config[i];return `<li><a href="${c[0]}/"><span class="sv4-no">0${i+1}</span><span><strong>${E(title)}</strong><small>${E(body)}</small></span><span class="sv4-arrow" aria-hidden="true">↗</span></a></li>`;}).join("");
 const hubScene=extractScene(files[hub],"ATZ-SEC-008");
 const hubMarkup=`<section class="ui sv4-hero sv4-hero--hub" data-pes-editorial>${image("009","Illuminated terrace overlooking Los Angeles at night","../",true)}<div class="wrap sv4-hero-copy"><p class="eyebrow">PES / OUR SERVICES</p><h1>Electrical<br><strong>services.</strong></h1><span class="sv4-rule"></span><p>${E(hb[0][1])}</p><a class="sv4-link" href="#service-index">Explore our services ↓</a></div></section>
<section class="ui sv4-index" id="service-index" data-pes-editorial><div class="wrap"><p class="eyebrow">PES / FIVE SERVICE AREAS</p><h2>Explore our<br><strong>capabilities.</strong></h2><span class="sv4-rule"></span><ol>${hubItems}</ol></div></section>
${hubScene}
<section class="ui sv4-duo"><div class="wrap">${[3,4].map(i=>`<article data-pes-editorial><a class="sv4-media" href="${config[i][0]}/">${image(config[i][4],config[i][3],"../")}</a><p class="eyebrow">0${i+1} / PES</p><h2>${E(hb[i+1][0])}</h2><p>${E(hb[i+1][1])}</p><a class="sv4-link" href="${config[i][0]}/">Explore service ↗</a></article>`).join("")}</div></section>
${close("../")}`;
 output[hub]=wrap(files[hub],hubMarkup,hp,"../");
 config.forEach((c,i)=>{
 const [slug,line1,line2,alt,hero,detail,detailAlt,kind]=c, r="capabilities/"+slug, path=r+"/index.html", p=get(r), b=blocks(p.editorial_approved), pre="../../";
 const power=i===3, light=i===2, intro=b[0][1], body=power?b.slice(1,-1):b.slice(1);
 if(!body.length)throw Error("Missing master copy");
 const heroMarkup=`<section class="ui sv4-hero sv4-hero--${kind}" data-pes-editorial>${image(hero,alt,pre,true)}<div class="wrap sv4-hero-copy"><a class="sv4-back" href="../">← All services</a><p class="eyebrow">PES / ${power?"EDUCATIONAL OVERVIEW":"ELECTRICAL SERVICES"}</p><h1>${E(line1)}<br><strong>${E(line2)}</strong></h1><span class="sv4-rule"></span><p>${E(intro)}</p><a class="sv4-link" href="#service-story">Explore ${power?"the essentials":"the service"} ↓</a></div></section>`;
 const sections=body.map(([h,t],j)=>{
 const row=`<section ${j===0?'id="service-story" ':''}class="ui sv4-chapter${j%2===1?' sv4-chapter--dark':''}" data-pes-editorial><div class="wrap"><div class="sv4-chapter-index"><p class="eyebrow">${String(j+1).padStart(2,"0")} / PES</p><span class="sv4-rule"></span></div><div><h2>${E(h)}</h2><p>${E(t)}</p>${light&&j===body.length-1?`<a class="sv4-link" href="${pre}portfolio/">Explore projects ↗</a>`:""}</div></div></section>`;
 return row+(j===0&&detail?`<figure class="ui sv4-detail">${image(detail,detailAlt,pre)}<figcaption class="wrap">PES / ${E(detailAlt)}</figcaption></figure>`:"")+(j===0&&light?extractScene(files[path],"ATZ-SEC-007"):"");
 }).join("\n");
 const ref=power?`<section class="ui sv4-reference"><div class="wrap">Technical reference: <a href="https://technav.ieee.org/topic/power-quality/">IEEE Technology Navigator, Power Quality</a>.</div></section>`:"";
 const footer=power?close(pre,...b[b.length-1]):close(pre);
 output[path]=wrap(files[path],[heroMarkup,sections,ref,footer].join("\n"),p,pre);
 });
 return output;
}
const paths=["capabilities/index.html","capabilities/lighting-systems/index.html","capabilities/automated-window-coverings/index.html","capabilities/lighting-design/index.html","capabilities/power-quality-and-energy-management/index.html","capabilities/ev-charging/index.html","data/editorial-v3.json"];
const files=Object.fromEntries(paths.map(p=>[p,fs.readFileSync(path.join(root,p),'utf8')]));
for(const [p,c] of Object.entries(renderServices(files)))fs.writeFileSync(path.join(root,p),c);

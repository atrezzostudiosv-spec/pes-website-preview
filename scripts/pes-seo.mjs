import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const config=JSON.parse(fs.readFileSync(path.join(ROOT,'data/seo-v1.json'),'utf8'));
function applySeo(html,route,config){
 const p=config.pages.find(x=>x.route===route);if(!p)throw Error("SEO route missing: "+route);
 const esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
 const url=config.preview_base+route,im=config.preview_base+p.image.path,org=config.preview_base+"#organization",site=config.preview_base+"#website",webpage=url+"#webpage";
 const schema=[{"@type":"Organization","@id":org,name:config.organization,url:config.preview_base,logo:{"@type":"ImageObject",url:config.preview_base+"assets/brand/pes-logo-flat.svg"},telephone:config.phone,areaServed:{"@type":"City",name:"Los Angeles"},sameAs:["https://www.instagram.com/pes.la/"]},{"@type":"WebSite","@id":site,url:config.preview_base,name:"Premium Energy Solutions",publisher:{"@id":org},inLanguage:"en-US"},{"@type":p.type,"@id":webpage,url,name:p.title,description:p.description,isPartOf:{"@id":site},about:{"@id":org},inLanguage:"en-US",primaryImageOfPage:{"@type":"ImageObject",url:im,width:p.image.width,height:p.image.height}}];
 if(route){const chain=[config.pages[0],...(p.parent?[config.pages.find(x=>x.route===p.parent)]:[]),p];schema.push({"@type":"BreadcrumbList","@id":url+"#breadcrumb",itemListElement:chain.map((x,i)=>({"@type":"ListItem",position:i+1,name:x.label,item:config.preview_base+x.route}))});schema[2].breadcrumb={"@id":url+"#breadcrumb"};}
 if(p.service){schema.push({"@type":"Service","@id":url+"#service",name:p.service,serviceType:p.service,description:p.description,url,provider:{"@id":org},areaServed:{"@type":"City",name:"Los Angeles"}});schema[2].mainEntity={"@id":url+"#service"};}
 const tag=(kind,key,value)=>`  <meta ${kind}="${key}" content="${esc(value)}">`;
 const block=["  <!-- PES SEO V1 START -->",tag("name","description",p.description),`  <link rel="canonical" href="${esc(url)}">`,...Object.entries({"og:type":"website","og:site_name":"Premium Energy Solutions","og:locale":"en_US","og:title":p.title,"og:description":p.description,"og:url":url,"og:image":im,"og:image:secure_url":im,"og:image:type":p.image.path.endsWith(".png")?"image/png":"image/jpeg","og:image:width":p.image.width,"og:image:height":p.image.height,"og:image:alt":p.image.alt}).map(([k,v])=>tag("property",k,v)),...Object.entries({"twitter:card":"summary_large_image","twitter:title":p.title,"twitter:description":p.description,"twitter:image":im,"twitter:image:alt":p.image.alt}).map(([k,v])=>tag("name",k,v)),`  <script type="application/ld+json">${JSON.stringify({"@context":"https://schema.org","@graph":schema}).replace(/</g,"\\u003c")}</script>`,"  <!-- PES SEO V1 END -->"].join("\n");
 const head=html.match(/<head>[\s\S]*?<\/head>/)?.[0];if(!head)throw Error("Missing head "+route);
 let h=head.replace(/\n?[ \t]*<!-- PES SEO V1 START -->[\s\S]*?<!-- PES SEO V1 END -->/g,"").replace(/[ \t]*<meta name="description"[^>]*>\n?/g,"").replace(/<title>[\s\S]*?<\/title>/,()=>`<title>${esc(p.title)}</title>\n${block}`);
 // Keep one clean newline between tags, even if an old description was adjacent to the favicon.
 h=h.replace(/>(?=<link |<meta |<script )/g,">\n  ");
 return html.replace(head,()=>h);
}
export function withSeo(html,file){return applySeo(html,file.replace(/index\.html$/,''),config);}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){for(const p of config.pages){const f=path.join(ROOT,p.route,'index.html');const current=fs.readFileSync(f,'utf8'),updated=applySeo(current,p.route,config);if(process.argv.includes('--check')){if(current!==updated)throw Error('SEO drift: '+p.route);}else fs.writeFileSync(f,updated);}console.log('SEO verified / '+config.pages.length+' pages');}

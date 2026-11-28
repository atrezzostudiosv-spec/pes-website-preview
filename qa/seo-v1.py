from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json, struct
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/seo-v1.json').read_text())
class Head(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True); self.inhead=False; self.intitle=False; self.injson=False; self.title=''; self.meta={}; self.links={}; self.schemas=[]; self.buf=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='head':self.inhead=True
  if not self.inhead:return
  if tag=='title':self.intitle=True
  if tag=='meta':
   k=a.get('property') or a.get('name')
   if k:self.meta.setdefault(k,[]).append(a.get('content',''))
  if tag=='link':self.links.setdefault(a.get('rel'),[]).append(a.get('href',''))
  if tag=='script' and a.get('type')=='application/ld+json':self.injson=True;self.buf=''
 def handle_endtag(self,tag):
  if tag=='head':self.inhead=False
  if tag=='title':self.intitle=False
  if tag=='script' and self.injson:self.schemas.append(json.loads(self.buf));self.injson=False
 def handle_data(self,d):
  if self.intitle:self.title+=d
  if self.injson:self.buf+=d
def image_size(p):
 b=p.read_bytes()
 if b[:8]==b'\x89PNG\r\n\x1a\n':return struct.unpack('>II',b[16:24])
 assert b[:2]==b'\xff\xd8',p
 i=2
 while i<len(b):
  if b[i]!=255:raise ValueError(p)
  while b[i]==255:i+=1
  marker=b[i];i+=1
  if marker in (0xd8,0xd9):continue
  n=int.from_bytes(b[i:i+2],'big')
  if marker in (0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf):
   h,w=struct.unpack('>HH',b[i+3:i+7]);return w,h
  i+=n
 raise ValueError(p)
titles=set();descs=set();urls=set()
for p in data['pages']:
 f=ROOT/p['route']/'index.html';h=Head();h.feed(f.read_text())
 url=data['preview_base']+p['route'];img=data['preview_base']+p['image']['path']
 assert h.title==p['title'] and h.title not in titles,f
 assert h.meta['description']==[p['description']] and p['description'] not in descs,f
 assert h.links['canonical']==[url] and url not in urls,f
 for k,v in {'og:title':p['title'],'og:description':p['description'],'og:url':url,'og:image':img,'og:image:width':str(p['image']['width']),'og:image:height':str(p['image']['height']),'twitter:card':'summary_large_image','twitter:image':img}.items():
  assert h.meta[k]==[v],(f,k)
 assert 'noindex' in h.meta['robots'][0],f
 assert image_size(ROOT/p['image']['path'])==(p['image']['width'],p['image']['height']),(f,p['image'])
 assert len(h.schemas)==1 and h.schemas[0]['@context']=='https://schema.org',f
 graph=h.schemas[0]['@graph'];assert not any(x['@type']=='JobPosting' for x in graph),f
 assert len([x for x in graph if x['@type']=='Service'])==int('service' in p),f
 assert len(h.links.get('icon',[]))==2,f
 titles.add(h.title);descs.add(p['description']);urls.add(url)
assert len(titles)==18
print('PASS: 18 titles, descriptions, canonicals, sharing cards, images, JSON-LD and preview safeguards')

"""Build the PES V3 editorial review pages from public-facing structured data.

Home and Why Us are deliberately outside this builder. Private editorial worksheets
are generated only under .private-review and are never part of GitHub Pages.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITORIAL = {p["route"]: p for p in json.loads((ROOT / "data/editorial-v3.json").read_text())["pages"]}
PROJECTS = json.loads((ROOT / "data/projects-v3.json").read_text())["projects"]
E = html.escape


def path(route: str) -> Path:
    return ROOT / route.strip("/") / "index.html"


def prefix(route: str) -> str:
    return "../" * len([p for p in route.strip("/").split("/") if p])


def image(src: str, alt: str, route: str, *, priority: bool = False, small: str | None = None) -> str:
    pre = prefix(route)
    srcset = f' srcset="{pre}{E(small)} 800w, {pre}{E(src)} 1600w" sizes="(max-width: 800px) 100vw, 100vw"' if small else ""
    loading = ' fetchpriority="high"' if priority else ' loading="lazy"'
    return f'<img src="{pre}{E(src)}"{srcset} alt="{E(alt)}"{loading}>'


def shell(route: str, base: str | None = None) -> str:
    target = path(route)
    if target.exists():
        return target.read_text()
    assert base
    return path(base).read_text()


def write_page(route: str, content: str, *, title: str, description: str, base: str | None = None) -> None:
    current = shell(route, base)
    if base and base != route:
        # The new project pages have the same route depth as their source shell.
        assert len(prefix(base)) == len(prefix(route))
        current = current.replace('aria-current="page"', '')
    main = re.search(r'<main\b[^>]*>.*?</main>', current, re.S)
    if not main:
        raise ValueError(f"Missing main landmark: {route}")
    opening = re.match(r'<main\b[^>]*>', main.group()).group()
    current = current[:main.start()] + opening + "\n" + content + "\n</main>" + current[main.end():]
    current = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', current, count=1, flags=re.S)
    meta = f'<meta name="description" content="{E(description, quote=True)}">'
    if re.search(r'<meta name="description"[^>]*>', current):
        current = re.sub(r'<meta name="description"[^>]*>', meta, current, count=1)
    else:
        current = current.replace('</title>', '</title>' + meta, 1)
    css = f'<link rel="stylesheet" href="{prefix(route)}assets/pes-interiors-v3.css">'
    if 'pes-interiors-v3.css' not in current:
        current = current.replace('</head>', f'  {css}\n</head>', 1)
    target = path(route)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(current)


def split_copy(copy: str) -> list[tuple[str, str]]:
    blocks = []
    for raw in copy.strip().split("\n\n"):
        lines = raw.strip().splitlines()
        if not lines:
            continue
        blocks.append((lines[0].strip(), " ".join(x.strip() for x in lines[1:])))
    return blocks


def close(route: str, heading: str = "Let’s discuss your project.") -> str:
    pre = prefix(route)
    return f'''<section class="ui iv3-close" data-pes-editorial><div class="wrap iv3-close__inner">
      <p class="eyebrow">PES / LET’S CONNECT</p><h2>{E(heading)}</h2>
      <p>Share the electrical requirements of your property with our team.</p>
      <div class="iv3-actions"><a class="button" href="{pre}contact/">Discuss Your Project <span aria-hidden="true">↗</span></a><a class="iv3-phone" href="tel:+12135873257">213-587-3257</a></div>
    </div></section>'''


def text_section(index: int, heading: str, body: str, *, dark: bool = False) -> str:
    kind = ' iv3-text--dark' if dark else ''
    return f'''<section class="ui iv3-text{kind}" data-pes-editorial><div class="wrap iv3-text__grid">
      <p class="eyebrow">{index:02d} / PES</p><div><h2>{E(heading)}</h2><p>{E(body)}</p></div>
    </div></section>'''


SERVICE_MEDIA = {
    '/capabilities/lighting-systems/': ('assets/media/PES-034.jpg', 'Electrical distribution and control equipment', 'assets/media/PES-037.jpg', 'Electrical installation detail'),
    '/capabilities/automated-window-coverings/': ('assets/media/PES-039.jpg', 'Automated window coverings in a residence', None, None),
    '/capabilities/ev-charging/': ('assets/media/PES-048.jpg', 'Electric vehicle connected to charging equipment', 'assets/media/PES-022.jpg', 'Wall-mounted electric vehicle charging equipment'),
}


def service_page(route: str) -> None:
    data = EDITORIAL[route]
    blocks = split_copy(data['editorial_approved'])
    hero_src, hero_alt, detail_src, detail_alt = SERVICE_MEDIA[route]
    title, intro = blocks[0]
    parts = [f'''<section class="ui iv3-hero" data-pes-editorial>{image(hero_src, hero_alt, route, priority=True)}
      <div class="wrap iv3-hero__copy"><p class="eyebrow">PES / ELECTRICAL SERVICES</p><h1>{E(title)}</h1><p>{E(intro)}</p><a class="iv3-down" href="#service-story">Explore the service ↓</a></div></section>''']
    for i, (heading, body) in enumerate(blocks[1:], 1):
        if i == 2 and detail_src:
            parts.append(f'<section class="ui iv3-photo-band" data-pes-editorial>{image(detail_src, detail_alt, route)}<div class="wrap"><p class="eyebrow">PES / WORK IN FOCUS</p></div></section>')
        parts.append(text_section(i, heading, body, dark=i % 3 == 0).replace('class="ui iv3-text', 'id="service-story" class="ui iv3-text', 1) if i == 1 else text_section(i, heading, body, dark=i % 3 == 0))
    parts.append(close(route))
    write_page(route, '\n'.join(parts), title=data['seo_title'], description=data['seo_description'])


def power_quality() -> None:
    route = '/capabilities/power-quality-and-energy-management/'
    data = EDITORIAL[route]
    blocks = split_copy(data['editorial_approved'])
    parts = [f'''<section class="ui iv3-hero" data-pes-editorial>{image('assets/media/PES-035.jpg', 'Electrical distribution equipment', route, priority=True)}
      <div class="wrap iv3-hero__copy"><p class="eyebrow">PES / EDUCATIONAL OVERVIEW</p><h1>Power Quality<br>and Energy Management.</h1>
      <p>{E(blocks[0][1])}</p><a class="iv3-down" href="#understanding-power">Explore the essentials ↓</a></div></section>''']
    for i, (heading, body) in enumerate(blocks[1:-1], 1):
        part = text_section(i, heading, body, dark=i == 2)
        if i == 1:
            part = part.replace('<section ', '<section id="understanding-power" ', 1)
        parts.append(part)
    parts.append('<p class="ui iv3-source wrap">Technical reference: <a href="https://technav.ieee.org/topic/power-quality/">IEEE Technology Navigator, Power Quality</a>.</p>')
    parts.append(close(route, blocks[-1][0]))
    write_page(route, '\n'.join(parts), title=data['seo_title'], description=data['seo_description'])


def project_page(project: dict) -> None:
    slug = project['slug']
    route = f'/{slug}/'
    hero = project['hero']
    media = image(hero['src'], hero['alt'], route, priority=True, small=hero.get('src_small')) if hero else ''
    hero_class = 'iv3-project-hero' if hero else 'iv3-project-hero iv3-project-hero--type'
    subtitle = ' · '.join(x for x in [project['property_type'], project['completion']] if x)
    parts = [f'''<section class="ui {hero_class}" data-pes-editorial>{media}
      <div class="wrap iv3-project-hero__copy"><a class="iv3-back" href="../portfolio/">← All projects</a>
      <p class="eyebrow">PES / SELECTED WORK</p><h1>{E(project['title'])}</h1><p>{E(project['location'])}<br>{E(subtitle)}</p></div></section>''']
    parts.append(text_section(1, 'The residence', project['overview']))
    if project['pes_scope']:
        parts.append(text_section(2, 'PES scope of work', project['pes_scope'], dark=True))
    details = [(k.replace('_', ' ').title(), project[k]) for k in ('technical_challenge','electrical_solution','installation_details','project_coordination','final_result') if project.get(k)]
    if details:
        parts.append('<section class="ui iv3-craft" data-pes-editorial><div class="wrap"><p class="eyebrow">PES / ENGINEERING & CRAFTSMANSHIP</p><h2>Electrical craftsmanship.</h2>')
        parts += [f'<p><strong>{E(k)}</strong> {E(v)}</p>' for k,v in details]
        parts.append('</div></section>')
    gallery = project['gallery']
    if gallery:
        parts.append('<section class="ui iv3-gallery" data-pes-editorial><div class="wrap"><p class="eyebrow">THE PROJECT / IN DETAIL</p><h2>Project gallery.</h2><div class="iv3-gallery__grid">')
        parts += [f'<figure>{image(item["src"],item["alt"],route)}<figcaption>{E(item["alt"])}</figcaption></figure>' for item in gallery]
        parts.append('</div></div></section>')
    credits = [c for c in project['credits'] if c.get('verified')]
    if credits:
        parts.append('<section class="ui iv3-credits" data-pes-editorial><div class="wrap iv3-text__grid"><p class="eyebrow">PROJECT TEAM</p><div><h2>The people behind the project.</h2><dl>')
        parts += [f'<div><dt>{E(c["role"])}</dt><dd>{E(c["name"])}</dd></div>' for c in credits]
        parts.append('</dl></div></div></section>')
    next_project = PROJECTS[(PROJECTS.index(project) + 1) % len(PROJECTS)]
    next_hero = next_project['hero']
    next_media = image(next_hero['src'], next_hero['alt'], route, small=next_hero.get('src_small')) if next_hero else ''
    parts.append(f'<section class="ui iv3-next{" iv3-next--photo" if next_hero else ""}" data-pes-editorial>{next_media}<a href="../{E(next_project["slug"])}/"><span class="eyebrow">NEXT PROJECT</span><strong>{E(next_project["title"])}</strong><span aria-hidden="true">↗</span></a></section>')
    parts.append(close(route))
    description = f'Explore {project["title"]}, a {project["location"]} residence featured by Premium Energy Solutions.'
    write_page(route, '\n'.join(parts), title=f'{project["title"]} | Premium Energy Solutions', description=description, base='/hillside/')


def portfolio() -> None:
    route = '/portfolio/'
    cards = []
    for i,p in enumerate(PROJECTS,1):
        hero = p['hero']
        media = image(hero['src'], hero['alt'], route, small=hero.get('src_small')) if hero else '<span class="iv3-project-card__field" aria-hidden="true">PES / PROJECT</span>'
        cards.append(f'''<a class="iv3-project-card{' iv3-project-card--type' if not hero else ''}" href="../{E(p['slug'])}/">
          {media}<span class="iv3-project-card__copy"><span class="eyebrow">0{i} / {E(p['location'])}</span><strong>{E(p['title'])}</strong><span>{E(p['pes_scope'] or p['property_type'])}</span><span class="iv3-project-card__arrow" aria-hidden="true">↗</span></span></a>''')
    content = '''<section class="ui iv3-portfolio-intro" data-pes-editorial><div class="wrap"><p class="eyebrow">PREMIUM ENERGY SOLUTIONS / PROJECTS</p><h1>Selected<br><strong>residential work.</strong></h1><p>Explore residences featured by PES in Los Angeles. Each project is presented with the information and photography currently identified for review.</p></div></section>'''
    content += '<section class="ui iv3-portfolio-list" data-pes-editorial><div class="wrap">' + '\n'.join(cards) + '</div></section>' + close(route)
    page = EDITORIAL[route]
    write_page(route, content, title=page['seo_title'], description=page['seo_description'])


def add_editorial(route: str, content: str) -> None:
    target = path(route)
    current = target.read_text()
    current = re.sub(r'\n[ \t]*<!-- PES INTERIORS V3 START -->.*?<!-- PES INTERIORS V3 END -->\n?', '\n', current, flags=re.S)
    marker = '<section class="ui close dark"'
    if marker not in current:
        marker = '</main>'
    current = re.sub(r'\n{2,}(?=' + re.escape(marker) + ')', '\n', current)
    current = current.replace(marker, '<!-- PES INTERIORS V3 START -->\n' + content + '\n<!-- PES INTERIORS V3 END -->\n' + marker, 1)
    css = f'<link rel="stylesheet" href="{prefix(route)}assets/pes-interiors-v3.css">'
    if 'pes-interiors-v3.css' not in current:
        current = current.replace('</head>', f'{css}\n</head>', 1)
    data = EDITORIAL[route]
    if not re.search(r'<meta name="description"[^>]*>', current):
        current = current.replace('</title>', f'</title><meta name="description" content="{E(data["seo_description"], quote=True)}">', 1)
    current = re.sub(r'(?m)^[ \t]+$', '', current)
    target.write_text(current)


def existing_pages() -> None:
    # Services V4 owns the capabilities routes.
    route = '/careers/'
    blocks = split_copy(EDITORIAL[route]['editorial_approved'])
    # Current positions are not verified; use the master to present PES culture and historical benefits.
    content = ''.join(text_section(i, heading, body, dark=i == 2) for i,(heading,body) in enumerate(blocks[2:4],1))
    content += '<p class="ui iv3-source wrap">Role profiles and benefits are retained for review. Current openings and terms require confirmation from PES.</p>'
    add_editorial(route, content)
    route = '/contact/'
    content = '<section class="ui iv3-text" data-pes-editorial><div class="wrap iv3-text__grid"><p class="eyebrow">PES / LOS ANGELES</p><div><h2>Where we work.</h2><p>Serving Los Angeles, including Santa Monica, Pacific Palisades, Westwood and Beverly Hills. To discuss an electrical project or request an estimate, call <a href="tel:+12135873257">213-587-3257</a>.</p></div></div></section>'
    add_editorial(route, content)


def main() -> None:
    import subprocess
    subprocess.run(['node', str(ROOT / 'scripts/build_services_v4.mjs')], check=True)
    # Projects V4 owns these routes; never overwrite its master template.
    subprocess.run(['node', str(ROOT / 'scripts/build_projects_v4.mjs')], check=True)
    existing_pages()
    # Archived role descriptions remain intact; only add search descriptions.
    for route, data in EDITORIAL.items():
        if not route.startswith('/careers/') or route == '/careers/':
            continue
        target = path(route)
        current = target.read_text()
        if not re.search(r'<meta name="description"[^>]*>', current):
            current = current.replace('</title>', f'</title><meta name="description" content="{E(data["seo_description"], quote=True)}">', 1)
            target.write_text(current)
    print('Built PES Interiors V3: 16 internal routes; Home and Why Us untouched.')


if __name__ == '__main__':
    main()

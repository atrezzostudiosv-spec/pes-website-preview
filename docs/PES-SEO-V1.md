# PES SEO V1 — review / launch readiness

18 unique page titles and meta descriptions, English (US), self-referencing preview canonicals, Open Graph metadata and Twitter/X large image metadata. Shared corporate PNG 1200 x 630 from approved PES logo, real previously approved preview photographs for selected pages. The brand card is used for St. Cloud and historical career profiles to avoid misattributing photographs. Photo permissions and photographer credits are not production-cleared. The home card is a corporate design decision; no new image licensing claim.

Organization, WebSite, WebPage and BreadcrumbList JSON-LD; Service only for established services. Power Quality is editorial, not a confirmed installation offering. No fabricated postal address, ratings, certifications, job vacancies, pricing or local business attributes. Existing confirmed phone and Instagram are retained. Existing ALT texts remain; no visible page content changed.

Preview remains noindex,nofollow,noimageindex. robots.txt preserves default disallow, with specific social preview agents allowed in the project file; robots policies for GitHub Pages project subpaths are controlled by the origin root, so the live social fetch must be verified. No active production sitemap or redirects published. Public link previews may be cached and are not guaranteed by metadata.

## Launch checklist (do not execute without approval)
- Confirm final hosting/domain and every route, rights to social photos, project details, and contact routing; confirm careers vacancies before indexing role profiles.
- Switch SEO manifest preview_base to the approved production base, regenerate all pages and verify canonicals/OG URLs/JSON-LD, then remove noindex only on approved pages, set root robots allow crawl, and publish final XML sitemap.
- Draft sitemap at docs/seo-production-sitemap-draft.xml is a candidate URL inventory, not a live submission. Excludes historical role profiles and St. Cloud pending details; verify Laurel Way and all other pages before launch.
- Existing domain migration: configure server-side permanent redirects from verified old routes to mapped final URLs, keep redirects and test query strings, status and destinations. Do not overwrite the current site until approved.
- Verify Search Console ownership, submit sitemap, inspect live URL coverage and monitor indexing. Use Facebook Sharing Debugger and LinkedIn Post Inspector after deployment to refresh cached previews. Google may rewrite snippets; no ranking or rich result guarantee.

## Original route mapping (source: PES original media/content manifest)
| Previous path | Candidate path |
| --- | --- |
| /why-us | /about/ |
| /system-lighting-upgrade | /capabilities/lighting-systems/ |
| /automated-window-covering | /capabilities/automated-window-coverings/ |
| /lighting-design-and-installatio | /capabilities/lighting-design/ |
| /power-quality-and-energy-management-1 | /capabilities/power-quality-and-energy-management/ |
| /ev-charger-installation | /capabilities/ev-charging/ |
| /carrers | /careers/ |
| /foreman | /careers/foreman/ |
| /journeyman | /careers/journeyman/ |
| /electrician-1 | /careers/electrician/ |
| /apprentice | /careers/apprentice/ |
| /contact-pes | /contact/ |
Verify original project and service index paths before configuring any additional redirect.

## Maintenance
Edit data/seo-v1.json and run node scripts/pes-seo.mjs. Individual V4 page builders apply the same metadata module when writing their pages. Run node scripts/pes-seo.mjs --check and python qa/seo-v1.py. The production activation is a separate release gate, not an automatic change.

// Mapa strony generowana przy budowaniu: strony stałe + wszystkie artykuły bazy wiedzy.
import { SITE } from '../data/site.js';
const STATIC = [
  ['/', 1.0], ['/pl/', 0.9],
  ['/avoid-currency-exchange-scams-krakow', 0.8], ['/pl/jak-nie-dac-sie-oszukac-w-kantorze-krakow', 0.8],
  ['/scam-help', 0.8], ['/pl/oszukal-cie-kantor', 0.8],
  ['/before-you-visit-krakow', 0.8], ['/pl/zanim-odwiedzisz-krakow', 0.8],
  ['/exchange-euro-coins-krakow', 0.8], ['/pl/skup-bilonu-euro-krakow', 0.8],
  ['/exchange-damaged-withdrawn-banknotes-krakow', 0.8], ['/pl/wymiana-zniszczonych-wycofanych-banknotow-krakow', 0.8],
  ['/knowledge-base/', 0.7], ['/pl/baza-wiedzy/', 0.7], ['/privacy', 0.3],
];
const IMAGES = ['/images/exchange-kantor-black-sheep-florianska-37-krakow.jpg', '/images/front-og-2.jpg'];
export async function GET() {
  const today = new Date().toISOString().slice(0, 10);
  const posts = Object.values(import.meta.glob(['./knowledge-base/*.md', './pl/baza-wiedzy/*.md'], { eager: true }));
  const rows = STATIC.map(([p, pr]) => ({ loc: SITE.url + p, lastmod: today, pr, img: p === '/' || p === '/pl/' }));
  for (const p of posts) {
    const d = p.frontmatter.updated || p.frontmatter.date;
    rows.push({ loc: SITE.url + p.url.replace(/\.html$/, ''), lastmod: new Date(d).toISOString().slice(0, 10), pr: 0.6 });
  }
  const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' +
    rows.map((r) => `  <url><loc>${r.loc}</loc>${r.img ? IMAGES.map((i) => `<image:image><image:loc>${SITE.url}${i}</image:loc></image:image>`).join('') : ''}<lastmod>${r.lastmod}</lastmod><priority>${r.pr.toFixed(1)}</priority></url>`).join('\n') + '\n</urlset>\n';
  return new Response(xml, { headers: { 'content-type': 'application/xml; charset=utf-8' } });
}

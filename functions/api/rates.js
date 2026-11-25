// Kursy dla strony: detal z public/rates.json (ręcznie), hurt liczony z kursu rynkowego.
// Zasady i marże są w rates.json w polu "wholesaleAuto"; tu są tylko wartości domyślne.
// Źródła kursu rynkowego: źródło na żywo (do podłączenia w liveMids), zapasowo NBP (raz dziennie).
// Kursy hurtowe zaokrąglamy do 3 miejsc po przecinku (najwyżej 4 cyfry w tabeli).
// Hurt reguluje się sam. Gdy wyliczony kurs wychodzi poza detal, hurt = detal.
// Gdy brak kursu rynkowego albo rynek odbiega od detalu o więcej niż errorOutsideRetail,
// zwracamy błąd (mode: 'error') zamiast starych kursów ręcznych. Ręczne buyHurt/sellHurt
// są używane tylko po wyłączeniu automatu: "wholesaleAuto": { "enabled": false }.

const CODES = ['EUR', 'USD', 'GBP'];
const DEFAULTS = {
  enabled: true,
  dayStart: 9,            // godziny czasu polskiego, dni robocze
  dayEnd: 17,
  day:   { buy: { EUR: 0.02, USD: 0.02, GBP: 0.029 }, sell: { EUR: 0.005, USD: 0.005, GBP: 0.005 } },
  night: { buy: { EUR: 0.03, USD: 0.03, GBP: 0.039 }, sell: { EUR: 0.01,  USD: 0.01,  GBP: 0.01  } },
  maxDeviationFromNbp: 0.03,
  errorOutsideRetail: 0.05,  // kurs rynkowy dalej niż 5 gr poza widełkami detalu: błąd // kurs na żywo różni się od NBP o więcej niż 3%: nie ufamy mu
};
const CACHE_SECONDS = 600;

const round3 = (x) => Math.round(x * 1e3) / 1e3;

export function warsawParts(date) {
  const f = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Warsaw', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', weekday: 'short', hour12: false });
  const p = Object.fromEntries(f.formatToParts(date).map((x) => [x.type, x.value]));
  return { y: +p.year, m: +p.month, d: +p.day, h: +p.hour % 24, min: +p.minute, wd: p.weekday };
}

function easter(y) { // algorytm Meeusa, zwraca [miesiąc, dzień]
  const a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4;
  const f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31), day = ((h + l - 7 * m + 114) % 31) + 1;
  return [month, day];
}

export function isPolishHoliday(y, m, d) {
  const fixed = ['1-1', '1-6', '5-1', '5-3', '8-15', '11-1', '11-11', '12-24', '12-25', '12-26'];
  if (fixed.includes(`${m}-${d}`)) return true;
  const [em, ed] = easter(y);
  const base = Date.UTC(y, em - 1, ed);
  return [0, 1, 49, 60].some((off) => { // Wielkanoc, Poniedziałek Wielkanocny, Zielone Świątki, Boże Ciało
    const t = new Date(base + off * 86400000);
    return t.getUTCMonth() + 1 === m && t.getUTCDate() === d;
  });
}

// Pora: 'day' (dni robocze w godzinach rynku), 'weekend', 'holiday' albo 'evening'.
export function period(date, cfg) {
  const p = warsawParts(date);
  if (p.wd === 'Sat' || p.wd === 'Sun') return 'weekend';
  if (isPolishHoliday(p.y, p.m, p.d)) return 'holiday';
  return p.h >= cfg.dayStart && p.h < cfg.dayEnd ? 'day' : 'evening';
}

export function isDayMode(date, cfg) {
  const p = warsawParts(date);
  if (p.wd === 'Sat' || p.wd === 'Sun') return false;
  if (isPolishHoliday(p.y, p.m, p.d)) return false;
  return p.h >= cfg.dayStart && p.h < cfg.dayEnd;
}

async function getJson(url) {
  const res = await fetch(url, { headers: { accept: 'application/json' } });
  if (!res.ok) throw new Error(`${url.split('?')[0]} -> ${res.status}`);
  return res.json();
}

async function nbpMids() {
  const out = {}; let date = null;
  await Promise.all(CODES.map(async (c) => {
    const j = await getJson(`https://api.nbp.pl/api/exchangerates/rates/a/${c.toLowerCase()}/?format=json`);
    out[c] = Number(j.rates[0].mid); date = j.rates[0].effectiveDate;
  }));
  return { mids: out, time: date };
}

// Źródło kursu na żywo: Wise (kurs środkowy rynku, aktualizowany na bieżąco).
// Wymaga zmiennej WISE_TOKEN w ustawieniach Cloudflare Pages (token tylko do odczytu z konta Wise).
// Bez tokenu funkcja zwraca null i strona korzysta z NBP (zawsze szersze marże).
const WISE_URLS = ['https://api.wise.com/v1/rates', 'https://api.wise.com/2026Q4/rates'];
export const MAX_LIVE_AGE_MIN = 30; // starszy kurs nie jest traktowany jako "na żywo"

export function parseWise(json, code) {
  const row = Array.isArray(json) ? json.find((r) => r.source === code && r.target === 'PLN') : null;
  const rate = Number(row?.rate);
  if (!Number.isFinite(rate) || rate <= 0) throw new Error('wise: brak kursu ' + code);
  return { rate, time: row.time };
}

async function wisePair(base, code, token) {
  const res = await fetch(`${base}?source=${code}&target=PLN`, { headers: { accept: 'application/json', authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`wise ${code} -> ${res.status}`);
  return parseWise(await res.json(), code);
}

async function liveMids(env) {
  if (!env.WISE_TOKEN) return null;
  let lastErr;
  for (const base of WISE_URLS) {
    try {
      const rows = await Promise.all(CODES.map((c) => wisePair(base, c, env.WISE_TOKEN)));
      const mids = {}; let oldest = Infinity;
      rows.forEach((r, i) => { mids[CODES[i]] = r.rate; const t = Date.parse(r.time); if (Number.isFinite(t)) oldest = Math.min(oldest, t); });
      const time = Number.isFinite(oldest) ? new Date(oldest).toISOString() : new Date().toISOString();
      const fresh = (Date.now() - Date.parse(time)) / 60000 <= MAX_LIVE_AGE_MIN;
      return { mids, time, source: fresh ? 'wise' : 'wise-stale' };
    } catch (e) { lastErr = e; }
  }
  throw lastErr;
}

// Czysta funkcja: z ręcznych danych, kursów rynkowych i czasu wylicza odpowiedź. Łatwa do testowania.
export function compute(manual, market, now) {
  const cfg = { ...DEFAULTS, ...(manual.wholesaleAuto || {}) };
  cfg.day = { ...DEFAULTS.day, ...(manual.wholesaleAuto?.day || {}) };
  cfg.night = { ...DEFAULTS.night, ...(manual.wholesaleAuto?.night || {}) };
  const out = JSON.parse(JSON.stringify(manual));
  const info = { mode: 'manual', source: 'manual', quoteTime: null, reason: null, period: period(now, cfg), generatedAt: now.toISOString() };
  out.wholesaleAutoInfo = info;
  if (!cfg.enabled) { info.reason = 'auto wyłączone w rates.json'; return out; }
  const fail = (reason) => {
    info.mode = 'error'; info.reason = reason;
    for (const c of CODES) if (out.rates?.[c]) { out.rates[c].buyHurt = null; out.rates[c].sellHurt = null; }
    return out;
  };
  if (!market || !market.mids) return fail('brak kursu rynkowego');
  info.marketSource = market.source; info.marketTime = market.time;
  const live = market.source !== 'nbp' && market.source !== 'wise-stale';
  const day = live && isDayMode(now, cfg);
  const m = day ? cfg.day : cfg.night;
  const next = {};
  for (const c of CODES) {
    const r = manual.rates?.[c]; const mid = market.mids[c];
    if (!r || !Number.isFinite(mid)) return fail('brak danych dla ' + c);
    if (mid < r.buy - cfg.errorOutsideRetail || mid > r.sell + cfg.errorOutsideRetail) return fail(`kurs rynkowy ${c} ${mid} daleko poza detalem ${r.buy}-${r.sell}`);
    // Hurt nie może być gorszy dla klienta niż detal.
    let buyHurt = Math.max(round3(mid - m.buy[c]), r.buy);
    let sellHurt = Math.min(round3(mid + m.sell[c]), r.sell);
    // Rynek uciekł poza detal i marża się nie mieści: hurt = detal.
    if (buyHurt >= sellHurt) { buyHurt = r.buy; sellHurt = r.sell; }
    next[c] = { buyHurt, sellHurt };
  }
  for (const c of CODES) Object.assign(out.rates[c], next[c]);
  info.mode = day ? 'day' : 'night'; info.source = market.source; info.quoteTime = market.time;
  return out;
}

// Kurs rynkowy (Wise, NBP) jest pamiętany przez CACHE_SECONDS, żeby nie pytać o niego przy każdym wejściu.
// Plik rates.json (kursy detaliczne, godziny) jest czytany przy każdym wejściu, więc jego zmiana
// jest widoczna od razu po opublikowaniu strony.
async function marketData(context) {
  const { request, env } = context;
  const cacheKey = new Request(new URL('/api/_market-cache', request.url).toString());
  const cache = caches.default;
  const hit = await cache.match(cacheKey);
  if (hit) { try { return await hit.json(); } catch (e) { /* uszkodzony wpis: pobierz od nowa */ } }
  const data = { nbp: null, live: null, errors: [] };
  try { data.nbp = await nbpMids(); } catch (e) { data.errors.push(String(e.message || e)); }
  try { data.live = await liveMids(env); } catch (e) { data.errors.push(String(e.message || e)); }
  if (data.nbp || data.live) {
    const res = new Response(JSON.stringify(data), { headers: { 'content-type': 'application/json', 'cache-control': `public, max-age=${CACHE_SECONDS}` } });
    context.waitUntil(cache.put(cacheKey, res));
  }
  return data;
}

export async function onRequestGet(context) {
  const { request, env } = context;
  let manual;
  try {
    const res = await env.ASSETS.fetch(new URL('/rates.json', request.url));
    manual = await res.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: 'rates.json niedostępny' }), { status: 502, headers: { 'content-type': 'application/json' } });
  }

  const { nbp, live, errors: marketErrors } = await marketData(context);
  const errors = [...marketErrors];
  let market = null;
  if (live) {
    const cfg = { ...DEFAULTS, ...(manual.wholesaleAuto || {}) };
    const sane = !nbp || CODES.every((c) => Math.abs(live.mids[c] / nbp.mids[c] - 1) <= cfg.maxDeviationFromNbp);
    if (sane) market = live; else errors.push('kurs na żywo odbiega od NBP');
  }
  if (!market && nbp) market = { ...nbp, source: 'nbp' };

  const body = compute(manual, market, new Date());
  if (errors.length) body.wholesaleAutoInfo.errors = errors;
  return new Response(JSON.stringify(body), {
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}

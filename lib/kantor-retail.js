// Kursy detaliczne przysyłane z programu KANTOR (komputer w kantorze) i trzymane w Cloudflare KV.
// Używane przez functions/api/push-rates.js (zapis) i functions/api/rates.js (odczyt).
export const RETAIL_KEY = 'retail-v1';
export const RETAIL_CODES = ['EUR', 'USD', 'GBP'];
export const RETAIL_DEFAULTS = {
  enabled: true,
  maxSpread: 0.40,            // największa dopuszczalna różnica sprzedaż - kupno (zł)
  maxDeviationFromMid: 0.04,  // kurs nie może odbiegać od kursu rynkowego o więcej niż 4%
  maxJump: 0.50,              // gdy brak kursu rynkowego: największa zmiana względem poprzedniego kursu (zł)
};

const round4 = (n) => Math.round(n * 10000) / 10000;

// Przyjmuje treść pliku kursy.js ("window.KURSY={...}") albo zwykły JSON o tym samym kształcie.
// Klucze mogą być w cudzysłowach lub bez; kolejność pól w obiekcie dowolna.
export function parsePush(text) {
  const src = String(text || '');
  const upd = src.match(/["']?updated["']?\s*:\s*["']([^"']+)["']/);
  const list = [];
  const re = /\{[^{}]*\}/g; let m;
  while ((m = re.exec(src))) {
    const o = m[0];
    const code = o.match(/["']?code["']?\s*:\s*["']([A-Za-z]{3})["']/);
    const num = (k) => { const x = o.match(new RegExp(`["']?${k}["']?\\s*:\\s*["']?(-?[0-9]+(?:[.,][0-9]+)?)`)); return x ? Number(x[1].replace(',', '.')) : NaN; };
    if (!code) continue;
    const unit = num('unit'); const buy = num('buy'); const sell = num('sell');
    list.push({ code: code[1].toUpperCase(), unit: Number.isFinite(unit) && unit > 0 ? unit : 1, buy, sell });
  }
  return { updated: upd ? upd[1] : null, list };
}

// Zwraca { ok, reasons[], retail } ; retail = { rates: {EUR:{buy,sell},...}, others: {...}, updated }
export function validatePush(parsed, market, prev, cfgIn) {
  const cfg = { ...RETAIL_DEFAULTS, ...(cfgIn || {}) };
  const reasons = []; const rates = {}; const others = {};
  const byCode = {}; for (const r of parsed.list) byCode[r.code] = r;
  for (const c of RETAIL_CODES) {
    const r = byCode[c];
    if (!r) { reasons.push(`${c}: brak waluty`); continue; }
    const buy = round4(r.buy / r.unit); const sell = round4(r.sell / r.unit);
    if (!Number.isFinite(buy) || !Number.isFinite(sell) || buy <= 0 || sell <= 0) { reasons.push(`${c}: kurs nie jest liczbą dodatnią`); continue; }
    if (buy >= sell) { reasons.push(`${c}: kupno ${buy} nie jest niższe od sprzedaży ${sell}`); continue; }
    if (sell - buy > cfg.maxSpread + 1e-9) reasons.push(`${c}: różnica ${round4(sell - buy)} zł większa niż ${cfg.maxSpread} zł`);
    const mid = market?.mids?.[c];
    if (Number.isFinite(mid) && mid > 0) {
      for (const [k, v] of [['kupno', buy], ['sprzedaż', sell]]) {
        if (Math.abs(v / mid - 1) > cfg.maxDeviationFromMid) reasons.push(`${c}: ${k} ${v} odbiega od kursu rynkowego ${round4(mid)} o więcej niż ${cfg.maxDeviationFromMid * 100}%`);
      }
    } else if (prev?.rates?.[c]) {
      for (const [k, v, p] of [['kupno', buy, prev.rates[c].buy], ['sprzedaż', sell, prev.rates[c].sell]]) {
        if (Math.abs(v - p) > cfg.maxJump + 1e-9) reasons.push(`${c}: ${k} ${v} różni się od poprzedniego ${p} o więcej niż ${cfg.maxJump} zł`);
      }
    }
    rates[c] = { buy, sell };
  }
  for (const r of parsed.list) {
    if (RETAIL_CODES.includes(r.code)) continue;
    const buy = round4(r.buy / r.unit); const sell = round4(r.sell / r.unit);
    if (Number.isFinite(buy) && buy > 0) others[r.code] = { buy, sell: Number.isFinite(sell) && sell > 0 ? sell : null };
  }
  const updated = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(parsed.updated || '') ? parsed.updated.slice(0, 19) : null;
  return { ok: reasons.length === 0, reasons, retail: { rates, others, updated } };
}

// Nakłada kursy z kantoru na dane z rates.json. Zwraca opis źródła (retailInfo).
export function applyRetail(manual, stored) {
  const cfg = { ...RETAIL_DEFAULTS, ...(manual.retailFromKantor || {}) };
  if (!cfg.enabled) return { source: 'file', reason: 'wyłączone w rates.json' };
  if (!stored || !stored.rates) return { source: 'file', reason: 'brak kursów z kantoru' };
  for (const c of RETAIL_CODES) {
    const s = stored.rates[c]; if (!s || !manual.rates?.[c]) return { source: 'file', reason: 'niepełne kursy z kantoru' };
  }
  for (const c of RETAIL_CODES) { manual.rates[c].buy = stored.rates[c].buy; manual.rates[c].sell = stored.rates[c].sell; }
  const when = stored.updated || stored.receivedLocal || null;
  if (when) manual.updated = when.slice(0, 10);
  return { source: 'kantor', updated: when, receivedAt: stored.receivedAt || null };
}

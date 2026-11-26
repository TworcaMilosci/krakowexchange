// Przyjmuje kursy detaliczne z komputera w kantorze (skrypt kursy-www.ps1) i zapisuje je w Cloudflare KV.
// Wymaga w ustawieniach Cloudflare Pages: powiązania KV o nazwie RATES_KV oraz sekretu RATES_PUSH_KEY.
// Treść żądania: zawartość pliku kursy.js z kantoru (albo JSON o tym samym kształcie).
import { RETAIL_KEY, parsePush, validatePush } from '../../lib/kantor-retail.js';
import { marketData } from './rates.js';

const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

function sameKey(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!env.RATES_PUSH_KEY || env.RATES_PUSH_KEY.length < 24) return json({ ok: false, error: 'brak sekretu RATES_PUSH_KEY (min. 24 znaki) w ustawieniach strony' }, 503);
  if (!env.RATES_KV) return json({ ok: false, error: 'brak powiązania KV o nazwie RATES_KV w ustawieniach strony' }, 503);
  const auth = request.headers.get('authorization') || '';
  if (!sameKey(auth, 'Bearer ' + env.RATES_PUSH_KEY)) return json({ ok: false, error: 'zły klucz' }, 401);

  const text = await request.text();
  if (text.length > 20000) return json({ ok: false, error: 'za duża treść' }, 413);
  const parsed = parsePush(text);
  if (!parsed.list.length) return json({ ok: false, error: 'nie znaleziono kursów w przesłanej treści' }, 400);

  let manual = {}; try { manual = await (await env.ASSETS.fetch(new URL('/rates.json', request.url))).json(); } catch (e) { /* bez pliku: ustawienia domyślne */ }
  let market = null;
  try { const m = await marketData(context); market = m.live || m.nbp; } catch (e) { /* bez rynku: porównanie z poprzednim kursem */ }
  let prev = null; try { prev = await env.RATES_KV.get(RETAIL_KEY, 'json'); } catch (e) { /* pierwszy zapis */ }

  const v = validatePush(parsed, market, prev, manual.retailFromKantor);
  const now = new Date();
  if (!v.ok) {
    try { await env.RATES_KV.put('retail-rejected', JSON.stringify({ at: now.toISOString(), reasons: v.reasons, sent: v.retail })); } catch (e) { /* tylko diagnostyka */ }
    return json({ ok: false, error: 'kursy odrzucone, na stronie zostają poprzednie', reasons: v.reasons }, 422);
  }
  const stored = {
    ...v.retail,
    receivedAt: now.toISOString(),
    receivedLocal: now.toLocaleString('sv-SE', { timeZone: 'Europe/Warsaw' }).replace(' ', 'T'),
  };
  await env.RATES_KV.put(RETAIL_KEY, JSON.stringify(stored));
  return json({ ok: true, saved: stored.rates, updated: stored.updated || stored.receivedLocal });
}

export async function onRequestGet() {
  return json({ ok: false, error: 'ten adres przyjmuje tylko kursy wysyłane z kantoru' }, 405);
}

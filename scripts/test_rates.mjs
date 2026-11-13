import { compute, isDayMode, isPolishHoliday, warsawParts } from '../functions/api/rates.js';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const manual = JSON.parse(fs.readFileSync('public/rates.json', 'utf8'));
const mids = { EUR: 4.40, USD: 3.98, GBP: 5.26 };
const cfg = { dayStart: 9, dayEnd: 17 };
// czas: piątek 13.11.2026 12:00 Warszawa (CET, UTC+1)
const fri = new Date('2026-11-13T11:00:00Z'), friEve = new Date('2026-11-13T16:30:00Z'), sat = new Date('2026-11-14T11:00:00Z');
assert.equal(isDayMode(fri, cfg), true); assert.equal(isDayMode(friEve, cfg), false); assert.equal(isDayMode(sat, cfg), false);
assert.equal(isDayMode(new Date('2026-11-11T11:00:00Z'), cfg), false); // 11 listopada
assert.equal(isDayMode(new Date('2026-07-15T07:30:00Z'), cfg), true);  // lato: 9:30 CEST
assert.equal(isDayMode(new Date('2026-07-15T06:30:00Z'), cfg), false); // lato: 8:30 CEST
assert.equal(isPolishHoliday(2026, 4, 5), true); assert.equal(isPolishHoliday(2026, 4, 6), true); assert.equal(isPolishHoliday(2026, 6, 4), true); // Wielkanoc 5.04.2026, Boże Ciało 4.06.2026
assert.equal(isPolishHoliday(2027, 3, 29), true); // Poniedziałek Wielkanocny 2027
let r = compute(manual, { mids, source: 'twelvedata', time: 'x' }, fri);
assert.equal(r.wholesaleAutoInfo.mode, 'day');
assert.deepEqual([r.rates.EUR.buyHurt, r.rates.EUR.sellHurt], [4.38, 4.405]);
assert.deepEqual([r.rates.USD.buyHurt, r.rates.USD.sellHurt], [3.96, 3.985]);
assert.deepEqual([r.rates.GBP.buyHurt, r.rates.GBP.sellHurt], [5.231, 5.265]);
assert.equal(r.rates.EUR.buy, manual.rates.EUR.buy);
r = compute(manual, { mids, source: 'twelvedata', time: 'x' }, sat);
assert.equal(r.wholesaleAutoInfo.mode, 'night');
assert.deepEqual([r.rates.EUR.buyHurt, r.rates.EUR.sellHurt, r.rates.GBP.buyHurt, r.rates.GBP.sellHurt], [4.37, 4.41, 5.221, 5.27]);
r = compute(manual, { mids, source: 'nbp', time: '2026-11-13' }, fri); // NBP w dzień: zawsze szerzej
assert.equal(r.wholesaleAutoInfo.mode, 'night');
r = compute(manual, { mids: { ...mids, EUR: 4.50 }, source: 'twelvedata', time: 'x' }, fri); // poza widełkami detalu
assert.equal(r.wholesaleAutoInfo.mode, 'manual'); assert.equal(r.rates.EUR.buyHurt, manual.rates.EUR.buyHurt); assert.equal(r.rates.USD.buyHurt, manual.rates.USD.buyHurt);
r = compute(manual, null, fri); assert.equal(r.wholesaleAutoInfo.mode, 'manual');
r = compute({ ...manual, wholesaleAuto: { enabled: false } }, { mids, source: 'twelvedata', time: 'x' }, fri); assert.equal(r.wholesaleAutoInfo.mode, 'manual');
r = compute({ ...manual, wholesaleAuto: { day: { buy: { EUR: 0.015, USD: 0.02, GBP: 0.029 } } } }, { mids, source: 'twelvedata', time: 'x' }, fri);
assert.equal(r.rates.EUR.buyHurt, 4.385); assert.equal(r.rates.EUR.sellHurt, 4.405);
r = compute(manual, { mids: { EUR: 4.335, USD: 3.98, GBP: 5.26 }, source: 'twelvedata', time: 'x' }, fri); // blisko detalu: nie gorzej niż detal
assert.equal(r.rates.EUR.buyHurt, 4.33);
console.log('rates tests OK', warsawParts(fri));

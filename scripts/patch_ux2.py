import re,json
T={'en':dict(cap='We buy · We sell',r='Retail',w='Wholesale',aria='Today\'s rates. Tap to see the full board.',
    at='A currency exchange at Floriańska 37 since 2010',b_old='We have been exchanging money since 2010: until 2026',b_new='We have been at the same address since 2010: until 2026'),
   'pl':dict(cap='Kupno · Sprzedaż',r='Detal',w='Hurt',aria='Dzisiejsze kursy. Dotknij, aby zobaczyć pełną tablicę.',
    at='Kantor przy Floriańskiej 37 od 2010 roku',b_old='Wymieniamy walutę od 2010 roku: do 2026',b_new='Działamy pod tym samym adresem od 2010 roku: do 2026')}
CSS_OLD_START='        /* Pasek kursów nad hasłem'; CSS_OLD_END='        /* Jak nas rozpoznać: panel pod zdjęciem */'
CSS='''        /* Pasek kursów nad hasłem (tylko telefon i tablet; na komputerze tablica jest obok) */
        .rate-strip { display: block; margin-bottom: .9rem; padding: .6rem .8rem .7rem; border: 1px solid #262626; border-radius: 1rem; background: #141414; cursor: pointer; }
        .rate-strip .rs-head { display: flex; align-items: center; justify-content: space-between; gap: .5rem; margin-bottom: .45rem; }
        .rate-strip .rs-cap { font-size: .56rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: #a3a3a3; white-space: nowrap; }
        .rate-strip .rs-seg { display: inline-flex; border: 1px solid #3a3a3a; border-radius: 999px; padding: 2px; flex: none; }
        .rate-strip .rs-seg button { font: 800 .56rem/1 'Montserrat', sans-serif; letter-spacing: .12em; text-transform: uppercase; color: #8a8a8a; background: none; border: 0; border-radius: 999px; padding: .38rem .6rem; cursor: pointer; }
        .rate-strip .rs-seg button.on { background: #fff; color: #000; }
        .rate-strip .rs-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem; }
        .rate-strip .rs-item { min-width: 0; white-space: nowrap; font-size: clamp(.72rem, 3.3vw, .9rem); color: #e5e5e5; font-variant-numeric: tabular-nums; }
        .rate-strip .rs-item b { display: block; font-weight: 800; color: #fff; font-size: .78em; letter-spacing: .08em; margin-bottom: .1rem; }
        @media (min-width: 1024px) { .rate-strip { display: none; } }
        /* Telefon: cała góra strony (pasek, hasło, przyciski) ma się mieścić na pierwszym ekranie */
        @media (max-width: 1023px) {
            #top { padding-top: 4.6rem; }
            #top .hero-art { width: 74%; margin: -1.6rem 0 .6rem; }
            #top .hero-text .eyebrow { margin-bottom: .45rem; }
            #top .hero-slogan { margin-bottom: .6rem; font-size: .95rem; line-height: 1.5; }
            #top .hero-cta { gap: .6rem; }
            #top .hero-cta a { padding-top: .8rem; padding-bottom: .8rem; }
        }
        /* Otwarte teraz / zamknięte: zielona pulsująca kropka, gdy otwarte */
        @keyframes dot-pulse { 0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34,197,94,.55); } 50% { opacity: .55; box-shadow: 0 0 0 5px rgba(34,197,94,0); } }
        .live-dot { background: #22c55e !important; animation: dot-pulse 1.8s ease-in-out infinite; }
        .open-now { display: flex; align-items: center; gap: .55rem; font-size: .85rem; font-weight: 600; color: #e5e5e5; margin: 0 0 1rem; min-height: 1.3rem; }
        .open-now:empty { display: none; }
        .open-now .dot { width: .55rem; height: .55rem; border-radius: 50%; flex: none; background: #22c55e; animation: dot-pulse 1.8s ease-in-out infinite; }
        .open-now.closed { color: #a3a3a3; }
        .open-now.closed .dot { background: transparent; border: 1.5px solid #a3a3a3; animation: none; }
        #find { scroll-margin-top: 5.2rem; }
'''
JS_OLD_START='        // ----- Otwarte teraz -----'; JS_OLD_END='        function tierSpreads(buyKey, sellKey) {'
JS='''        // ----- Otwarte teraz -----
        // Stałe godziny tygodnia (minuty od północy; brak dnia = zamknięte). Wyjątki na konkretne daty
        // wpisuje się w rates.json: "specialHours": { "2026-11-15": "12:30-14:30", "2026-12-25": "closed" }
        const OPENING = { 1: [570, 1230], 2: [570, 1230], 3: [570, 1230], 4: [570, 1230], 5: [570, 1230], 6: [600, 1230] };
        function plHoliday(y, m, d) {
            if (["1-1", "1-6", "5-1", "5-3", "8-15", "11-1", "11-11", "12-24", "12-25", "12-26"].includes(m + "-" + d)) return true;
            const a = y % 19, b = Math.floor(y / 100), c = y % 100, dd = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - dd - g + 15) % 30, i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, mm = Math.floor((a + 11 * h + 22 * l) / 451);
            const base = Date.UTC(y, Math.floor((h + l - 7 * mm + 114) / 31) - 1, ((h + l - 7 * mm + 114) % 31) + 1);
            return [0, 1, 49, 60].some(o => { const t = new Date(base + o * 86400000); return t.getUTCMonth() + 1 === m && t.getUTCDate() === d; });
        }
        function hm(min) { return String(Math.floor(min / 60)).padStart(2, "0") + ":" + String(min % 60).padStart(2, "0"); }
        // Godziny dla daty (obiekt Date w UTC oznaczający dzień kalendarzowy w Polsce):
        // [od, do] w minutach, null = zamknięte, undefined = święto bez wpisu (nie wiemy)
        function hoursFor(day) {
            const y = day.getUTCFullYear(), m = day.getUTCMonth() + 1, d = day.getUTCDate();
            const key = y + "-" + String(m).padStart(2, "0") + "-" + String(d).padStart(2, "0");
            const sp = DATA && DATA.specialHours ? DATA.specialHours[key] : undefined;
            if (typeof sp === "string") {
                const mt = sp.match(/^\\s*(\\d{1,2})[:.](\\d{2})\\s*[-–]\\s*(\\d{1,2})[:.](\\d{2})\\s*$/);
                return mt ? [+mt[1] * 60 + +mt[2], +mt[3] * 60 + +mt[4]] : null;
            }
            if (plHoliday(y, m, d)) return undefined;
            return OPENING[day.getUTCDay()] || null;
        }
        function openStatus(nowDate) {
            const p = Object.fromEntries(new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Warsaw", year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric", hour12: false }).formatToParts(nowDate).map(x => [x.type, x.value]));
            const today = new Date(Date.UTC(+p.year, +p.month - 1, +p.day)), now = (+p.hour % 24) * 60 + +p.minute;
            const t = hoursFor(today);
            if (t === undefined) return { state: "holiday" };
            if (t && now >= t[0] && now < t[1]) return { state: "open", until: t[1] };
            if (t && now < t[0]) return { state: "closed", inDays: 0, at: t[0], wd: today.getUTCDay() };
            for (let n = 1; n <= 14; n++) {
                const day = new Date(today.getTime() + n * 86400000), h = hoursFor(day);
                if (h) return { state: "closed", inDays: n, at: h[0], wd: day.getUTCDay() };
            }
            return { state: "closed" };
        }
        function renderOpenNow() {
            const pl = currentLang === "pl", s = openStatus(new Date());
            const names = pl ? ["w niedzielę", "w poniedziałek", "we wtorek", "w środę", "w czwartek", "w piątek", "w sobotę"] : ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
            let cls = "open-now closed", text;
            if (s.state === "holiday") text = pl ? "Dziś święto: sprawdź godziny w Mapach Google" : "Public holiday today: check hours on Google Maps";
            else if (s.state === "open") { cls = "open-now"; text = (pl ? "Otwarte teraz · do " : "Open now · until ") + hm(s.until); }
            else if (s.at === undefined) text = pl ? "Zamknięte" : "Closed";
            else {
                const when = s.inDays === 0 ? (pl ? "dziś" : "today") : s.inDays === 1 ? (pl ? "jutro" : "tomorrow") : names[s.wd];
                text = (pl ? "Zamknięte · otwieramy " : "Closed · opens ") + when + (pl ? " o " : " at ") + hm(s.at);
            }
            document.querySelectorAll(".open-now").forEach(el => { el.className = cls; el.innerHTML = '<span class="dot" aria-hidden="true"></span><span></span>'; el.lastChild.textContent = text; });
        }
        setInterval(renderOpenNow, 60000);
        // ----- Pasek kursów na telefonie: detal / hurt -----
        let stripTier = "retail";
        function renderRateStrip() {
            const w = stripTier === "wholesale";
            for (const [code, r] of Object.entries(DATA.rates)) {
                const el = document.getElementById("rs-" + code); if (!el) continue;
                const b = w ? r.buyHurt : r.buy, s = w ? r.sellHurt : r.sell;
                el.textContent = (typeof b === "number" && typeof s === "number") ? fmtRate(b) + " · " + fmtRate(s) : "—";
            }
            document.querySelectorAll(".rs-seg button").forEach(btn => btn.classList.toggle("on", btn.dataset.tier === stripTier));
        }
        function setStripTier(tier, ev) { if (ev) ev.stopPropagation(); stripTier = tier; renderRateStrip(); }

'''
def fr(n):
    s=('%.3f'%n).rstrip('0'); return s if len(s.split('.')[1])>=2 else ('%.2f'%n)
R=json.load(open('public/rates.json'))['rates']
for f,lang in (('src/pages/index.astro','en'),('src/pages/pl/index.astro','pl')):
    t=T[lang]; s=open(f,encoding='utf-8').read()
    # strip markup
    m=re.search(r'<a href="#rates" class="rate-strip".*?</a>',s,re.S); assert m
    strip=('<div class="rate-strip" role="link" tabindex="0" aria-label="'+t['aria']+'" onclick="location.hash=\'#rates\'"><div class="rs-head"><span class="rs-cap">'+t['cap']+'</span>'
      '<span class="rs-seg" role="group"><button type="button" data-tier="retail" class="on" onclick="setStripTier(\'retail\', event)">'+t['r']+'</button><button type="button" data-tier="wholesale" onclick="setStripTier(\'wholesale\', event)">'+t['w']+'</button></span></div>'
      '<div class="rs-row">'+''.join(f'<span class="rs-item"><b>{c}</b><span id="rs-{c}">{fr(R[c]["buy"])} · {fr(R[c]["sell"])}</span></span>' for c in ('EUR','USD','GBP'))+'</div></div>')
    s=s[:m.start()]+strip+s[m.end():]
    # css + js replace blocks
    a=s.index(CSS_OLD_START); b=s.index(CSS_OLD_END); s=s[:a]+CSS+s[b:]
    a=s.index(JS_OLD_START); b=s.index(JS_OLD_END); s=s[:a]+JS+s[b:]
    # hero hooks
    s,n=re.subn(r'(<img src="(?:\.\./)?images/hero-flock\.webp"[^>]*class=")w-full -mt-12 mb-6 ',r'\1hero-art w-full -mt-12 mb-6 ',s); assert n==1
    s,n=re.subn(r'<p class="(text-neutral-400 text-base sm:text-lg mb-4 max-w-md" data-i18n="hero_slogan")',r'<p class="hero-slogan \1',s); assert n==1
    a='<div class="flex flex-col sm:flex-row gap-4">\n                    <a href="#rates" class="btn-solid" data-i18n="btn_rates">'; assert a in s
    s=s.replace(a,'<div class="hero-cta flex flex-col sm:flex-row gap-4">\n                    <a href="#rates" class="btn-solid" data-i18n="btn_rates">')
    a='<a href="#visit" class="btn-ghost" data-i18n="btn_visit">'; assert a in s; s=s.replace(a,'<a href="#find" class="btn-ghost" data-i18n="btn_visit">')
    a='<div class="loc-wrap">'; assert s.count(a)==1; s=s.replace(a,'<div class="loc-wrap" id="find">')
    a='<span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse" aria-hidden="true"></span>'; assert a in s; s=s.replace(a,'<span class="live-dot w-1.5 h-1.5 rounded-full" aria-hidden="true"></span>')
    # about
    for l in ('en','pl'):
        o={'en':'A currency exchange in Kraków since 2010','pl':'Kantor w Krakowie od 2010 roku'}[l]
        assert o in s; s=s.replace(o,T[l]['at'])
        assert T[l]['b_old'] in s; s=s.replace(T[l]['b_old'],T[l]['b_new'])
    open(f,'w',encoding='utf-8').write(s)
d='docs/INSTRUKCJA-KURSY.md'; x=open(d,encoding='utf-8').read()
if 'specialHours' not in x:
    x+='''
---

## Godziny otwarcia: wyjątki na konkretne dni

Znacznik "Otwarte teraz" na stronie liczy się ze stałych godzin (pon.-pt. 9:30-20:30, sob. 10:00-20:30, niedziela zamknięte).
Gdy danego dnia masz wolne albo inne godziny, dopisz ten dzień w `public/rates.json` w polu `specialHours`:

    "specialHours": {
      "2026-11-15": "12:30-14:30",
      "2026-12-24": "9:30-14:00",
      "2026-12-25": "closed"
    }

- Data w formacie RRRR-MM-DD, godziny jako OD-DO, a dzień wolny jako "closed".
- Wpis dotyczy tylko tej jednej daty; w pozostałe dni obowiązują stałe godziny.
- W polskie święta bez wpisu strona pokazuje "sprawdź godziny w Mapach Google". Jeśli w święto pracujesz, dopisz godziny; jeśli nie, dopisz "closed", wtedy strona policzy czas do następnego otwarcia.
- Stare daty można usuwać, ale nie trzeba.
- Pamiętaj o przecinkach między wpisami (po ostatnim bez przecinka).
'''
    open(d,'w',encoding='utf-8').write(x)
r=json.load(open('public/rates.json'))
if 'specialHours' not in r:
    r['specialHours']={}; json.dump(r,open('public/rates.json','w'),indent=2,ensure_ascii=False)
print('ok')

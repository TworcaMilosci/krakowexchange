import re,json
R=json.load(open('public/rates.json'))['rates']
T={
'en':dict(strip_cap='We buy · We sell', strip_aria="Today's retail rates. Tap to see the full board.",
  spot_eye='How to spot us', spot='Look for <b>the board with the black sheep</b> and the buy and sell rates for EUR, USD and GBP. Floriańska 37, between St. Florian\'s Gate and the Main Square. Don\'t get fleeced.',
  about_title='A currency exchange in Kraków since 2010',
  about_body='Exchange Kantor Black Sheep is a physical currency exchange office (kantor) at Floriańska 37 in Kraków\'s Old Town, listed in the NBP register of currency exchange activity. We have been exchanging money since 2010: until 2026 as Kantor Wymiany Walut "U Górali", today under a new name with the same owner. We exchange cash at the counter six days a week, with fair rates, 0% commission and fast, friendly service in English and Polish. In more than 250 Google reviews (4.8 average) customers most often mention good rates, quick service, and getting exactly what the board shows. The guides on this site are written by us, because we watch this street every day.',
  since='<p><b>Operating since:</b> 2010</p>'),
'pl':dict(strip_cap='Kupno · Sprzedaż', strip_aria='Dzisiejsze kursy detaliczne. Dotknij, aby zobaczyć pełną tablicę.',
  spot_eye='Jak nas rozpoznać', spot='Szukaj <b>tablicy z czarną owcą</b> i kursami skupu i sprzedaży EUR, USD, GBP. Floriańska 37, między Bramą Floriańską a Rynkiem Głównym. Nie daj się oskubać.',
  about_title='Kantor w Krakowie od 2010 roku',
  about_body='Exchange Kantor Black Sheep to stacjonarny kantor wymiany walut przy ul. Floriańskiej 37 na Starym Mieście w Krakowie, wpisany do rejestru działalności kantorowej NBP. Wymieniamy walutę od 2010 roku: do 2026 jako Kantor Wymiany Walut „U Górali”, dziś pod nową nazwą, z tym samym właścicielem. Wymieniamy gotówkę w okienku sześć dni w tygodniu: uczciwy kurs, 0% prowizji oraz szybka i miła obsługa po polsku i angielsku. W ponad 250 opiniach w Google (średnia 4,8) klienci najczęściej piszą o dobrych kursach, sprawnej obsłudze i o tym, że dostają dokładnie tyle, ile pokazuje tablica. Poradniki na tej stronie piszemy sami, bo na tę ulicę patrzymy codziennie.',
  since='<p><b>Działa od:</b> 2010 r.</p>')}
CSS='''
        /* Pasek kursów nad hasłem (tylko telefon i tablet; na komputerze tablica jest obok) */
        .rate-strip { display: block; margin-bottom: 1.1rem; padding: .7rem .9rem .75rem; border: 1px solid #262626; border-radius: 1rem; background: #141414; text-decoration: none; }
        .rate-strip .rs-cap { display: block; font-size: .58rem; font-weight: 700; letter-spacing: .22em; text-transform: uppercase; color: #a3a3a3; margin-bottom: .4rem; }
        .rate-strip .rs-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem; }
        .rate-strip .rs-item { min-width: 0; white-space: nowrap; font-size: clamp(.72rem, 3.3vw, .9rem); color: #e5e5e5; font-variant-numeric: tabular-nums; }
        .rate-strip .rs-item b { display: block; font-weight: 800; color: #fff; font-size: .78em; letter-spacing: .08em; margin-bottom: .1rem; }
        @media (min-width: 1024px) { .rate-strip { display: none; } }
        /* Otwarte teraz / zamknięte */
        .open-now { display: flex; align-items: center; gap: .5rem; font-size: .85rem; font-weight: 600; color: #e5e5e5; margin: 0 0 1.25rem; min-height: 1.3rem; }
        .open-now:empty { display: none; }
        .open-now .dot { width: .55rem; height: .55rem; border-radius: 50%; background: #fff; flex: none; }
        .open-now.closed { color: #a3a3a3; }
        .open-now.closed .dot { background: transparent; border: 1.5px solid #a3a3a3; }
        /* Jak nas rozpoznać: panel pod zdjęciem */
        .spot { margin-top: .9rem; padding: 1.25rem 1.5rem; border: 1px solid #262626; border-radius: 1rem; background: #141414; }
        .spot p:not(.eyebrow) { margin: 0; font-size: 1rem; line-height: 1.6; color: #d4d4d4; }
        .spot p b { color: #fff; font-weight: 700; }
        /* Drobne szare teksty przy tablicy: jaśniejszy odcień szarości */
        #rates .text-neutral-500, #board-note, #wholesale-note, #stale-note { color: #a3a3a3; }
        /* Komputer: "Skupujemy również" pod hasłem po lewej, tablica po prawej na całą wysokość */
        .hero-also { margin-top: -2.25rem; }
        @media (min-width: 1024px) {
            .hero-grid { grid-template-areas: "text board" "also board"; grid-template-rows: auto 1fr; }
            .hero-grid > .hero-text { grid-area: text; }
            .hero-grid > #rates { grid-area: board; }
            .hero-grid > .hero-also { grid-area: also; margin-top: 0; align-self: start; }
        }
'''
JS='''
        // ----- Otwarte teraz -----
        const OPENING = { 1: [570, 1230], 2: [570, 1230], 3: [570, 1230], 4: [570, 1230], 5: [570, 1230], 6: [600, 1230] }; // minuty od północy; 0 = niedziela (zamknięte)
        function plHoliday(y, m, d) {
            if (["1-1", "1-6", "5-1", "5-3", "8-15", "11-1", "11-11", "12-24", "12-25", "12-26"].includes(m + "-" + d)) return true;
            const a = y % 19, b = Math.floor(y / 100), c = y % 100, dd = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - dd - g + 15) % 30, i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, mm = Math.floor((a + 11 * h + 22 * l) / 451);
            const base = Date.UTC(y, Math.floor((h + l - 7 * mm + 114) / 31) - 1, ((h + l - 7 * mm + 114) % 31) + 1);
            return [0, 1, 49, 60].some(o => { const t = new Date(base + o * 86400000); return t.getUTCMonth() + 1 === m && t.getUTCDate() === d; });
        }
        function hm(min) { return String(Math.floor(min / 60)).padStart(2, "0") + ":" + String(min % 60).padStart(2, "0"); }
        function renderOpenNow() {
            const pl = currentLang === "pl";
            const p = Object.fromEntries(new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Warsaw", year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric", weekday: "short", hour12: false }).formatToParts(new Date()).map(x => [x.type, x.value]));
            const wd = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(p.weekday), now = (+p.hour % 24) * 60 + +p.minute;
            const names = pl ? ["w niedzielę", "w poniedziałek", "we wtorek", "w środę", "w czwartek", "w piątek", "w sobotę"] : ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
            let cls = "open-now closed", text;
            if (plHoliday(+p.year, +p.month, +p.day)) {
                text = pl ? "Dziś święto: sprawdź godziny w Mapach Google" : "Public holiday today: check hours on Google Maps";
            } else {
                const t = OPENING[wd];
                if (t && now >= t[0] && now < t[1]) { cls = "open-now"; text = (pl ? "Otwarte teraz · do " : "Open now · until ") + hm(t[1]); }
                else if (t && now < t[0]) text = (pl ? "Zamknięte · otwieramy dziś o " : "Closed · opens today at ") + hm(t[0]);
                else {
                    let n = 1; while (!OPENING[(wd + n) % 7]) n++;
                    const nd = (wd + n) % 7, when = n === 1 ? (pl ? "jutro" : "tomorrow") : names[nd];
                    text = (pl ? "Zamknięte · otwieramy " : "Closed · opens ") + when + (pl ? " o " : " at ") + hm(OPENING[nd][0]);
                }
            }
            document.querySelectorAll(".open-now").forEach(el => { el.className = cls; el.innerHTML = '<span class="dot" aria-hidden="true"></span><span></span>'; el.lastChild.textContent = text; });
        }
        setInterval(renderOpenNow, 60000);
        function renderRateStrip() {
            for (const [code, r] of Object.entries(DATA.rates)) {
                const el = document.getElementById("rs-" + code);
                if (el && typeof r.buy === "number") el.textContent = fmtRate(r.buy) + " · " + fmtRate(r.sell);
            }
        }
'''
def fr(n):
    s=('%.3f'%n).rstrip('0'); 
    return s if len(s.split('.')[1])>=2 else ('%.2f'%n)
for f,lang in (('src/pages/index.astro','en'),('src/pages/pl/index.astro','pl')):
    t=T[lang]; s=open(f,encoding='utf-8').read()
    # --- hero grid + strip + open-now + also-buy move
    a='<div class="relative z-10 max-w-6xl mx-auto grid lg:grid-cols-2 gap-14 items-start">\n\n            <div>'; assert a in s
    strip='<a href="#rates" class="rate-strip" aria-label="'+t['strip_aria']+'"><span class="rs-cap">'+t['strip_cap']+'</span><span class="rs-row">'+''.join(f'<span class="rs-item"><b>{c}</b><span id="rs-{c}">{fr(R[c]["buy"])} · {fr(R[c]["sell"])}</span></span>' for c in ('EUR','USD','GBP'))+'</span></a>'
    s=s.replace(a,'<div class="hero-grid relative z-10 max-w-6xl mx-auto grid lg:grid-cols-2 gap-14 items-start">\n\n            <div class="hero-text">\n                '+strip)
    m=re.search(r'(data-i18n="hero_reviews">[^<]*</span>\s*</a>)',s); assert m
    s=s[:m.end()]+'\n                <p class="open-now" aria-live="polite"></p>'+s[m.end():]
    s=s.replace('class="group inline-flex items-center mb-6" aria-label=','class="group inline-flex items-center mb-3" aria-label=',1)
    m=re.search(r'\n(\s*)<!-- Also buy -->\n\s*<div class="mt-5 (bg-\[#141414\]/60 border border-neutral-800 rounded-3xl px-6 py-5)">(.*?)\n\s*</div>\n(\s*)</div>\n(\s*)</div>\n(\s*)</header>',s,re.S); assert m,f
    also='\n            <!-- Also buy -->\n            <div class="hero-also '+m.group(2)+'">'+m.group(3)+'\n            </div>'
    s=s[:m.start()]+'\n'+m.group(4)+'</div>'+also+'\n'+m.group(5)+'</div>\n'+m.group(6)+'</header>'+s[m.end():]
    # --- hours card: open-now line under eyebrow
    m=re.search(r'(<p class="eyebrow mb-3" data-i18n="visit_hours">[^<]*</p>)',s); assert m
    s=s[:m.end()]+'\n                    <p class="open-now" style="margin-bottom:.9rem"></p>'+s[m.end():]
    # --- spot panel instead of caption
    m=re.search(r'<p class="text-center" style="[^"]*" data-i18n="visit_photo_caption"[^>]*>.*?</p>',s,re.S); assert m
    s=s[:m.start()]+'<div class="spot"><p class="eyebrow mb-2">'+t['spot_eye']+'</p><p data-i18n="visit_photo_caption" data-i18n-html="">'+t['spot']+'</p></div>'+s[m.end():]
    for l in ('en','pl'):
        s,n=re.subn(r'visit_photo_caption: "(?:[^"\\]|\\.)*(?:black sheep|czarną owcą)(?:[^"\\]|\\.)*"',lambda mm: mm.group(0) if (('black sheep' in mm.group(0))!=(l=='en')) else 'visit_photo_caption: "'+T[l]['spot'].replace('"','\\"')+'"',s)
    # --- about
    s,n=re.subn(r'(<h2 class="display text-2xl sm:text-3xl mb-6" data-i18n="about_title">)[^<]*(</h2>)',lambda mm:mm.group(1)+t['about_title']+mm.group(2),s); assert n==1
    s,n=re.subn(r'(<p class="text-neutral-400 leading-relaxed" data-i18n="about_body">).*?(</p>)',lambda mm:mm.group(1)+t['about_body']+mm.group(2),s,flags=re.S); assert n==1
    for l,k in (('en','A real kantor, not a portal'),('pl','Prawdziwy kantor, nie portal')):
        a='about_title: "'+k+'"'; assert s.count(a)==1,(f,a); s=s.replace(a,'about_title: "'+T[l]['about_title']+'"')
    cnt=0
    def bodyrep(mm):
        global cnt; cnt+=1
        l='en' if 'is a licensed' in mm.group(0) or 'physical currency' in mm.group(0) else 'pl'
        return 'about_body: "'+T[l]['about_body'].replace('"','\\"')+'"'
    s=re.sub(r'about_body: "(?:[^"\\]|\\.)*"',bodyrep,s); assert cnt==2,cnt
    for l,k in (('en','<p><b>Address:</b>'),('pl','<p><b>Adres:</b>')):
        assert s.count(k)>=1; s=s.replace(k,T[l]['since']+k)
    def ld(mm):
        d=json.loads(mm.group(2))
        if d.get('@type')!='FinancialService': return mm.group(0)
        d['foundingDate']='2010'
        return mm.group(1)+'\n'+json.dumps(d,ensure_ascii=False,indent=2)+'\n    '+mm.group(3)
    s=re.sub(r'(<script is:inline type="application/ld\+json">)(.*?)(</script>)',ld,s,flags=re.S)
    # --- css + js
    a='        /* Sekcja lokalizacji'; assert a in s; s=s.replace(a,CSS.strip('\n')+'\n'+a,1)
    s=s.replace('font-size: clamp(0.66rem, 3.05vw, 0.8rem); font-weight: 600; color: #d4d4d4; white-space: nowrap; }','font-size: clamp(0.66rem, 3.05vw, 0.8rem); font-weight: 600; color: #d4d4d4; }')
    a='        function tierSpreads(buyKey, sellKey) {'; assert a in s; s=s.replace(a,JS.strip('\n')+'\n\n'+a)
    # EN spread: krótszy zapis, jednostka raz na końcu
    a='.map(([code, r]) => code + " " + fmtSpread(r[sellKey] - r[buyKey])).join(" · ");'; assert a in s
    s=s.replace(a,'.map(([code, r]) => code + " " + fmtSpread(r[sellKey] - r[buyKey]).replace(" PLN", "")).join(" · ") + (currentLang === "pl" ? "" : " PLN");')
    a='            renderBoardNote();\n            calculate();'; assert s.count(a)>=1
    s=s.replace(a,'            renderBoardNote();\n            renderRateStrip();\n            renderOpenNow();\n            calculate();')
    open(f,'w',encoding='utf-8').write(s)
l=open('public/llms.txt',encoding='utf-8').read()
if 'Operating since' not in l: l=l.replace('- Address: Floriańska 37','- Operating since 2010 (until 2026 under the name Kantor Wymiany Walut U Górali)\n- Address: Floriańska 37'); open('public/llms.txt','w',encoding='utf-8').write(l)
print('ok')

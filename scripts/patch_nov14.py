import re,json,glob
FN={'pl':'w godzinach pracy polskiego rynku walutowego','en':'during Polish FX market hours'}
def fix_answer(txt,lang):
    old='2–3 gr' if lang=='pl' else '0.02–0.03 PLN'; new='1–3 gr*' if lang=='pl' else '0.01–0.03 PLN*'
    if old not in txt: return txt
    return txt.replace(old,new)+' (*'+FN[lang]+')'
for f,lang in (('src/pages/index.astro','en'),('src/pages/pl/index.astro','pl')):
    s=open(f,encoding='utf-8').read()
    # --- spread texts: dict strings, html paragraphs
    for l in ('pl','en'):
        old='2–3 gr' if l=='pl' else '0.02–0.03 PLN'
        s=re.sub(r'(faq_a(?:11|2): ")((?:[^"\\]|\\.)*)(")',lambda m:m.group(1)+(fix_answer(m.group(2),l) if old in m.group(2) else m.group(2))+m.group(3),s)
        # facts (dict + html)
        fo=('w hurcie 2–3 gr; większe kwoty negocjujemy</p>','w hurcie 1–3 gr*; większe kwoty negocjujemy</p>') if l=='pl' else ('wholesale 0.02–0.03 PLN; larger amounts negotiable</p>','wholesale 0.01–0.03 PLN*; larger amounts negotiable</p>')
        s=s.replace(fo[0],fo[1])
        end='tablica z czarną owcą i kursami skupu i sprzedaży</p>' if l=='pl' else 'the board with the black sheep and both buy and sell rates</p>'
        s=s.replace(end,end+'<p><small>* '+FN[l]+'</small></p>')
    s=re.sub(r'(<p data-i18n="faq_a(?:11|2)" data-i18n-html="">)(.*?)(</p>)',lambda m:m.group(1)+fix_answer(m.group(2),lang)+m.group(3),s,flags=re.S)
    # --- JSON-LD
    def ldfix(m):
        d=json.loads(m.group(2)); ch=False
        if d.get('@type')=='FAQPage':
            for q in d['mainEntity']:
                a=q['acceptedAnswer']; n=fix_answer(a['text'],lang)
                if 'Sobota: 09:30' in n or 'Saturday: 09:30' in n: n=n.replace('Sobota: 09:30','Sobota: 10:00').replace('Saturday: 09:30','Saturday: 10:00')
                if n!=a['text']: a['text']=n; ch=True
            return m.group(1)+json.dumps(d,ensure_ascii=False)+m.group(3) if ch else m.group(0)
        if d.get('@type')=='FinancialService':
            d['description']=d['description'].replace('hurtowy 2–3 gr przy','hurtowy 1–3 gr w godzinach pracy polskiego rynku walutowego, kursy dla').replace('wholesale spread 0.02–0.03 PLN at','wholesale spread 0.01–0.03 PLN during Polish FX market hours, rates shown for')
            for o in d['openingHoursSpecification']:
                if o['dayOfWeek']==['Saturday']: o['opens']='10:00'
            return m.group(1)+'\n'+json.dumps(d,ensure_ascii=False,indent=2)+'\n    '+m.group(3)
        return m.group(0)
    s=re.sub(r'(<script is:inline type="application/ld\+json">)(.*?)(</script>)',ldfix,s,flags=re.S)
    left=[x for x in re.findall(r'.{40}(?:2–3 gr|0\.02–0\.03 PLN).{20}',s)]; assert not left,left[:2]
    # --- Saturday hours
    n=s.count('Sobota: 09:30–20:30')+s.count('Saturday: 09:30–20:30'); s=s.replace('Sobota: 09:30–20:30','Sobota: 10:00–20:30').replace('Saturday: 09:30–20:30','Saturday: 10:00–20:30'); assert n>=3,n
    m=re.search(r'(data-i18n="hours_sat">[^<]*</span></p>\s*<p class="text-lg font-semibold num mb-2">)09:30 – 20:30',s); assert m; s=s[:m.end(1)]+'10:00 – 20:30'+s[m.end():]
    # --- rate format: max 3 decimals
    a='return n.toFixed(Math.min(Math.max(dec, 2), 4));'; assert a in s; s=s.replace(a,'return n.toFixed(Math.min(Math.max(dec, 2), 3)); // najwyżej 4 cyfry w tabeli')
    # --- update time + weekend label
    a='document.getElementById("board-date").textContent = DATA.updated || "—";'; assert a in s
    s=s.replace(a,'''const ai = DATA.wholesaleAutoInfo;
            let stamp = DATA.updated || "—";
            if (ai && ai.mode !== "manual" && ai.generatedAt) {
                const g = new Date(ai.generatedAt);
                if (!isNaN(g)) stamp = g.toLocaleDateString("sv-SE", { timeZone: "Europe/Warsaw" }) + " " + g.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Warsaw" });
            }
            document.getElementById("board-date").textContent = stamp;
            const sl = document.querySelector('[data-i18n="spread_label"]');
            if (sl) sl.textContent = (ai && ai.mode !== "manual" && ai.period === "weekend") ? translations[currentLang].spread_weekend : translations[currentLang].spread_label;''')
    s=s.replace('new Date(DATA.updated + "T00:00:00")','new Date(String(DATA.updated).slice(0, 10) + "T00:00:00")')
    for a,b in (('spread_label: "Spread",','spread_label: "Spread", spread_weekend: "Weekend spread",'),):
        pass
    i=s.index('tier_retail_sub: "any amount"'); s=s[:i]+s[i:].replace('spread_label: "Spread",','spread_label: "Spread", spread_weekend: "Weekend spread",',1)
    i=s.index('tier_retail_sub: "każda kwota"'); s=s[:i]+s[i:].replace('spread_label: "Spread",','spread_label: "Spread", spread_weekend: "Weekendowy spread",',1)
    open(f,'w',encoding='utf-8').write(s)
for f in glob.glob('src/pages/**/*.astro',recursive=True):
    s=open(f,encoding='utf-8').read(); o=s
    s=s.replace('Czynne od poniedziałku do soboty, 09:30–20:30','Czynne od poniedziałku do piątku 09:30–20:30, w sobotę 10:00–20:30').replace('Open Monday to Saturday, 09:30–20:30','Open Monday to Friday 09:30–20:30, Saturday 10:00–20:30')
    if s!=o: open(f,'w',encoding='utf-8').write(s)
d='docs/INSTRUKCJA-KURSY.md'; s=open(d,encoding='utf-8').read()
s=re.sub(r'Źródła kursu rynkowego: Twelve Data[^\n]*','Źródła kursu rynkowego: źródło na żywo (jeszcze niepodłączone, wybór w toku), zapasowo NBP (jeden kurs dziennie; wtedy zawsze obowiązują szersze marże). Kursy hurtowe są zaokrąglane do 3 miejsc po przecinku.',s); open(d,'w',encoding='utf-8').write(s)
print('ok')

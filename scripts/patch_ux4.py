import re
SL={'en':("The best exchange rates in Kraków's Old Town, with a spread of just a few groszy. The rate you see is the rate you get.",
          "The best exchange rates in Kraków's Old Town<span class=\"sl-x\">, with a spread of just a few groszy</span>. The rate you see is the rate you get."),
    'pl':("Najlepsze kursy walut w centrum Krakowa, spread tylko kilka groszy. Kurs, który widzisz, to kurs, który dostajesz.",
          "Najlepsze kursy walut w centrum Krakowa<span class=\"sl-x\">, spread tylko kilka groszy</span>. Kurs, który widzisz, to kurs, który dostajesz.")}
for f,lang in (('src/pages/index.astro','en'),('src/pages/pl/index.astro','pl')):
    s=open(f,encoding='utf-8').read()
    # H1 obejmuje nadtytuł
    m=re.search(r'<p class="eyebrow mb-3">(<span class="whitespace-nowrap" data-i18n="hero_eyebrow_1">.*?</span> · <span class="whitespace-nowrap" data-i18n="hero_eyebrow_2">.*?</span>)</p>\s*<h1 class="(display [^"]*)" data-i18n="hero_title">(.*?)</h1>',s,re.S); assert m
    s=s[:m.start()]+f'<h1 class="hero-h1"><span class="eyebrow hero-eyebrow">{m.group(1)}</span> <span class="hero-h {m.group(2)}" data-i18n="hero_title">{m.group(3)}</span></h1>'+s[m.end():]
    # hasło: część ukrywana na telefonie (zostaje w kodzie)
    old,new=SL[lang]
    a=f'data-i18n="hero_slogan">{old}</p>'; assert a in s; s=s.replace(a,f'data-i18n="hero_slogan" data-i18n-html="">{new}</p>')
    for l in ('en','pl'):
        o,n=SL[l]; a=f'hero_slogan: "{o}"'; assert a in s,a; s=s.replace(a,'hero_slogan: "'+n.replace('"','\\"')+'"')
    # CSS
    a=s.index("            #top { padding-top: 4.4rem; }"); b=s.index("        /* Otwarte teraz / zamknięte")
    s=s[:a]+'''            #top { padding-top: 4.6rem; }
            .rate-strip { margin-bottom: 1.1rem; padding: .55rem .8rem .6rem; }
            #top .hero-eyebrow { margin-bottom: .55rem; }
            #top .hero-h { margin-bottom: .4rem; }
            #top .open-now { margin-bottom: 1.1rem; }
            #top .hero-art { display: block; width: 66%; margin: -1.2rem auto .7rem; }
            #top .hero-slogan { margin-bottom: .9rem; font-size: .95rem; line-height: 1.5; }
            /* pasek kursów zastępuje przycisk "zobacz kursy"; zostaje jeden, główny przycisk */
            #top .hero-cta .btn-solid { display: none; }
            #top .hero-cta .btn-ghost { background: #fff; color: var(--ink); }
        }
        @media (max-width: 639px) {
            #top .hero-h { font-size: 1.95rem; }
            #top .hero-eyebrow { white-space: nowrap; letter-spacing: .12em; font-size: clamp(.56rem, 2.85vw, .7rem); }
            #top .hero-slogan .sl-x { display: none; }
        }
        .hero-h1 { margin: 0; }
        .hero-h1 > span { display: block; }
        .hero-eyebrow { margin-bottom: .75rem; }
'''+s[b:]
    # próg hurtowy 1 000 EUR
    for a,b in (('wholesaleFrom: "5 000 EUR"','wholesaleFrom: "1 000 EUR"'),('wholesaleMinAmount: 5000','wholesaleMinAmount: 1000')):
        assert a in s; s=s.replace(a,b)
    n=s.count('5 000 EUR'); s=s.replace('5 000 EUR','1 000 EUR'); print(f,'5 000 ->',n)
    open(f,'w',encoding='utf-8').write(s)

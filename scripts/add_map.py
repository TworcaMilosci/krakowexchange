# Wstawia mapkę-schemat okolicy (SVG) pod zdjęciem w sekcji "Jak nas znaleźć".
import re
L={'pl':dict(planty='PLANTY',barb='BARBAKAN',gate='BRAMA FLORIAŃSKA',pij='ul. Pijarska',marka='ul. św. Marka',tom='ul. św. Tomasza',rynek='RYNEK GŁÓWNY',mar='Kościół Mariacki',hotel='Hotel Wyndham Grand · Swatch',st='Dworzec Główny',stt='ok. 10 min pieszo',cta='Otwórz w Mapach Google →',aria='Mapka dojścia: Exchange Kantor Black Sheep, Floriańska 37, 120 m od Bramy Floriańskiej i 230 m od Rynku Głównego. Kliknij, aby otworzyć Mapy Google.',title='Mapka okolicy'),
'en':dict(planty='PLANTY PARK',barb='BARBICAN',gate="ST. FLORIAN'S GATE",pij='Pijarska St.',marka='św. Marka St.',tom='św. Tomasza St.',rynek='MAIN SQUARE',mar="St. Mary's Basilica",hotel='Wyndham Grand Hotel · Swatch',st='Railway station',stt='about 10 min on foot',cta='Open in Google Maps →',aria="Map: Exchange Kantor Black Sheep, Floriańska 37, 120 m from St. Florian's Gate and 230 m from the Main Square. Click to open Google Maps.",title='Area map')}
def svg(l,base):
    t=L[l]; F="font-family:'Montserrat','Montserrat Fallback',system-ui,sans-serif"
    return f'''
                <a id="area-map" href="https://maps.google.com/?cid=3299726714959505459" target="_blank" rel="noopener" aria-label="{t['aria']}" style="display:block;text-decoration:none">
                    <svg viewBox="0 0 400 470" role="img" aria-label="{t['title']}" style="display:block;width:100%;height:auto;border:1px solid #232323;border-radius:20px;background:#141414;{F}">
                        <rect x="0" y="0" width="400" height="40" fill="#19211b"/>
                        <text x="16" y="25" fill="#5f7a66" font-size="10" font-weight="700" letter-spacing="2">{t['planty']}</text>
                        <text x="384" y="18" fill="#bdbdbd" font-size="10.5" font-weight="700" text-anchor="end">{t['st']} →</text>
                        <text x="384" y="32" fill="#7d7d7d" font-size="9.5" text-anchor="end">{t['stt']}</text>
                        <line x1="24" y1="78" x2="376" y2="78" stroke="#2a2a2a" stroke-width="7" stroke-linecap="round"/>
                        <line x1="24" y1="212" x2="376" y2="212" stroke="#2a2a2a" stroke-width="7" stroke-linecap="round"/>
                        <line x1="24" y1="316" x2="376" y2="316" stroke="#2a2a2a" stroke-width="7" stroke-linecap="round"/>
                        <rect x="24" y="398" width="176" height="56" rx="6" fill="#1f1f1f"/>
                        <line x1="200" y1="44" x2="200" y2="398" stroke="#3d3d3d" stroke-width="13" stroke-linecap="round"/>
                        <circle cx="200" cy="24" r="11" fill="#141414" stroke="#8a8a8a" stroke-width="2"/>
                        <text x="218" y="28" fill="#8a8a8a" font-size="9.5" font-weight="700" letter-spacing="1.5">{t['barb']}</text>
                        <rect x="186" y="58" width="28" height="18" rx="3" fill="#141414" stroke="#fff" stroke-width="2"/>
                        <text x="174" y="64" fill="#fff" font-size="10.5" font-weight="800" letter-spacing="1" text-anchor="end">{t['gate']}</text>
                        <text x="376" y="70" fill="#6f6f6f" font-size="9.5" text-anchor="end">{t['pij']}</text>
                        <text x="376" y="230" fill="#6f6f6f" font-size="9.5" text-anchor="end">{t['marka']}</text>
                        <text x="376" y="334" fill="#6f6f6f" font-size="9.5" text-anchor="end">{t['tom']}</text>
                        <text x="228" y="300" fill="#8a8a8a" font-size="9.5" font-weight="700" letter-spacing="2" transform="rotate(-90 228 300)">FLORIAŃSKA</text>
                        <text x="112" y="431" fill="#bdbdbd" font-size="11" font-weight="800" letter-spacing="2" text-anchor="middle">{t['rynek']}</text>
                        <rect x="212" y="404" width="40" height="44" rx="4" fill="#141414" stroke="#8a8a8a" stroke-width="1.5"/>
                        <path d="M232 414v24M224 422h16" stroke="#8a8a8a" stroke-width="2" stroke-linecap="round"/>
                        <text x="262" y="430" fill="#8a8a8a" font-size="9.5">{t['mar']}</text>
                        <text x="160" y="186" fill="#6f6f6f" font-size="9" text-anchor="end">{t['hotel']}</text>
                        <path d="M176 84v94M171 84h10M171 178h10" stroke="#6f6f6f" stroke-width="1.2" fill="none" stroke-dasharray="3 3"/>
                        <text x="166" y="135" fill="#e5e5e5" font-size="11" font-weight="700" text-anchor="end">120 m · &lt; 1 min</text>
                        <path d="M176 194v198M171 194h10M171 392h10" stroke="#6f6f6f" stroke-width="1.2" fill="none" stroke-dasharray="3 3"/>
                        <text x="166" y="372" fill="#e5e5e5" font-size="11" font-weight="700" text-anchor="end">230 m · &lt; 2 min</text>
                        <circle cx="212" cy="186" r="5" fill="#fff"/>
                        <line x1="212" y1="186" x2="232" y2="172" stroke="#fff" stroke-width="2"/>
                        <text x="222" y="203" fill="#8a8a8a" font-size="9">Souvenirs I Love Krakow</text>
                        <text x="216" y="97" fill="#8a8a8a" font-size="9">McDonald's</text>
                        <rect x="228" y="142" width="40" height="40" rx="10" fill="#dadada" stroke="#fff" stroke-width="2"/>
                        <image href="{base}images/sygnet-96.png" x="231" y="145" width="34" height="34"/>
                        <text x="276" y="157" fill="#fff" font-size="14" font-weight="800" textLength="104" lengthAdjust="spacingAndGlyphs">EXCHANGE</text>
                        <text x="276" y="169" fill="#fff" font-size="8.6" font-weight="800" textLength="104" lengthAdjust="spacingAndGlyphs">KANTOR <tspan fill="#a3a3a3" font-weight="700">BLACK SHEEP</tspan></text>
                        <text x="276" y="183" fill="#bdbdbd" font-size="9.5">Floriańska 37</text>
                    </svg>
                    <span style="display:block;text-align:center;margin-top:.6rem;font-size:.8rem;color:#bdbdbd;text-decoration:underline;text-underline-offset:4px">{t['cta']}</span>
                </a>'''
for f,l,base in (('src/pages/index.astro','en',''),('src/pages/pl/index.astro','pl','../')):
    s=open(f,encoding='utf-8').read()
    s=re.sub(r'\n\s*<a id="area-map".*?</a>','',s,flags=re.S)
    m=re.search(r'<p class="text-center" style="[^"]*" data-i18n="visit_photo_caption"[^>]*>.*?</p>',s,re.S); assert m
    k=s.index('</div>',m.end())+6  # po zamknięciu .loc-photo
    s=s[:k]+svg(l,base)+s[k:]
    open(f,'w',encoding='utf-8').write(s)
print('map ok')

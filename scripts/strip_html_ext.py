# Jednorazowo: adresy bez końcówki .html (tak serwuje je Cloudflare Pages).
import re,glob
SLUGS=['avoid-currency-exchange-scams-krakow','before-you-visit-krakow','exchange-damaged-withdrawn-banknotes-krakow','exchange-euro-coins-krakow','privacy','scam-help','jak-nie-dac-sie-oszukac-w-kantorze-krakow','oszukal-cie-kantor','skup-bilonu-euro-krakow','wymiana-zniszczonych-wycofanych-banknotow-krakow','zanim-odwiedzisz-krakow']
pat=re.compile(r'\b('+'|'.join(map(re.escape,SLUGS))+r')\.html')
for f in glob.glob('src/pages/**/*.astro',recursive=True)+['public/sitemap.xml','public/llms.txt']:
    s=open(f,encoding='utf-8').read(); o=s
    s=s.replace('pl/index.html','pl/').replace('../index.html','../').replace('index.html#','./#')
    s=re.sub(r'(?<=["\'])index\.html(?=["\'])','./',s)
    s=pat.sub(r'\1',s)
    assert '.html' not in s.replace('index\\.html',''),(f,re.findall(r'.{30}\.html.{10}',s)[:3])
    if s!=o: open(f,'w',encoding='utf-8').write(s)
open('public/_redirects','w').write('''/avoid-scams.html    /avoid-currency-exchange-scams-krakow    301
/avoid-scams         /avoid-currency-exchange-scams-krakow    301
/before-you-visit.html    /before-you-visit-krakow    301
/before-you-visit         /before-you-visit-krakow    301
''')
print('ok')

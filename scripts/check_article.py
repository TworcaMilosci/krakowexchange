#!/usr/bin/env python3
# Kontrola jakości artykułów bazy wiedzy. Uruchom: python3 scripts/check_article.py
# Każdy artykuł musi przejść wszystkie punkty, zanim trafi do publikacji.
import re,glob,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files=sorted(glob.glob(ROOT+'/src/pages/knowledge-base/*.md')+glob.glob(ROOT+'/src/pages/pl/baza-wiedzy/*.md'))
def url_of(p):
    rel=os.path.relpath(p,ROOT+'/src/pages')[:-3]; return '/'+rel
urls={url_of(p) for p in files}
bad=0
for p in files:
    s=open(p,encoding='utf-8').read(); m=re.match(r'---\n(.*?)\n---\n(.*)',s,re.S); fm,body=m.group(1),m.group(2)
    get=lambda k:(re.search(r'^'+k+r': "?(.*?)"?$',fm,re.M) or [None,None])[1]
    lang=get('lang'); issues=[]
    words=len(re.findall(r'\w+',re.sub(r'[|#*>\-\[\]()]',' ',body)))
    if words<1000: issues.append(f'za krótki: {words} słów (min. 1000)')
    st=get('seoTitle') or ''
    if not (25<=len(st)<=60): issues.append(f'seoTitle ma {len(st)} znaków (25-60)')
    d=get('description') or ''
    if not (110<=len(d)<=160): issues.append(f'description ma {len(d)} znaków (110-160)')
    alt=get('alt')
    if not alt or alt not in urls: issues.append(f'brak wersji w drugim języku: {alt}')
    if len(re.findall(r'^  - q:',fm,re.M))<4: issues.append('mniej niż 4 pytania w faq')
    if len(re.findall(r'^## ',body,re.M))<5: issues.append('mniej niż 5 nagłówków H2')
    links=[l for l in re.findall(r'\]\((/[^)]*)\)',body) if not l.startswith('/images/')]
    if len(links)<4: issues.append(f'tylko {len(links)} linków wewnętrznych (min. 4)')
    if any('.html' in l for l in links): issues.append('link z .html')
    wrong=[l for l in links if (lang=='pl')!=l.startswith('/pl/')]
    if wrong: issues.append(f'link do innej wersji językowej: {wrong[:2]}')
    if 'Floriańska 37' not in body and 'Floriańskiej 37' not in body and 'Floriańską 37' not in body: issues.append('brak adresu Floriańska 37 w treści')
    if 'Exchange Kantor Black Sheep' not in s and 'Floria' not in fm: pass
    if re.search(r'(?<!Exchange )Kantor Black Sheep',body): issues.append('skrócona nazwa firmy (ma być Exchange Kantor Black Sheep)')
    if re.search(r'!\[\s*\]\(',body): issues.append('obrazek bez opisu alt')
    if not re.search(r'^\*\*(W skrócie|In short|Najkrócej)',body,re.M) and not re.search(r'^## (Najkrócej|The short version|A quick checklist|Krótka ściąga)',body,re.M): issues.append('brak krótkiej odpowiedzi/ściągi')
    if '—' in body: issues.append('pauza (—) w treści')
    print(('OK  ' if not issues else 'BŁĄD'),os.path.relpath(p,ROOT+'/src/pages'),f'({words} słów)')
    for i in issues: print('     -',i); bad+=1
sys.exit(1 if bad else 0)

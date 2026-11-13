# Sprawdza linki wewnętrzne w dist/ przy adresach bez .html, przekierowania językowe i błędy JS.
import re,glob,os,asyncio,http.server,threading
from urllib.parse import urljoin,urlparse
D='dist'
def resolve(path):
    p=path.lstrip('/')
    for c in ([p+'index.html'] if p=='' or p.endswith('/') else [p,p+'.html']):
        if os.path.isfile(os.path.join(D,c)): return c
def url_of(rel): return '/'+(rel[:-10] if rel.endswith('index.html') else rel[:-5])
bad=0;n=0
for f in glob.glob(D+'/**/*.html',recursive=True):
    rel=os.path.relpath(f,D); url=url_of(rel); s=open(f,encoding='utf-8').read()
    for h in re.findall(r'(?:href|src)=\\?"([^"\\]+)\\?"',s):
        if h.startswith(('mailto:','tel:','#','data:','//')): continue
        if h.startswith('http'):
            if h.startswith('https://kantorblacksheep.pl'):
                n+=1
                if not resolve(urlparse(h).path) or h.endswith('.html'): bad+=1; print('BAD abs',rel,h)
            continue
        n+=1; t=urlparse(urljoin('https://x'+url,h)).path
        if not resolve(t) or t.endswith('.html'): bad+=1; print('BAD',rel,h,'->',t)
print('links',n,'bad',bad)
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self,path):
        r=resolve(urlparse(path).path); return os.path.join(os.getcwd(),D,r if r else '__404')
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8103),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
from playwright.async_api import async_playwright
async def main():
    errs=0
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for f in sorted(glob.glob(D+'/**/*.html',recursive=True)):
            url=url_of(os.path.relpath(f,D))
            for loc in ('en-US','pl-PL'):
                ctx=await b.new_context(locale=loc); pg=await ctx.new_page(); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
                await pg.route('**/*',lambda r: r.continue_() if '127.0.0.1' in r.request.url else r.abort())
                await pg.goto('http://127.0.0.1:8103'+url); await pg.wait_for_timeout(600)
                final=urlparse(pg.url).path
                if e or not resolve(final): errs+=1; print('ERR',url,loc,final,e[:1])
                elif final!=url: print('  redirect',loc,url,'->',final)
                await ctx.close()
        await b.close()
    print('js/redirect problems',errs)
asyncio.run(main())

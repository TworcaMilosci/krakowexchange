import asyncio,os,http.server,threading,sys
from urllib.parse import urlparse
from playwright.async_api import async_playwright
D='dist'
def resolve(path):
    p=path.lstrip('/')
    for c in ([p+'index.html'] if p=='' or p.endswith('/') else [p,p+'.html']):
        if os.path.isfile(os.path.join(D,c)): return c
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self,path):
        r=resolve(urlparse(path).path); return os.path.join(os.getcwd(),D,r if r else '__404')
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8105),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for name,url,vp in (('kb_m','/pl/baza-wiedzy/kurs-kupna-i-sprzedazy-w-kantorze',{"width":390,"height":1500}),('kb_d','/knowledge-base/buy-rate-vs-sell-rate-kantor',{"width":1280,"height":1100}),('kb_idx','/pl/baza-wiedzy/',{"width":390,"height":700})):
            ctx=await b.new_context(viewport=vp); pg=await ctx.new_page()
            await pg.route('**/*',lambda r: r.continue_() if '127.0.0.1' in r.request.url else r.abort())
            await pg.goto('http://127.0.0.1:8105'+url); await pg.wait_for_timeout(600)
            if name=='kb_d': await pg.evaluate("window.scrollTo(0,1500)"); await pg.wait_for_timeout(200)
            await pg.screenshot(path=f'/tmp/{name}.png'); print(name, await pg.evaluate("document.documentElement.scrollWidth"), vp['width'])
            await ctx.close()
        await b.close()
asyncio.run(main())

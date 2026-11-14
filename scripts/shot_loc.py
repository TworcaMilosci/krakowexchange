import asyncio,os,http.server,threading
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
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8108),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for name,url,w,loc in (('loc_d_en','/',1280,'en-US'),('loc_m_pl','/pl/',390,'pl-PL'),('loc_360','/pl/',360,'pl-PL')):
            ctx=await b.new_context(viewport={"width":w,"height":900},locale=loc); pg=await ctx.new_page(); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
            async def h(r):
                u=r.request.url
                if '/api/rates' in u: return await r.fulfill(body=open('/tmp/api_ok.json').read(),content_type='application/json')
                if '127.0.0.1' in u: return await r.continue_()
                if 'images/' in u or 'fonts/' in u: return await r.abort()
                return await r.abort()
            await pg.route('**/*',h); await pg.goto('http://127.0.0.1:8108'+url); await pg.wait_for_timeout(900)
            await pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')"); await pg.wait_for_timeout(500)
            el=pg.locator('#visit'); await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(500); await el.screenshot(path=f'/tmp/{name}.png')
            sp=pg.locator('#wholesale-block .spread-line'); bb=await sp.bounding_box()
            print(name,'err' if e else 'ok','sw',await pg.evaluate("document.documentElement.scrollWidth"),'spread h',round(bb['height']),'|',await sp.inner_text(),'|',await pg.locator('#wholesale-note').inner_text(),'|',await pg.locator('#board-note').inner_text())
            await ctx.close()
        await b.close()
asyncio.run(main())

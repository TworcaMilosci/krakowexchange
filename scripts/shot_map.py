import asyncio,os,http.server,threading,json
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
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8107),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for name,url,w,api in (('map_pl_m','/pl/',390,'/tmp/api_ok.json'),('map_en_d','/',1280,'/tmp/api_ok.json'),('err_pl','/pl/',390,None)):
            ctx=await b.new_context(viewport={"width":w,"height":900},locale='pl-PL' if 'pl' in name else 'en-US',device_scale_factor=2 if 'map' in name else 1); pg=await ctx.new_page(); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
            async def h(r):
                u=r.request.url
                if '/api/rates' in u: return await (r.fulfill(body=open(api).read(),content_type='application/json') if api else r.fulfill(status=500,body='x'))
                return await (r.continue_() if '127.0.0.1' in u else r.abort())
            await pg.route('**/*',h); await pg.goto('http://127.0.0.1:8107'+url); await pg.wait_for_timeout(900)
            el=pg.locator('#area-map' if 'map' in name else '#wholesale-block'); await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
            await el.screenshot(path=f'/tmp/{name}.png')
            print(name,'err' if e else 'ok','sw',await pg.evaluate("document.documentElement.scrollWidth"),'|',await pg.locator('#board-date').inner_text(),'|',(await pg.locator('#board-body-hurt').inner_text()).replace('\n',' ')[:80])
            if name=='err_pl':
                await pg.fill('#amount','6000'); await pg.wait_for_timeout(100); print('   calc:',await pg.locator('#applied-rate').inner_text(),await pg.locator('#rate-tier').inner_text())
            await ctx.close()
        await b.close()
asyncio.run(main())

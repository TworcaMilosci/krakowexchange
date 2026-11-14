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
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8109),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for url,loc in (('/','en-US'),('/pl/','pl-PL')):
            for w,hh in ((320,700),(360,740),(390,844),(768,1000),(1024,800),(1280,800),(1600,900)):
                ctx=await b.new_context(viewport={"width":w,"height":hh},locale=loc); pg=await ctx.new_page(); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
                async def h(r):
                    u=r.request.url
                    if '/api/rates' in u: return await r.fulfill(body=open('/tmp/api_ok.json').read(),content_type='application/json')
                    return await (r.continue_() if '127.0.0.1' in u else r.abort())
                await pg.route('**/*',h); await pg.goto('http://127.0.0.1:8109'+url); await pg.wait_for_timeout(700)
                sw=await pg.evaluate("document.documentElement.scrollWidth")
                wide=await pg.evaluate("(()=>{const vw=innerWidth;return [...document.querySelectorAll('body *')].filter(x=>{const r=x.getBoundingClientRect();return r.width>0&&r.right>vw+1}).slice(0,3).map(x=>x.tagName+'.'+String(x.className).slice(0,30)+' '+Math.round(x.getBoundingClientRect().right))})()")
                flag='OVERFLOW' if sw>w else 'ok'
                print(url,w,flag,sw,'JSERR' if e else '',wide if sw>w else '', '|', (await pg.locator('.open-now').first.inner_text()) if w==390 else '')
                if (w in (390,1280)):
                    await pg.screenshot(path=f"/tmp/ux_{'pl' if 'pl' in url else 'en'}_{w}.png")
                    if w==390 and 'pl' not in url:
                        el=pg.locator('#about'); await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
                await ctx.close()
        await b.close()
asyncio.run(main())

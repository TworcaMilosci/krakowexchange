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
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8106),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for w in (360,390):
            ctx=await b.new_context(viewport={"width":w,"height":800},locale='pl-PL'); pg=await ctx.new_page()
            async def h(r):
                u=r.request.url
                if '/api/rates' in u: return await r.fulfill(body=open('/tmp/api_day.json').read(),content_type='application/json')
                return await (r.continue_() if '127.0.0.1' in u else r.abort())
            await pg.route('**/*',h); await pg.goto('http://127.0.0.1:8106/pl/'); await pg.wait_for_timeout(900)
            el=pg.locator('#wholesale-block'); await el.scroll_into_view_if_needed()
            box=await el.bounding_box(); await pg.evaluate(f"window.scrollTo(0,{box['y']}+window.scrollY-70)"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'/tmp/board_{w}.png'); print(w,'scrollWidth',await pg.evaluate("document.documentElement.scrollWidth"), await pg.locator('#board-date').inner_text())
            await ctx.close()
        await b.close()
asyncio.run(main())

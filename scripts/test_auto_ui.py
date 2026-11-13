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
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8104),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for case,api in (('day','/tmp/api_day.json'),('manual','/tmp/api_manual.json'),('down',None)):
            for url,loc in (('/pl/','pl-PL'),('/','en-US')):
                ctx=await b.new_context(viewport={"width":390,"height":844},locale=loc); pg=await ctx.new_page(); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
                async def h(r):
                    u=r.request.url
                    if '/api/rates' in u:
                        return await (r.fulfill(body=open(api).read(),content_type='application/json') if api else r.fulfill(status=404,body='x'))
                    return await (r.continue_() if '127.0.0.1' in u else r.abort())
                await pg.route('**/*',h); await pg.goto('http://127.0.0.1:8104'+url); await pg.wait_for_timeout(900)
                rows=await pg.locator('#board-body-hurt tr').all_inner_texts()
                print(case,url,'ERR' if e else '', [' '.join(x.split()) for x in rows], '|', await pg.locator('#spread-wholesale').inner_text(), '|', await pg.locator('#wholesale-note').inner_text(), '| reserve hidden:', await pg.locator('#reserve-row').is_hidden())
                await pg.fill('#amount','6000'); await pg.wait_for_timeout(100); print('   calc 6000:', await pg.locator('#applied-rate').inner_text(), await pg.locator('#rate-tier').inner_text())
                if case=='day' and url=='/pl/':
                    el=pg.locator('#wholesale-block'); await el.scroll_into_view_if_needed(); await el.screenshot(path='/tmp/hurt_auto.png'); print('   wa:',(await pg.locator('#reserve-wa').get_attribute('href'))[:90])
                await ctx.close()
        await b.close()
asyncio.run(main())

# Porównanie piksel po pikselu: stara strona (repo) kontra build Astro.
import asyncio,glob,os,subprocess,sys,time
from playwright.async_api import async_playwright
from PIL import Image,ImageChops
A,B='/home/claude/repo','/home/claude/astro/dist'
async def main():
    sa=subprocess.Popen(['python3','-m','http.server','8101','-d',A],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    sb=subprocess.Popen(['python3','-m','http.server','8102','-d',B],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(1); bad=0
    pages=sorted([os.path.relpath(f,A) for f in glob.glob(A+'/*.html')+glob.glob(A+'/pl/*.html')])
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for rel in pages:
            for vp in ({"width":1280,"height":800},{"width":390,"height":844}):
                shots=[]
                for port in (8101,8102):
                    ctx=await b.new_context(viewport=vp,locale='pl-PL' if rel.startswith('pl/') else 'en-US')
                    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
                    await pg.route('**/*',lambda r: r.continue_() if 'localhost' in r.request.url else r.abort())
                    await pg.goto(f'http://localhost:{port}/{rel}'); await pg.wait_for_timeout(700)
                    fn=f'/tmp/cmp_{port}.png'; await pg.screenshot(path=fn,full_page=True); shots.append(Image.open(fn).convert('RGB'))
                    if errs: print('JSERR',port,rel,errs[:1]); bad+=1
                    await ctx.close()
                same=shots[0].size==shots[1].size and ImageChops.difference(*shots).getbbox() is None
                if not same: bad+=1; print('DIFF',rel,vp['width'],shots[0].size,shots[1].size)
        await b.close()
    sa.kill(); sb.kill(); print('pages',len(pages),'problems',bad)
asyncio.run(main())

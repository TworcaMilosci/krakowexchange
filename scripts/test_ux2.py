import asyncio, json
from playwright.async_api import async_playwright
B='http://localhost:4599'
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for path in ('/','/pl/'):
            for w in (320,360,390,430,768,1024,1280,1600):
                pg=await br.new_page(viewport={'width':w,'height':800}); await pg.goto(B+path); await pg.wait_for_timeout(500)
                sw=await pg.evaluate('document.documentElement.scrollWidth')
                if sw>w: print('OVERFLOW',path,w,sw)
                await pg.close()
            for w,h in ((320,568),(375,667),(390,844),(430,932)):
                pg=await br.new_page(viewport={'width':w,'height':h}); await pg.goto(B+path); await pg.wait_for_timeout(500)
                b=await pg.evaluate('document.querySelector("#top .btn-ghost").getBoundingClientRect().bottom')
                s=await pg.evaluate('(()=>{const r=document.querySelector(".rate-strip");const i=[...r.querySelectorAll(".rs-item")].map(e=>e.scrollWidth>e.clientWidth+1);return i})()')
                print(path,w,h,'cta bottom',round(b),'item overflow',s)
                if w==390:
                    await pg.screenshot(path=f'/tmp/claude-0/-home-claude/852cfe16-0fa9-5eb4-a1a2-59e026524c0e/scratchpad/hero{path.strip("/") or "en"}.png',clip={'x':0,'y':0,'width':390,'height':760})
                    await pg.click('.rs-seg button[data-tier=wholesale]'); 
                    print('  hurt:',await pg.inner_text('#rs-EUR'),'hash',await pg.evaluate('location.hash'))
                    await pg.click('#top .btn-ghost'); await pg.wait_for_timeout(900)
                    y=await pg.evaluate('[document.querySelector("#find").getBoundingClientRect().top, [...document.querySelectorAll("#find a")].filter(a=>/maps/i.test(a.href)).map(a=>Math.round(a.getBoundingClientRect().bottom))]')
                    print('  find top / maps links bottoms',y)
                    await pg.screenshot(path=f'/tmp/claude-0/-home-claude/852cfe16-0fa9-5eb4-a1a2-59e026524c0e/scratchpad/find{path.strip("/") or "en"}.png')
                await pg.close()
        # open-now logic
        pg=await br.new_page(); await pg.goto(B+'/pl/'); await pg.wait_for_timeout(500)
        tests=[('2026-11-13T10:00:00Z',{}),('2026-11-13T20:00:00Z',{}),('2026-11-14T08:00:00Z',{}),('2026-11-14T20:00:00Z',{}),
               ('2026-11-15T12:00:00Z',{'2026-11-15':'12:30-14:30'}),('2026-11-15T11:00:00Z',{'2026-11-15':'12:30-14:30'}),('2026-11-15T14:00:00Z',{'2026-11-15':'12:30-14:30'}),
               ('2026-11-14T20:00:00Z',{'2026-11-15':'12:30-14:30'}),('2026-11-11T10:00:00Z',{}),('2026-11-11T10:00:00Z',{'2026-11-11':'closed'}),('2026-11-10T20:00:00Z',{}),('2026-12-23T20:00:00Z',{'2026-12-24':'9:30-14:00','2026-12-25':'closed','2026-12-26':'closed'}),('2026-12-24T14:00:00Z',{'2026-12-24':'9:30-14:00','2026-12-25':'closed','2026-12-26':'closed'})]
        for t,sp in tests:
            r=await pg.evaluate('([t,sp])=>{DATA.specialHours=sp;const s=openStatus(new Date(t));return JSON.stringify(s)}',[t,sp]); print(t,sp,r)
        await br.close()
asyncio.run(main())

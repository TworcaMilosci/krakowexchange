# Jednorazowa konwersja istniejących stron HTML na strony Astro.
import re,glob,os,sys
R='/home/claude/repo'
for f in sorted(glob.glob(R+'/*.html')+glob.glob(R+'/pl/*.html')):
    rel=os.path.relpath(f,R); s=open(f,encoding='utf-8').read(); up='../' if rel.startswith('pl/') else ''
    base='../' if rel.startswith('pl/') else ''
    # analytics
    s,n=re.subn(r'<!-- Cloudflare Web Analytics -->.*?<!-- End Cloudflare Web Analytics -->','@@ANALYTICS@@',s,flags=re.S); assert n==1,rel
    # geo
    s,n=re.subn(r'<meta name="geo\.region"[^>]*>\s*<meta name="geo\.placename"[^>]*>\s*<meta name="geo\.position"[^>]*>\s*<meta name="ICBM"[^>]*>','@@GEO@@',s); assert n==1,rel
    # logo
    s,n1=re.subn(r'<img src="(?:\.\./)?images/sygnet-96\.png" alt="Exchange Kantor Black Sheep" class="w-10 h-10 rounded-xl" width="40" height="40">\s*<span class="lockup" style="font-size: 0\.62rem;">\s*<span class="top">Exchange</span>\s*<span class="sub"><b>Kantor</b> Black Sheep</span>\s*</span>','@@LOGO_L@@',s)
    s,n2=re.subn(r'<img src="(?:\.\./)?images/sygnet-96\.png" alt="Exchange Kantor Black Sheep" width="40" height="40">\s*<span class="logo-txt">EXCHANGE<small><b>KANTOR</b> BLACK SHEEP</small></span>','@@LOGO_T@@',s)
    assert n1+n2==1,(rel,n1,n2)
    s=re.sub(r'<script(?=[\s>])','<script is:inline',s); s=re.sub(r'<style(?=[\s>])','<style is:inline',s)
    out=re.sub(r'<(script|style)\b.*?</\1>','',s,flags=re.S); assert '{' not in out and '}' not in out,rel
    s=s.replace('@@ANALYTICS@@','<Analytics />').replace('@@GEO@@','<GeoMeta />')
    s=s.replace('@@LOGO_L@@',f'<Logo variant="lockup" base="{base}" />').replace('@@LOGO_T@@',f'<Logo variant="txt" base="{base}" />')
    fm=f"---\nimport Logo from '{up}../components/Logo.astro';\nimport GeoMeta from '{up}../components/GeoMeta.astro';\nimport Analytics from '{up}../components/Analytics.astro';\n---\n"
    dst='src/pages/'+rel[:-5]+'.astro'; open(dst,'w',encoding='utf-8').write(fm+s); print('ok',dst)

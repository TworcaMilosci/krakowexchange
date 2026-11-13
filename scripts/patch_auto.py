import re
NEW_LOAD='''        async function loadRates() {
            // 1) /api/rates: detal ręczny + hurt liczony z rynku (funkcja na hostingu)
            // 2) /rates.json: same kursy ręczne (gdy funkcja nie odpowiada)
            const sources = ["/api/rates?t=" + Date.now(), "/rates.json?t=" + Date.now()];'''
EN={'wholesale_note_auto':'Indicative wholesale rate, calculated from the market rate ({T}). Confirm it at the counter, on WhatsApp or by phone before you come.','reserve_btn':'Reserve this rate','reserve_call':'or call us','reserve_msg':'Hello, I would like to reserve the wholesale rate. Currency and amount: '}
PL={'wholesale_note_auto':'Kurs hurtowy orientacyjny, liczony z kursu rynkowego ({T}). Potwierdź go w okienku, na WhatsAppie lub telefonicznie przed przyjściem.','reserve_btn':'Zarezerwuj kurs','reserve_call':'lub zadzwoń','reserve_msg':'Dzień dobry, chcę zarezerwować kurs hurtowy. Waluta i kwota: '}
def dict_add(d): return ' '+' '.join(f'{k}: "{v}",' for k,v in d.items())
for f,lang in (('src/pages/index.astro','en'),('src/pages/pl/index.astro','pl')):
    s=open(f,encoding='utf-8').read()
    s,n=re.subn(r'        async function loadRates\(\) \{\n            const sources = \[\n.*?\n            \];',lambda m:NEW_LOAD,s,flags=re.S); assert n==1
    for key,d in (('wholesale_note: "The wholesale table',EN),('wholesale_note: "Kursy w tabeli',PL)):
        assert s.count(key)==1; s=s.replace(key,dict_add(d).strip()+'\n                '+key)
    T=PL if lang=='pl' else EN
    old=re.search(r'(<p id="wholesale-note"[^>]*>.*?</p>)',s,re.S); assert old
    btn='''\n                        <p id="reserve-row" class="px-6 pb-4" hidden><a id="reserve-wa" href="https://wa.me/48889505057" target="_blank" rel="noopener" style="display:inline-block;border:1px solid #fff;border-radius:999px;padding:.6rem 1.15rem;font-size:.72rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#fff" data-i18n="reserve_btn">'''+T['reserve_btn']+'''</a> <a href="tel:+48889505057" style="margin-left:.75rem;font-size:.8rem;text-decoration:underline;color:#d4d4d4" data-i18n="reserve_call">'''+T['reserve_call']+'''</a></p>'''
    s=s[:old.end()]+btn+s[old.end():]
    a='document.getElementById("wholesale-note").textContent = t.wholesale_note.replace("{X}", DATA.wholesaleFrom || "");'
    assert s.count(a)==1
    s=s.replace(a,'''const auto = DATA.wholesaleAutoInfo && DATA.wholesaleAutoInfo.mode !== "manual" ? DATA.wholesaleAutoInfo : null;
            let noteText = t.wholesale_note.replace("{X}", DATA.wholesaleFrom || "");
            if (auto) {
                let when = "";
                const q = new Date(auto.quoteTime);
                if (auto.source === "nbp") when = "NBP " + auto.quoteTime;
                else if (!isNaN(q)) when = q.toLocaleTimeString(currentLang === "pl" ? "pl-PL" : "en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Warsaw" });
                noteText = t.wholesale_note_auto.replace("{T}", when);
            }
            document.getElementById("wholesale-note").textContent = noteText;
            document.getElementById("reserve-row").hidden = !auto;
            document.getElementById("reserve-wa").href = "https://wa.me/48889505057?text=" + encodeURIComponent(t.reserve_msg);''')
    open(f,'w',encoding='utf-8').write(s)
print('patched')

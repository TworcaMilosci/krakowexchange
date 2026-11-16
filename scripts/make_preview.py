#!/usr/bin/env python3
"""Tworzy samodzielne pliki HTML do podglądu (style, czcionki i obrazki wbudowane w plik).
Użycie: python3 scripts/make_preview.py <katalog_dist> <katalog_wyjściowy> <ścieżka strony> [kolejne...]
Przykład ścieżki: pl/baza-wiedzy/kantor-krakow-gdzie-wymienic-walute"""
import sys, re, os, base64, mimetypes
dist, out, pages = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(out, exist_ok=True)
def data_uri(path):
    if not os.path.isfile(path) or os.path.getsize(path) > 600_000: return None
    mt = mimetypes.guess_type(path)[0] or ('font/woff2' if path.endswith('.woff2') else 'application/octet-stream')
    return f"data:{mt};base64," + base64.b64encode(open(path, 'rb').read()).decode()
def local(url, base):
    url = url.split('#')[0].split('?')[0]
    return os.path.join(dist, url.lstrip('/')) if url.startswith('/') else os.path.normpath(os.path.join(base, url))
def inline_css(css, base):
    def r(m):
        u = m.group(1).strip('\'"')
        if u.startswith(('data:', 'http')): return m.group(0)
        d = data_uri(local(u, base)); return f"url({d})" if d else m.group(0)
    return re.sub(r'url\(([^)]+)\)', r, css)
for page in pages:
    src = os.path.join(dist, page + '.html')
    if not os.path.isfile(src): src = os.path.join(dist, page, 'index.html')
    html = open(src, encoding='utf-8').read(); base = os.path.dirname(src)
    def css(m):
        p = local(m.group(1), base)
        return '<style>' + inline_css(open(p, encoding='utf-8').read(), os.path.dirname(p)) + '</style>' if os.path.isfile(p) else m.group(0)
    html = re.sub(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>', css, html)
    html = re.sub(r'<link[^>]+href="([^"]+)"[^>]+rel="stylesheet"[^>]*>', css, html)
    def img(m):
        d = data_uri(local(m.group(2), base)); return m.group(1) + d + m.group(3) if d else m.group(0)
    html = re.sub(r'(<img[^>]+src=")([^"]+)(")', img, html)
    html = re.sub(r'\ssrcset="[^"]*"', '', html)
    html = html.replace('<body', '<body data-preview="1"', 1)
    html = re.sub(r'(<body[^>]*>)', r'\1<div style="background:#b45309;color:#fff;font:600 13px/1.4 system-ui;padding:8px 14px;text-align:center">PODGLĄD przed publikacją. Linki do innych stron mogą tu nie działać.</div>', html, count=1)
    name = page.strip('/').replace('/', '__') + '.html'
    open(os.path.join(out, name), 'w', encoding='utf-8').write(html); print(name, os.path.getsize(os.path.join(out, name)) // 1024, 'KB')

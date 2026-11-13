# Exchange Kantor Black Sheep: strona www (Astro)

Źródła strony https://kantorblacksheep.pl. Strona jest statyczna, budowana przez Astro.

## Struktura

- `src/pages/` strony (EN w katalogu głównym, PL w `pl/`). Adresy kończą się na `.html`, tak jak przed migracją.
- `src/components/` wspólne elementy: `Logo.astro` (nagłówek), `GeoMeta.astro`, `Analytics.astro`.
- `src/data/site.js` dane firmy (nazwa, adres, telefon, współrzędne). Zmiana tutaj zmienia wszystkie strony.
- `public/` pliki kopiowane bez zmian: `styles.css`, `rates.json`, `images/`, `fonts/`, `robots.txt`, `llms.txt`, `sitemap.xml`, `_redirects`.
- `scripts/` narzędzia pomocnicze (konwersja, porównanie wyglądu).
- `docs/` instrukcje.

## Kursy

Kursy edytuje się w `public/rates.json` (patrz `docs/INSTRUKCJA-KURSY.md`).

## Budowanie

    npm install
    npm run build     # wynik w dist/
    npm run dev       # podgląd lokalny

## Zasady treści

- Nazwa firmy zawsze: Exchange Kantor Black Sheep.
- Każda strona ma wersję PL i EN, powiązane znacznikami hreflang.
- Nowe strony i artykuły: pełna optymalizacja SEO i GEO (dane strukturalne, alty, linkowanie wewnętrzne).

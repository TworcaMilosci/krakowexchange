# Jak zmienić kursy walut

Edytujesz **wyłącznie plik `rates.json`**. Nie dotykasz `index.html`.

## Krok po kroku (GitHub w przeglądarce lub aplikacji)

1. Otwórz repozytorium → plik **rates.json** → ikona ołówka (Edit).
2. Zmień liczby. Znaczenie pól:
   - `buy` = skup detal (kupujemy od klienta)
   - `sell` = sprzedaż detal (sprzedajemy klientowi)
   - `buyHurt` / `sellHurt` = kursy hurtowe (opcjonalne)
   - `wholesaleFrom` = od jakiej kwoty obowiązuje hurt (tekst wyświetlany, np. "1 000 EUR")
   - `wholesaleMinAmount` = próg liczbowy dla kalkulatora (np. 1000) — od tej kwoty
     kalkulator sam przelicza po kursie hurtowym
   - `alsoBuy` = lista walut skupowanych po wcześniejszym kontakcie
3. Zmień datę w polu `"updated"` — wyświetla się na tablicy jako "Aktualizacja".
4. Kliknij **Commit changes**. Netlify sam opublikuje stronę w ~1 minutę.

## Zasady zapisu (ważne!)

- Kropka dziesiętna, **nie przecinek**: `4.49` ✓ — `4,49` ✗
- Przecinek na końcu każdej linii **oprócz ostatniej** w bloku.
- Nie kasuj cudzysłowów ani nawiasów.

## Wzór poprawnego pliku

```json
{
  "updated": "2026-08-24",
  "wholesaleFrom": "1 000 EUR",
  "wholesaleMinAmount": 1000,
  "rates": {
    "EUR": { "buy": 4.49, "sell": 4.52, "buyHurt": 4.50, "sellHurt": 4.51 },
    "USD": { "buy": 3.78, "sell": 3.92, "buyHurt": 3.82, "sellHurt": 3.88 },
    "GBP": { "buy": 5.31, "sell": 5.55, "buyHurt": 5.38, "sellHurt": 5.48 }
  },
  "alsoBuy": ["CHF", "CAD", "AUD", "DKK", "SEK", "NOK", "CZK", "HUF", "JPY", "AED"]
}
```

## Warianty

- **Bez hurtu:** usuń `buyHurt` i `sellHurt` ze wszystkich walut — przełącznik
  Detal/Hurt sam zniknie ze strony.
- **Dodanie waluty do tablicy głównej:** dodaj linię w `rates`.
- **Dodanie waluty do "Skupujemy również":** dopisz kod do listy `alsoBuy`.
  Flagi działają automatycznie dla: EUR, USD, GBP, CHF, CAD, AUD, DKK, SEK,
  NOK, CZK, HUF, JPY, AED.

## Gdyby strona przestała pokazywać kursy

Najczęstsza przyczyna: literówka w `rates.json` (przecinek zamiast kropki,
brakujący cudzysłów). Wejdź na https://jsonlint.com, wklej zawartość pliku —
pokaże, w której linii jest błąd. Strona ma wbudowane kursy awaryjne, więc
nigdy nie pokaże pustej tabeli.

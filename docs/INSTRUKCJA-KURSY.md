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
   - `alsoBuy` = lista pozostałych walut, które skupujemy i sprzedajemy (kurs podajemy na miejscu lub telefonicznie)
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
- **Dodanie waluty do "Skupujemy i sprzedajemy również":** dopisz kod do listy `alsoBuy`.
  Flagi działają automatycznie dla: EUR, USD, GBP, CHF, CAD, AUD, DKK, SEK,
  NOK, CZK, HUF, JPY, AED.

## Gdyby strona przestała pokazywać kursy

Najczęstsza przyczyna: literówka w `rates.json` (przecinek zamiast kropki,
brakujący cudzysłów). Wejdź na https://jsonlint.com, wklej zawartość pliku —
pokaże, w której linii jest błąd. Strona ma wbudowane kursy awaryjne, więc
nigdy nie pokaże pustej tabeli.

---

## Kursy hurtowe liczone z rynku (od wersji Astro / Cloudflare)

Plik kursów to teraz `public/rates.json`. Kursy **detaliczne** (`buy`, `sell`) wpisujesz ręcznie jak dotąd.

Kursy **hurtowe** strona liczy sama z kursu rynkowego (funkcja `functions/api/rates.js`):

| | Skup EUR, USD | Skup GBP | Sprzedaż |
|---|---|---|---|
| Dni robocze 9:00-17:00 (kurs na żywo) | rynek -2 gr | rynek -2,9 gr | rynek +0,5 gr |
| Wieczór, weekend, święta, brak kursu na żywo | rynek -3 gr | rynek -3,9 gr | rynek +1 gr |

Marże i godziny zmienisz w `rates.json`, w polu `wholesaleAuto`.

Zabezpieczenia:
- `"wholesaleAuto": { "enabled": false }` wyłącza automat: strona pokazuje ręczne `buyHurt` i `sellHurt`.
- Jeśli kurs rynkowy wypada poza Twoje kursy detaliczne (kupno-sprzedaż), strona uznaje dane za nieaktualne i pokazuje ręczne kursy hurtowe. Dlatego detal trzeba aktualizować.
- Jeśli źródło kursów nie odpowiada, strona pokazuje ręczne kursy hurtowe.

Źródła kursu rynkowego: Wise (kurs środkowy rynku na żywo; wymaga zmiennej `WISE_TOKEN` w Cloudflare Pages: Settings, Variables and Secrets), zapasowo NBP (jeden kurs dziennie; wtedy zawsze obowiązują szersze marże). Kursy hurtowe są zaokrąglane do 3 miejsc po przecinku.

Podgląd tego, co strona policzyła: adres `/api/rates` (pole `wholesaleAutoInfo` mówi, z jakiego źródła i w jakim trybie).

---

## Godziny otwarcia: wyjątki na konkretne dni

Znacznik "Otwarte teraz" na stronie liczy się ze stałych godzin (pon.-pt. 9:30-20:30, sob. 10:00-20:30, niedziela zamknięte).
Gdy danego dnia masz wolne albo inne godziny, dopisz ten dzień w `public/rates.json` w polu `specialHours`:

    "specialHours": {
      "2026-11-15": "12:30-14:30",
      "2026-12-24": "9:30-14:00",
      "2026-12-25": "closed"
    }

- Data w formacie RRRR-MM-DD, godziny jako OD-DO, a dzień wolny jako "closed".
- Wpis dotyczy tylko tej jednej daty; w pozostałe dni obowiązują stałe godziny.
- W polskie święta bez wpisu strona pokazuje "sprawdź godziny w Mapach Google". Jeśli w święto pracujesz, dopisz godziny; jeśli nie, dopisz "closed", wtedy strona policzy czas do następnego otwarcia.
- Stare daty można usuwać, ale nie trzeba.
- Pamiętaj o przecinkach między wpisami (po ostatnim bez przecinka).

---

## Kursy detaliczne prosto z programu KANTOR

Od listopada 2026 kursy detaliczne (EUR, USD, GBP) mogą trafiać na stronę automatycznie z programu KANTOR na komputerze w kantorze.

Jak to działa:

1. Program KANTOR zapisuje tabelę kursów, a skrypt tablicy (`C:\Tablica\kursy-watcher.ps1`) tworzy z niej plik `C:\Tablica\kursy.js`.
2. Drugi skrypt, `C:\Tablica\kursy-www.ps1`, po każdej zmianie wysyła ten plik na adres `https://kantorblacksheep.pl/api/push-rates`, podpisany kluczem z pliku `C:\Tablica\www-klucz.txt`.
3. Strona sprawdza kursy i zapisuje je w pamięci Cloudflare (KV). Zmiana jest widoczna po kilku sekundach, bez budowania strony.
4. Kursy hurtowe dalej liczą się same z kursu rynkowego, w granicach nowych kursów detalicznych.

Zabezpieczenia: strona odrzuca kursy, gdy kupno nie jest niższe od sprzedaży, gdy różnica przekracza 40 groszy, gdy kurs odbiega od rynkowego o ponad 4% albo gdy brakuje którejś z trzech walut. Po odrzuceniu na stronie zostają poprzednie kursy, a powód jest zapisany w `C:\Tablica\kursy-www.log`.

Gdy komputer w kantorze jest wyłączony, strona pokazuje ostatnie przysłane kursy.

Plik `public/rates.json` zostaje jako:

- rezerwa: jego kursy detaliczne są używane, dopóki z kantoru nic nie przyszło;
- miejsce na `specialHours`, `wholesaleFrom` i ustawienia hurtu;
- wyłącznik: dopisanie `"retailFromKantor": { "enabled": false },` wraca do kursów wpisanych ręcznie w tym pliku.

Ustawienia po stronie Cloudflare (projekt Pages `krakowexchange`): powiązanie KV o nazwie `RATES_KV` oraz sekret `RATES_PUSH_KEY` (ten sam klucz co w `www-klucz.txt`).

Jak sprawdzić, skąd strona bierze kursy: otwórz `https://kantorblacksheep.pl/api/rates` i znajdź `retailInfo`. `"source": "kantor"` oznacza kursy z programu, `"source": "file"` kursy z `rates.json` (obok jest powód).

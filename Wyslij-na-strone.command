#!/bin/bash
# Dwuklik wysyła zatwierdzone zmiany strony na GitHuba (a stamtąd na hosting).
cd "$(dirname "$0")" || exit 1
echo "Wysyłam zmiany strony Exchange Kantor Black Sheep..."
echo
if ! command -v git >/dev/null 2>&1; then
  echo "Na tym Macu nie ma jeszcze programu git."
  echo "Pojawi się okno instalacji narzędzi Apple: kliknij Zainstaluj, a potem uruchom ten plik ponownie."
  xcode-select --install 2>/dev/null
else
  # najpierw pobierz zmiany zrobione na GitHubie (np. kursy), potem wyślij
  git pull --rebase --autostash origin "$(git rev-parse --abbrev-ref HEAD)" 2>&1 | sed 's/github_pat_[A-Za-z0-9_]*/***/g'
  git push -u origin HEAD 2>&1 | sed 's/github_pat_[A-Za-z0-9_]*/***/g'
  if [ "${PIPESTATUS[0]}" -eq 0 ]; then echo; echo "GOTOWE. Zmiany wysłane."; else echo; echo "NIE UDAŁO SIĘ. Zrób zrzut tego okna i wyślij Claude'owi."; fi
fi
echo
read -n 1 -s -r -p "Naciśnij dowolny klawisz, aby zamknąć okno."

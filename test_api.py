# Test: Welche Saisons liefert die football-data.org API mit eurem Gratis-Token?
# Ausfuehren: python test_api.py   (vorher: pip install requests)

import time
import requests

from pathlib import Path

# Token aus der Datei token.txt lesen (diese Datei wird NICHT auf GitHub hochgeladen)
try:
    TOKEN = Path("token.txt").read_text(encoding="utf-8").strip()
except FileNotFoundError:
    raise SystemExit("token.txt fehlt! Lege im Projektordner eine Datei token.txt an "
                     "und schreibe nur deinen football-data.org Token hinein.")

LIGEN = {"PL": "Premier League", "BL1": "Bundesliga", "PD": "La Liga"}
SAISONS = [2022, 2023, 2024, 2025]       # 2022 = Saison 2022/23 usw.

headers = {"X-Auth-Token": TOKEN}

for code, name in LIGEN.items():
    for saison in SAISONS:
        url = f"https://api.football-data.org/v4/competitions/{code}/matches"
        r = requests.get(url, headers=headers, params={"season": saison})

        if r.status_code == 200:
            spiele = r.json().get("matches", [])
            print(f"OK    {name:15} {saison}/{saison + 1 - 2000}: {len(spiele)} Spiele")
            if spiele:
                s = spiele[0]
                print(f"      Beispiel: {s['utcDate']}  {s['homeTeam']['name']} - "
                      f"{s['awayTeam']['name']}  {s['score']['fullTime']}  "
                      f"Stadion: {s.get('venue')}")
        elif r.status_code == 403:
            print(f"NEIN  {name:15} {saison}/{saison + 1 - 2000}: nicht im Gratis-Tarif")
        else:
            print(f"FEHLER {name:15} {saison}: Status {r.status_code} - {r.text[:100]}")

        time.sleep(7)   # Gratis-Tarif erlaubt max. 10 Anfragen pro Minute

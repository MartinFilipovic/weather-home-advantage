# 01_spiele_sammeln.py
# Holt alle Spiele (Premier League, Bundesliga, La Liga) der Saisons 2023/24-2025/26
# von der football-data.org API und speichert sie als CSV-Datei.
#
# Vorher einmal im Terminal:  pip install requests pandas
# Starten:                    python 01_spiele_sammeln.py

import os
import time
import requests
import pandas as pd

from pathlib import Path

# Token aus der Datei token.txt lesen (diese Datei wird NICHT auf GitHub hochgeladen)
try:
    TOKEN = Path("token.txt").read_text(encoding="utf-8").strip()
except FileNotFoundError:
    raise SystemExit("token.txt fehlt! Lege im Projektordner eine Datei token.txt an "
                     "und schreibe nur deinen football-data.org Token hinein.")

LIGEN = {"PL": "Premier League", "BL1": "Bundesliga", "PD": "La Liga"}
SAISONS = [2023, 2024, 2025]                  # 2023 = Saison 2023/24 usw.

headers = {"X-Auth-Token": TOKEN}
alle_spiele = []

for code, liga in LIGEN.items():
    for saison in SAISONS:
        saison_label = f"{saison}/{saison + 1 - 2000}"
        url = f"https://api.football-data.org/v4/competitions/{code}/matches"
        r = requests.get(url, headers=headers, params={"season": saison})

        if r.status_code != 200:
            print(f"FEHLER {liga} {saison_label}: Status {r.status_code}")
            time.sleep(7)
            continue

        spiele = r.json().get("matches", [])
        print(f"OK  {liga:15} {saison_label}: {len(spiele)} Spiele")

        for s in spiele:
            tore_heim = s["score"]["fullTime"]["home"]
            tore_gast = s["score"]["fullTime"]["away"]
            sieger = s["score"]["winner"]        # HOME_TEAM / AWAY_TEAM / DRAW

            if sieger == "HOME_TEAM":
                resultat = "H"                   # Heimsieg
            elif sieger == "AWAY_TEAM":
                resultat = "A"                   # Auswaertssieg
            elif sieger == "DRAW":
                resultat = "D"                   # Unentschieden
            else:
                resultat = None                  # Spiel nicht beendet

            alle_spiele.append({
                "match_id": s["id"],
                "liga": liga,
                "saison": saison_label,
                "spieltag": s.get("matchday"),
                "anstoss_utc": s["utcDate"],
                "status": s["status"],
                "heim_id": s["homeTeam"]["id"],
                "heim_team": s["homeTeam"]["name"],
                "gast_id": s["awayTeam"]["id"],
                "gast_team": s["awayTeam"]["name"],
                "tore_heim": tore_heim,
                "tore_gast": tore_gast,
                "resultat": resultat,
            })

        time.sleep(7)   # Gratis-Tarif: max. 10 Anfragen pro Minute

# Als Tabelle speichern
df = pd.DataFrame(alle_spiele)
os.makedirs("data", exist_ok=True)
df.to_csv("data/spiele_roh.csv", index=False, encoding="utf-8")

# Kurze Kontrolle
print("\n--- Zusammenfassung ---")
print(f"Spiele total: {len(df)}")
print(df.groupby(["liga", "saison"]).size())
print("\nStatus der Spiele (sollte ueberall FINISHED sein):")
print(df["status"].value_counts())
print("\nGespeichert in: data/spiele_roh.csv")

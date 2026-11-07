# 02_teams_liste.py
# Liest data/spiele_roh.csv und erstellt eine Liste aller Heimteams pro Liga.
# Diese Liste brauchen wir, um jedem Team sein Stadion zuzuordnen.
#
# Starten: python 02_teams_liste.py

import pandas as pd

df = pd.read_csv("data/spiele_roh.csv")

# 1) Das Spiel mit Status AWARDED anzeigen (am gruenen Tisch entschieden)
print("--- Spiele, die nicht normal beendet wurden ---")
print(df[df["status"] != "FINISHED"][["liga", "saison", "anstoss_utc",
                                      "heim_team", "gast_team", "status"]])

# 2) Alle Heimteams mit Liga und Anzahl Heimspiele
teams = (df.groupby(["liga", "heim_id", "heim_team"])
           .agg(heimspiele=("match_id", "count"),
                saisons=("saison", lambda s: ", ".join(sorted(s.unique()))))
           .reset_index()
           .sort_values(["liga", "heim_team"]))

teams.to_csv("data/teams.csv", index=False, encoding="utf-8")

pd.set_option("display.max_rows", 200)
pd.set_option("display.width", 200)
print(f"\n--- {len(teams)} Teams gefunden ---")
print(teams.to_string(index=False))
print("\nGespeichert in: data/teams.csv")

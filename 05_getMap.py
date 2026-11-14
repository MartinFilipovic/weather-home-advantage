"""
Stadien-Mapping-Skript
Liest die Koordinaten-CSV ein, extrahiert eindeutige Stadien/Heimteams pro Liga 
und generiert eine interaktive HTML-Karte (Folium) mit farbcodierten Markern 
und einer Legende.
"""

import os
import folium
import pandas as pd

# Pfad zur Datei mit den Koordinaten
input_file = "data/spiele_roh_with_coords.csv"
output_file = "data/staedte_karte.html"

if not os.path.exists(input_file):
  raise SystemExit(
      f"Fehler: Die Datei '{input_file}' wurde nicht gefunden! Bitte stellen"
      " Sie sicher, dass 03_getCoordinates.py bereits ausgeführt wurde."
  )

# Daten einlesen
print(f"Lade Daten aus {input_file}...")
df = pd.read_csv(input_file)

# Prüfen, ob Koordinaten-Spalten vorhanden sind
if "latitude" not in df.columns or "longitude" not in df.columns:
  raise SystemExit(
      "Die Spalten 'latitude' und 'longitude' fehlen in der CSV-Datei!"
  )

# Eindeutige Teams / Stadien pro Liga extrahieren
df_teams = (
    df[["liga", "heim_id", "heim_team", "latitude", "longitude"]]
    .dropna(subset=["latitude", "longitude"])
    .drop_duplicates(subset=["heim_id"])
    .reset_index(drop=True)
)

print(f"{len(df_teams)} Stadien/Teams mit gültigen Koordinaten gefunden.")

# Zentrum der Karte berechnen
center_lat = df_teams["latitude"].mean()
center_lon = df_teams["longitude"].mean()

# HINWEIS: 'OpenStreetMap' benötigt keinen API-Key und ist komplett frei
m = folium.Map(
    location=[center_lat, center_lon], zoom_start=5, tiles="OpenStreetMap"
)


# Farben für die verschiedenen Ligen definieren
def get_league_color(liga):
  colors = {
      "Premier League": "blue",
      "Bundesliga": "red",
      "La Liga": "orange",
  }
  return colors.get(liga, "green")


# Marker für jedes Stadion zur Karte hinzufügen
for _, row in df_teams.iterrows():
  liga = row.get("liga", "Unbekannt")
  team = row["heim_team"]
  lat = row["latitude"]
  lon = row["longitude"]
  color = get_league_color(liga)

  popup_html = f"""
    <div style="font-family: Arial; font-size: 12px; width: 200px;">
        <b>{team}</b><br>
        <b>Liga:</b> {liga}<br>
        <b>Koordinaten:</b> {lat:.4f}, {lon:.4f}
    </div>
    """

  folium.Marker(
      location=[lat, lon],
      popup=folium.Popup(popup_html, max_width=250),
      tooltip=f"{team} ({liga})",
      icon=folium.Icon(color=color, icon="futbol", prefix="fa"),
  ).add_to(m)

# Legende in der Ecke hinzufügen
legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px; height: 110px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px;">
      <b>Ligen-Legende</b><br>
      <i class="fa fa-map-marker" style="color:blue"></i> Premier League<br>
      <i class="fa fa-map-marker" style="color:red"></i> Bundesliga<br>
      <i class="fa fa-map-marker" style="color:orange"></i> La Liga
    </div>
    """
m.get_root().html.add_child(folium.Element(legend_html))

# Karte speichern
os.makedirs("data", exist_ok=True)
m.save(output_file)
print(f"Erfolgreich! Die interaktive Karte wurde unter '{output_file}' gespeichert.")

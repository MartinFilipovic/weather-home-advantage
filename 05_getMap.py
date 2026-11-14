"""
Stadium Mapping Script
Reads the coordinate CSV, extracts unique stadiums/home teams per league, 
and generates an interactive HTML map (Folium) with color-coded markers 
and a legend.
"""

import os
import folium
import pandas as pd

# Path to the file containing coordinates
input_file = "data/spiele_roh_with_coords.csv"
output_file = "data/staedte_karte.html"

if not os.path.exists(input_file):
  raise SystemExit(
      f"Fehler: Die Datei '{input_file}' wurde nicht gefunden! Bitte stellen"
      " Sie sicher, dass 03_getCoordinates.py bereits ausgeführt wurde."
  )

# Load data
print(f"Lade Daten aus {input_file}...")
df = pd.read_csv(input_file)

# Check if coordinate columns are present
if "latitude" not in df.columns or "longitude" not in df.columns:
  raise SystemExit(
      "Die Spalten 'latitude' und 'longitude' fehlen in der CSV-Datei!"
  )

# Extract unique teams / stadiums per league
df_teams = (
    df[["liga", "heim_id", "heim_team", "latitude", "longitude"]]
    .dropna(subset=["latitude", "longitude"])
    .drop_duplicates(subset=["heim_id"])
    .reset_index(drop=True)
)

print(f"{len(df_teams)} Stadien/Teams mit gültigen Koordinaten gefunden.")

# Calculate the center of the map
center_lat = df_teams["latitude"].mean()
center_lon = df_teams["longitude"].mean()

# NOTE: 'OpenStreetMap' requires no API key and is completely free
m = folium.Map(
    location=[center_lat, center_lon], zoom_start=5, tiles="OpenStreetMap"
)


# Define colors for the different leagues
def get_league_color(liga):
  colors = {
      "Premier League": "blue",
      "Bundesliga": "red",
      "La Liga": "orange",
  }
  return colors.get(liga, "green")


# Add a marker for each stadium to the map
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

# Add legend in the corner
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

# Save the map
os.makedirs("data", exist_ok=True)
m.save(output_file)
print(f"Erfolgreich! Die interaktive Karte wurde unter '{output_file}' gespeichert.")

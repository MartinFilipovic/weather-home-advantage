import time
import pandas as pd
import requests

# Input and output file paths
input_file = "data/spiele_roh_with_coords.csv"
output_file = "data/spiele_roh_with_weather.csv"

# Load dataset
df = pd.read_csv(input_file)

# Initialize weather metrics columns if not present
weather_columns = [
    "regen_summe",
    "temperatur_mittel",
    "wind_mittel",
    "snowfall_summe",
    "cloud_cover_mittel",
    "apparent_temp_mittel",
    "humidity_mittel",
    "surface_pressure_mittel",
    "pressure_msl_mittel",
    "wind_gusts_mittel",
]

for col in weather_columns:
  if col not in df.columns:
    df[col] = None

base_url = "https://archive-api.open-meteo.com/v1/archive"

# Selected hourly weather variables requested
hourly_vars = (
    "temperature_2m,rain,snowfall,weather_code,wind_speed_10m,cloud_cover,"
    "apparent_temperature,relative_humidity_2m,surface_pressure,pressure_msl,"
    "wind_gusts_10m"
)

print(
    f"Starting weather data retrieval for {len(df)} matches (Kickoff to +2h"
    " window)...\n"
)

# Iterate through each game record
for idx, row in df.iterrows():
  match_id = row.get("match_id", idx + 1)
  lat = row.get("latitude")
  lon = row.get("longitude")
  anstoss_utc = row.get("anstoss_utc")
  heim_team = row.get("heim_team", "Unknown")

  if pd.isna(lat) or pd.isna(lon) or pd.isna(anstoss_utc):
    print(
        f"✖ [Record {idx+1}/{len(df)}] Match ID: {match_id} -> Missing"
        " coordinates or kickoff time."
    )
    continue

  # Parse kickoff date and hour from UTC string (e.g., '2023-08-11T19:00:00Z')
  date_str = anstoss_utc[:10]  # 'YYYY-MM-DD'
  kickoff_hour = int(anstoss_utc[11:13])  # Hour (0-23)

  params = {
      "latitude": lat,
      "longitude": lon,
      "start_date": date_str,
      "end_date": date_str,
      "hourly": hourly_vars,
  }

  try:
    response = requests.get(base_url, params=params, timeout=15)
    if response.status_code == 200:
      data = response.json()
      hourly = data.get("hourly", {})
      times = hourly.get("time", [])

      # Extract arrays for each variable
      temps = hourly.get("temperature_2m", [])
      rains = hourly.get("rain", [])
      snows = hourly.get("snowfall", [])
      winds = hourly.get("wind_speed_10m", [])
      clouds = hourly.get("cloud_cover", [])
      app_temps = hourly.get("apparent_temperature", [])
      humidity = hourly.get("relative_humidity_2m", [])
      surf_pressure = hourly.get("surface_pressure", [])
      msl_pressure = hourly.get("pressure_msl", [])
      gusts = hourly.get("wind_gusts_10m", [])

      # Game window: kickoff_hour, kickoff_hour + 1, kickoff_hour + 2 (3 hours spanning 2h match duration)
      w_temps, w_rains, w_snows, w_winds, w_clouds = [], [], [], [], []
      w_app_temps, w_humidity, w_surf_pres, w_msl_pres, w_gusts = (
          [],
          [],
          [],
          [],
          [],
      )

      for h in range(kickoff_hour, kickoff_hour + 3):
        if h < len(times):
          if h < len(temps) and temps[h] is not None:
            w_temps.append(temps[h])
          if h < len(rains) and rains[h] is not None:
            w_rains.append(rains[h])
          if h < len(snows) and snows[h] is not None:
            w_snows.append(snows[h])
          if h < len(winds) and winds[h] is not None:
            w_winds.append(winds[h])
          if h < len(clouds) and clouds[h] is not None:
            w_clouds.append(clouds[h])
          if h < len(app_temps) and app_temps[h] is not None:
            w_app_temps.append(app_temps[h])
          if h < len(humidity) and humidity[h] is not None:
            w_humidity.append(humidity[h])
          if h < len(surf_pressure) and surf_pressure[h] is not None:
            w_surf_pres.append(surf_pressure[h])
          if h < len(msl_pressure) and msl_pressure[h] is not None:
            w_msl_pres.append(msl_pressure[h])
          if h < len(gusts) and gusts[h] is not None:
            w_gusts.append(gusts[h])

      # Calculate aggregates (Sums for precipitation/snow, Means for temperatures, wind, pressure, etc.)
      df.at[idx, "regen_summe"] = (
          round(sum(w_rains), 2) if w_rains else None
      )
      df.at[idx, "temperatur_mittel"] = (
          round(sum(w_temps) / len(w_temps), 2) if w_temps else None
      )
      df.at[idx, "wind_mittel"] = (
          round(sum(w_winds) / len(w_winds), 2) if w_winds else None
      )
      df.at[idx, "snowfall_summe"] = (
          round(sum(w_snows), 2) if w_snows else None
      )
      df.at[idx, "cloud_cover_mittel"] = (
          round(sum(w_clouds) / len(w_clouds), 2) if w_clouds else None
      )
      df.at[idx, "apparent_temp_mittel"] = (
          round(sum(w_app_temps) / len(w_app_temps), 2) if w_app_temps else None
      )
      df.at[idx, "humidity_mittel"] = (
          round(sum(w_humidity) / len(w_humidity), 2) if w_humidity else None
      )
      df.at[idx, "surface_pressure_mittel"] = (
          round(sum(w_surf_pres) / len(w_surf_pres), 2)
          if w_surf_pres
          else None
      )
      df.at[idx, "pressure_msl_mittel"] = (
          round(sum(w_msl_pres) / len(w_msl_pres), 2) if w_msl_pres else None
      )
      df.at[idx, "wind_gusts_mittel"] = (
          round(sum(w_gusts) / len(w_gusts), 2) if w_gusts else None
      )

      print(
          f"✔ [Record {idx+1}/{len(df)}] Match ID: {match_id} ({heim_team} |"
          f" {date_str} {kickoff_hour}:00 UTC) -> Temp:"
          f" {df.at[idx, 'temperatur_mittel']}°C, Rain:"
          f" {df.at[idx, 'regen_summe']}mm, Wind:"
          f" {df.at[idx, 'wind_mittel']}km/h"
      )
    else:
      print(
          f"✖ [Record {idx+1}/{len(df)}] Match ID: {match_id} -> API error"
          f" status {response.status_code}"
      )

  except Exception as e:
    print(f"✖ [Record {idx+1}/{len(df)}] Match ID: {match_id} -> Error: {e}")

  # Brief pause to respect API rate limits
  time.sleep(0.15)

# Save updated dataset to output file
df.to_csv(output_file, index=False)
print(f"\nSuccessfully finished! Enriched dataset saved to {output_file}")
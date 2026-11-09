import time
import pandas as pd
import requests

# Correct input and output file paths reflecting project structure
input_file = "data/spiele_roh_2.csv"
output_file = "data/spiele_roh_with_coords.csv"

df = pd.read_csv(input_file)

# Initialize coordinate columns if not present
if "latitude" not in df.columns:
  df["latitude"] = None
if "longitude" not in df.columns:
  df["longitude"] = None

# Cache dictionary to avoid duplicate API calls for the same city/location
coord_cache = {}

base_url = "https://geocoding-api.open-meteo.com/v1/search"


def get_coordinates(city_name):
  if not isinstance(city_name, str) or not city_name.strip():
    return None, None

  if city_name in coord_cache:
    return coord_cache[city_name]

  params = {
      "name": city_name,
      "count": 1,
      "language": "en",
      "format": "json",
  }

  try:
    response = requests.get(base_url, params=params, timeout=10)
    if response.status_code == 200:
      data = response.json()
      if "results" in data and len(data["results"]) > 0:
        lat = data["results"][0].get("latitude")
        lon = data["results"][0].get("longitude")
        coord_cache[city_name] = (lat, lon)
        return lat, lon
  except Exception as e:
    print(f"[{city_name}] Error fetching coordinates: {e}")

  return None, None


print(
    f"Starting coordinate retrieval for {len(df)} records (Real-time Console"
    " Logs):\n"
)

# Iterate through dataset rows with real-time feedback
for idx, row in df.iterrows():
  match_id = row.get("match_id", idx + 1)
  heim_team = row.get("heim_team", "Unknown")
  city = row["city"]

  lat, lon = get_coordinates(city)

  df.at[idx, "latitude"] = lat
  df.at[idx, "longitude"] = lon

  if lat is not None and lon is not None:
    print(
        f"✔ [Record {idx+1}/{len(df)}] Match ID: {match_id} | Team:"
        f" {heim_team} | City: {city} -> Lat: {lat}, Lon: {lon}"
    )
  else:
    print(
        f"✖ [Record {idx+1}/{len(df)}] Match ID: {match_id} | Team:"
        f" {heim_team} | City: {city} -> Coordinates not found!"
    )

  # Brief sleep to respect API rate limits
  time.sleep(0.1)

# Save the updated dataset back to the data folder
df.to_csv(output_file, index=False)
print(f"\nSuccessfully finished! Final dataset saved to {output_file}")
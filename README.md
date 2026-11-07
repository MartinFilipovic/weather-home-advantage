# Weather Conditions and Home Advantage
### A Comparative Analysis of European Football Leagues

Data Analytics Project – Martin, Hebron, Benjamin

**Research question:** How are weather conditions at kick-off associated with match outcomes and home advantage, and do these associations differ between leagues with different climates?

## Data
| Source | Content | Method |
|---|---|---|
| [football-data.org](https://www.football-data.org) | Matches: Premier League, Bundesliga, La Liga, seasons 2023/24–2025/26 (3,198 matches) | Web API |
| [Open-Meteo](https://open-meteo.com) | Hourly historical weather at each stadium | Web API |
| Wikipedia | Stadiums: coordinates, capacity, roof | Web scraping |

## Status
- [x] Match data collected (`01_spiele_sammeln.py` → `data/spiele_roh.csv`)
- [ ] Data cleaning + SQLite database (Martin)
- [ ] Stadiums + weather (Hebron)
- [ ] EDA + model (Benjamin)

## Setup
1. Install Python and run `pip install requests pandas`
2. Create a file `token.txt` in this folder containing only your [football-data.org](https://www.football-data.org/client/register) API token (this file is ignored by Git and never uploaded)
3. Run the scripts in order: `python 01_spiele_sammeln.py`, `python 02_teams_liste.py`

## Files
| File | Purpose |
|---|---|
| `test_api.py` | Tests which seasons the free API tier provides |
| `01_spiele_sammeln.py` | Downloads all matches → `data/spiele_roh.csv` |
| `02_teams_liste.py` | Lists all home teams → `data/teams.csv` |

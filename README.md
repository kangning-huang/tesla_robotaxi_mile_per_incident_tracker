# Tesla Robotaxi Miles Per Incident Tracker

An independent dashboard tracking Tesla's Robotaxi safety performance using NHTSA incident data and fleet size estimates.

## Live Dashboard

**[View Live Dashboard](https://kangning-huang.github.io/tesla_robotaxi_mile_per_incident_tracker/)**

The dashboard displays:
- **Safety Trend Analysis** — Miles per incident (MPI) chart with exponential trend projection
- **Current Streak** — Live-updating miles driven since last reported incident
- **Fleet Growth** — Austin robotaxi fleet size over time
- **Industry Comparison** — Tesla vs human drivers (police reports & insurance claims) vs Waymo
- **Incident Breakdown** — Table of all incidents with days between, fleet size, and miles driven

## Project Structure

```
├── .github/workflows/
│   ├── daily-analysis.yml      # Daily NHTSA data download & analysis
│   └── deploy-pages.yml        # Deploy dashboard to GitHub Pages
├── data/
│   ├── fleet_data.json         # Fleet size snapshots (Austin)
│   ├── fleet_data_scraped.json # Auto-scraped from robotaxitracker.com
│   ├── fleet_growth_active.json # Active fleet time-series (preserved for future use)
│   ├── fleet_growth_total.json  # Total fleet time-series (used for MPI)
│   ├── service_stoppages.json  # Dates when service was suspended (e.g. storms)
│   ├── analysis_results.json   # Latest MPI analysis output
│   ├── mpi_trend_chart.png     # Generated trend chart
│   └── SGO-2021-01_*.csv       # NHTSA incident data (downloaded)
├── docs/
│   ├── index.html              # Dashboard homepage
│   ├── styles.css              # Dark/light theme styling
│   └── app.js                  # Chart.js visualizations & calculations
├── scripts/
│   ├── download_nhtsa_data.py  # Download NHTSA ADS/ADAS CSV files
│   ├── analyze_tesla_incidents.py  # Calculate MPI with trend analysis
│   ├── scrape_fleet_data.py    # Scrape robotaxitracker.com via Playwright
│   └── scrape_fleet_growth.py  # Scrape active/total fleet growth time-series
└── requirements.txt
```

## Automated Daily Updates

The repository uses GitHub Actions to refresh data automatically.

| Job | Schedule | Description |
|-----|----------|-------------|
| `update-data` | Daily 6:00 AM UTC | Downloads NHTSA data, runs MPI analysis |
| `scrape-fleet-data` | Daily 6:00 AM UTC | Scrapes robotaxitracker.com for fleet size |

Updated files are auto-committed when changes are detected.

## Methodology

### Miles Per Incident Calculation

```
Miles between incidents = Σ (daily_fleet_size × 115 mi/day/vehicle)
```

- **Fleet size**: Interpolated daily from robotaxitracker.com snapshots
- **Total fleet size**: The calculation uses total fleet size (all vehicles in the Austin fleet), interpolated daily between known data points from robotaxitracker.com.
- **115 mi/day/vehicle**: Validated from Tesla's Q3 2025 report (~250K miles driven)
- **Incidents**: From NHTSA Standing General Order 2021-01 reports

### Trend Analysis

The analysis fits three models and selects the best by R²:
- **Linear**: MPI = a + b×t
- **Exponential**: MPI = a × e^(bt)
- **Quadratic**: MPI = a + bt + ct²

Current best fit: **Exponential** (R² = 0.955) with safety doubling every ~69 days.

### Human Driver Benchmarks

| Benchmark | Value | Source |
|-----------|-------|--------|
| Police-Reported Crashes | ~500,000 mi/crash | NHTSA CRSS 2023 |
| Insurance Claims | ~300,000 mi/claim | Swiss Re 2023 |

The 300K benchmark is more comparable since NHTSA requires reporting of *all* AV incidents, while ~60% of human property damage crashes go unreported to police.

## Data Sources

| Source | Data |
|--------|------|
| [NHTSA SGO 2021-01](https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/) | ADS/ADAS incident CSV files |
| [robotaxitracker.com](https://robotaxitracker.com) | Fleet size (Austin & Bay Area) |
| [NHTSA CRSS 2023](https://crashstats.nhtsa.dot.gov/Api/Public/Publication/813705) | Human crash statistics |
| [Swiss Re / Waymo Study](https://waymo.com/blog/2023/09/waymos-autonomous-vehicles-are-significantly-safer-than-human-driven-ones/) | Insurance claims analysis |

## Service Stoppages

The tracker accounts for days when Tesla's Robotaxi service was not operating. On these days, zero miles are accumulated — they are excluded from all MPI and streak calculations. Stoppage dates are recorded in [`data/service_stoppages.json`](data/service_stoppages.json) with sourced justifications.

| Dates | Reason |
|-------|--------|
| Jan 25–26, 2026 | [January 2026 North American winter storm](https://en.wikipedia.org/wiki/January_2026_North_American_winter_storm) — ice storm hit Austin with up to ¼ inch of ice, roads "extremely dangerous and near impossible," CapMetro suspended all transit, City of Austin closed facilities. Tesla Robotaxi service was observed offline before being reported as resumed later during the storm. |

**Why exclude these days?** Counting miles on days when no vehicles were operating would artificially inflate MPI figures and misrepresent the fleet's actual safety record. By zeroing out stoppage days, the tracker provides a more accurate miles-driven denominator.

## Data Scope

**Austin only**: All tracked incidents are from Austin, TX where Tesla operates true unsupervised Level 4 robotaxis. Bay Area vehicles have human safety drivers and aren't subject to ADS reporting requirements.

## Limitations

1. **Reporting Delays**: Tesla has been cited by NHTSA for delayed crash reporting
2. **Fleet Estimates**: Fleet data may not cover all dates (linearly interpolated between known data points)
3. **Miles Estimation**: No official daily miles data from Tesla
4. **Severity Variance**: All incidents treated equally regardless of severity
5. **Small Sample**: 10 incidents limits statistical confidence

## Local Development

```bash
# Clone and install
git clone https://github.com/kangning-huang/tesla_robotaxi_mile_per_incident_tracker.git
cd tesla_robotaxi_mile_per_incident_tracker
pip install -r requirements.txt

# Download NHTSA data
python scripts/download_nhtsa_data.py

# Run analysis
python scripts/analyze_tesla_incidents.py

# Scrape fleet data (requires Playwright)
pip install playwright && playwright install chromium
python scripts/scrape_fleet_data.py
```

## References

- [NHTSA SGO Crash Reporting](https://www.nhtsa.gov/laws-regulations/standing-general-order-crash-reporting)
- [Tesla Robotaxi Fleet (Jalopnik)](https://www.jalopnik.com/2063124/tesla-austin-robotaxi-fleet-34-cars/)
- [Swiss Re / Waymo Study (2024)](https://waymo.com/blog/2024/12/new-swiss-re-study-waymo)

---

Created by [Kangning Huang](https://x.com/FytasoK60918) · [Substack](https://open.substack.com/pub/kangninghuang)

*This is an independent analysis tool. Not affiliated with Tesla, Inc.*

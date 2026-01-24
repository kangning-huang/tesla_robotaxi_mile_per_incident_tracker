# Tesla Robotaxi Miles Per Incident Tracker

A tool to track and estimate the "miles per incident" metric for Tesla's Robotaxi service, based on NHTSA reports and fleet data.

## Why This Metric Matters

For TSLA investors, **miles per incident** is a critical safety metric that indicates:
- How safe Tesla's autonomous driving technology is
- Improvement trajectory over time
- Competitive position vs. Waymo, Zoox, and others
- Regulatory risk profile

## Data Sources

### 1. NHTSA Incident Data
- **Primary Source**: [robotaxitracker.com/nhtsa](https://robotaxitracker.com/nhtsa)
- **Alternative**: [NHTSA SGO Reports](https://static.nhtsa.gov/odi/inv/2025/INOA-PE25012-19171.pdf) (Standing General Order data)
- **Data Available**: Incident dates, locations, severity, descriptions

### 2. Fleet Size Data
- **Primary Source**: [robotaxitracker.com](https://robotaxitracker.com)
- **News Sources**: Teslarati, Electrek, official Tesla announcements

### Current Known Fleet Data (as of late 2025):
| Location | Vehicle Count | Notes |
|----------|---------------|-------|
| Austin, TX | ~34 Model Y | Robotaxi service with safety monitor |
| Bay Area, CA | ~128 vehicles | Human driver behind wheel (CA regulation) |

### Known Incident Data:
- **8 collisions** reported to NHTSA through October 2025
- Service launched in Austin late June 2025

## Estimation Methodology

### Formula
```
Miles Per Incident = Total Estimated Miles / Number of Incidents
```

### Estimating Total Miles Driven

Since Tesla doesn't publish daily miles data, we estimate using:

```
Total Miles = Σ (Active Vehicles × Days in Period × Avg Daily Miles)
```

#### Key Variables:
1. **Active Vehicles**: Fleet size at any point in time
2. **Days in Period**: Time between incidents or reporting periods
3. **Avg Daily Miles per Vehicle**: Industry estimates for robotaxis

#### Daily Miles Assumptions:
| Scenario | Miles/Day/Vehicle | Rationale |
|----------|-------------------|-----------|
| Conservative | 50 miles | Limited service hours, few rides |
| Moderate | 100 miles | ~8 hours operation, ~12 miles/hour avg |
| Aggressive | 150 miles | Near-continuous operation |

**Note**: Waymo vehicles reportedly drive ~150-200 miles/day in mature markets.

### Example Calculation

**Period**: June 25, 2025 - October 15, 2025 (~112 days)
**Incidents**: 7 collisions
**Average Fleet Size**: ~30 vehicles (ramping from ~10 to ~50)

| Scenario | Daily Miles | Total Miles | Miles/Incident |
|----------|-------------|-------------|----------------|
| Conservative | 50 | 168,000 | 24,000 |
| Moderate | 100 | 336,000 | 48,000 |
| Aggressive | 150 | 504,000 | 72,000 |

### Comparison Benchmarks
- **Human Drivers (US avg)**: ~500,000 miles per accident
- **Waymo (reported)**: ~1,000,000+ miles per incident (varies by severity)
- **Tesla FSD (supervised)**: ~3.4M miles per crash (Tesla's claim, different conditions)

## Data Collection Approach

### Option A: Manual Scraping (robotaxitracker.com blocks automated requests)
1. Visit the website manually
2. Export/copy incident data to JSON/CSV
3. Track fleet size announcements over time

### Option B: Automated Scraping with Browser Automation
```
Tools: Puppeteer, Playwright, or Selenium
Challenge: Site returns 403 for direct requests
Solution: Use headless browser with proper headers
```

### Option C: Alternative Data Sources
1. **NHTSA API/Database**: Standing General Order (SGO) reports
2. **News aggregation**: Parse Electrek, Teslarati, CNBC for incident reports
3. **Tesla investor relations**: Quarterly reports may include fleet data

## Proposed Data Schema

### incidents.json
```json
{
  "incidents": [
    {
      "id": "NHTSA-2025-001",
      "date": "2025-07-15",
      "location": "Austin, TX",
      "severity": "minor",
      "description": "Low-speed collision",
      "source_url": "https://...",
      "vehicle_type": "Model Y 2026"
    }
  ]
}
```

### fleet_data.json
```json
{
  "snapshots": [
    {
      "date": "2025-06-25",
      "austin_vehicles": 10,
      "bayarea_vehicles": 50,
      "source": "Tesla announcement"
    },
    {
      "date": "2025-12-22",
      "austin_vehicles": 34,
      "bayarea_vehicles": 128,
      "source": "Jalopnik/Electrek report"
    }
  ]
}
```

## Output: Miles Per Incident Tracker

### Proposed Output Format
```
Tesla Robotaxi Safety Metrics (Updated: 2026-01-24)
====================================================

Total Incidents: 8
Total Estimated Miles: 500,000 - 750,000

Miles Per Incident:
  - Conservative: 62,500
  - Moderate: 93,750

Trend: [chart showing improvement/decline over time]

Comparison:
  - Human Drivers: 500,000 mi/incident
  - Waymo: 1,000,000+ mi/incident
  - Tesla Robotaxi: ~75,000 mi/incident (estimated)
```

## Limitations & Caveats

1. **Incident Reporting**: Tesla has been cited by NHTSA for delayed crash reporting
2. **Fleet Size Estimates**: Actual active vehicles vs. registered vehicles differ
3. **Miles Estimation**: No official daily miles data from Tesla
4. **Severity Variance**: Not all incidents are equal (minor vs. serious)
5. **Supervised vs. Unsupervised**: Austin has passenger monitors; Bay Area has drivers

## Next Steps

1. [ ] Set up web scraping for robotaxitracker.com (handle 403 with browser automation)
2. [ ] Create data ingestion pipeline for incidents
3. [ ] Build fleet size tracking with date interpolation
4. [ ] Implement miles estimation with configurable assumptions
5. [ ] Create visualization/dashboard for the metric over time
6. [ ] Set up automated weekly/daily updates

## References

- [Tesla FSD Safety Report](https://www.tesla.com/fsd/safety)
- [NHTSA Tesla Investigation](https://techcrunch.com/2025/12/05/feds-find-more-complaints-of-teslas-fsd-running-red-lights-and-crossing-lanes/)
- [Tesla Robotaxi Fleet Size Reports](https://www.jalopnik.com/2063124/tesla-austin-robotaxi-fleet-34-cars/)
- [Tesla Robotaxi Crash Reports](https://electrek.co/2025/12/15/tesla-reports-another-robotaxi-crash-even-with-supervisor/)
- [Morgan Stanley 2026 Projections](https://finance.yahoo.com/news/tesla-seen-meaningfully-increasing-robotaxi-163028375.html)

# Tesla Robotaxi Miles Per Incident Tracker

A tool to track and estimate the "miles per incident" metric for Tesla's Robotaxi service, based on NHTSA reports and fleet data.

## Why This Metric Matters

For TSLA investors, **miles per incident** is a critical safety metric that indicates:
- How safe Tesla's autonomous driving technology is
- Improvement trajectory over time
- Competitive position vs. Waymo, Zoox, and others
- Regulatory risk profile

## Data Sources

### 1. NHTSA Official Data (Primary - No Scraping Needed!)

NHTSA provides **direct CSV downloads** of all autonomous vehicle crash data under Standing General Order 2021-01.

#### Direct Download Links:
| File | URL | Description |
|------|-----|-------------|
| **ADS Incidents** | [SGO-2021-01_Incident_Reports_ADS.csv](https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADS.csv) | Automated Driving Systems (L3-L5) crashes |
| **ADAS Incidents** | [SGO-2021-01_Incident_Reports_ADAS.csv](https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADAS.csv) | Level 2 ADAS crashes (FSD, Autopilot) |
| **Archive (2021-2025)** | [Archive Folder](https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/Archive-2021-2025/) | Historical data before June 2025 |
| **Data Dictionary** | [SGO-2021-01_Data_Element_Definitions.pdf](https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Data_Element_Definitions.pdf) | Field definitions (122 columns!) |

#### Key Data Fields in CSV:
- Incident date, city, state
- Vehicle make/model/year
- System type (ADS vs ADAS)
- Crash severity and injuries
- System engagement status 30 seconds before crash
- Weather and road conditions

#### Update Frequency:
- NHTSA updates CSV files **monthly**
- Current data: June 16, 2025 - December 15, 2025

#### Data Caveats:
- PII and CBI (Confidential Business Info) are redacted
- Data not normalized by miles traveled or fleet size
- Tesla cited for delayed reporting (may have lag)

### 2. Fleet Size Data
- **Primary Source**: [robotaxitracker.com](https://robotaxitracker.com) (requires browser automation)
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

### Option A: Direct NHTSA Download (Recommended for Incidents)

Simply download the CSV files directly - no scraping needed!

```python
import pandas as pd

# Download ADS (Robotaxi) incidents
ads_url = "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADS.csv"
ads_df = pd.read_csv(ads_url)

# Filter for Tesla
tesla_ads = ads_df[ads_df['Make'].str.contains('Tesla', case=False, na=False)]
```

### Option B: Browser Automation for robotaxitracker.com (Fleet Data)

robotaxitracker.com returns 403 for direct requests. Use browser automation:

#### Recommended Tool: **Playwright** (Python)
```bash
pip install playwright
playwright install
```

**Why Playwright over alternatives:**
| Tool | Pros | Cons |
|------|------|------|
| **Playwright** | Fast, multi-browser, async support, modern API | Newer, smaller community |
| Puppeteer | Fast, Chrome-optimized, large community | Node.js only, Chrome-focused |
| Selenium | Most mature, all browsers, all languages | Slower, more flaky |

```python
from playwright.async_api import async_playwright

async def scrape_robotaxi_tracker():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Fleet data
        await page.goto('https://robotaxitracker.com')
        fleet_data = await page.query_selector_all('.fleet-count')

        # NHTSA incidents page
        await page.goto('https://robotaxitracker.com/nhtsa')
        incidents = await page.query_selector_all('.incident-row')

        await browser.close()
```

#### GitHub Repos for NHTSA Data:
| Repo | Description | Language |
|------|-------------|----------|
| [iMears/nhtsa](https://github.com/iMears/nhtsa) | NPM package for NHTSA Vehicle API | JavaScript |
| [ZJAllen/NCAPDownload](https://github.com/ZJAllen/NCAPDownload) | NHTSA NCAP test data scraper | Python |
| [crashapi (R)](https://elipousson.github.io/crashapi/) | FARS crash data API wrapper | R |

### Option C: AI-Powered Scraping (For Complex Sites)

Modern AI-powered scrapers can handle dynamic content better:

#### **Crawl4AI** (Recommended - Open Source)
- 58k+ GitHub stars, fully open source
- Outputs clean markdown for LLM processing
- Runs locally (no API costs)
- Supports async and browser automation

```bash
pip install crawl4ai
```

```python
from crawl4ai import AsyncWebCrawler

async def crawl_with_ai():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://robotaxitracker.com",
            extraction_strategy="LLMExtractionStrategy",
            instruction="Extract fleet size data for Tesla robotaxis"
        )
        return result.extracted_content
```

GitHub: [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)

#### **Firecrawl** (Managed Service)
- Y Combinator backed
- 33% faster, 40% higher success rate
- Natural language extraction (no CSS selectors)
- Has self-hosted option

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="your-key")
result = app.scrape_url(
    "https://robotaxitracker.com",
    params={"formats": ["markdown", "extract"]}
)
```

### Option D: News Aggregation for Fleet Updates

Since fleet size changes infrequently, monitor news sources:
- Electrek, Teslarati, CNBC for Tesla announcements
- Use RSS feeds or news APIs (NewsAPI, GDELT)
- Manual tracking in `fleet_data.json`

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

1. [ ] **Download NHTSA data** - Fetch ADS/ADAS CSV files, filter for Tesla incidents
2. [ ] **Set up Playwright** - Scrape robotaxitracker.com for fleet size data
3. [ ] **Build data pipeline** - Parse, clean, and store incident + fleet data
4. [ ] **Implement miles estimation** - Calculate with configurable assumptions
5. [ ] **Create visualization** - Chart miles-per-incident trend over time
6. [ ] **Automate updates** - GitHub Actions to refresh data monthly
7. [ ] **Compare competitors** - Add Waymo, Cruise, Zoox data for context

## Recommended Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Collection                          │
├─────────────────────────────────────────────────────────────┤
│  NHTSA CSV → pandas (direct download, no scraping)          │
│  robotaxitracker.com → Playwright or Crawl4AI               │
│  News/Fleet Updates → Manual or RSS aggregation             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Processing                          │
├─────────────────────────────────────────────────────────────┤
│  Python: pandas, numpy                                      │
│  Data storage: SQLite or JSON files                         │
│  Scheduling: cron or GitHub Actions                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Visualization                            │
├─────────────────────────────────────────────────────────────┤
│  Charts: matplotlib, plotly                                 │
│  Dashboard: Streamlit or static HTML                        │
│  Output: README badges, JSON API                            │
└─────────────────────────────────────────────────────────────┘
```

### Python Dependencies
```
pandas>=2.0
playwright>=1.40
crawl4ai>=0.3
matplotlib>=3.8
requests>=2.31
```

## Useful GitHub Repositories

### NHTSA Data Tools
| Repository | Stars | Description |
|------------|-------|-------------|
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | 58k+ | AI-powered web crawler, outputs LLM-ready markdown |
| [iMears/nhtsa](https://github.com/iMears/nhtsa) | - | NPM package for NHTSA Vehicle API |
| [ZJAllen/NCAPDownload](https://github.com/ZJAllen/NCAPDownload) | - | Python scraper for NHTSA crash test data |
| [Biegalski-LLC/NHTSA-Vehicle-API](https://github.com/Biegalski-LLC/NHTSA-Vehicle-API) | - | PHP wrapper for NHTSA VIN decoder |

### Web Scraping
| Repository | Stars | Description |
|------------|-------|-------------|
| [playwright-python](https://github.com/microsoft/playwright-python) | 11k+ | Microsoft's browser automation for Python |
| [mendableai/firecrawl](https://github.com/mendableai/firecrawl) | 20k+ | AI-powered web scraper with LLM extraction |
| [ScrapeGraphAI](https://github.com/VinciGit00/Scrapegraph-ai) | 15k+ | Graph-based AI scraping |

## References

### Official Data Sources
- [NHTSA SGO Crash Reporting Portal](https://www.nhtsa.gov/laws-regulations/standing-general-order-crash-reporting)
- [NHTSA File Downloads](https://www.nhtsa.gov/file-downloads)
- [SGO Data Dictionary (PDF)](https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Data_Element_Definitions.pdf)
- [Tesla FSD Safety Report](https://www.tesla.com/fsd/safety)

### News & Analysis
- [NHTSA Tesla Investigation (TechCrunch)](https://techcrunch.com/2025/12/05/feds-find-more-complaints-of-teslas-fsd-running-red-lights-and-crossing-lanes/)
- [Tesla Robotaxi Fleet Size (Jalopnik)](https://www.jalopnik.com/2063124/tesla-austin-robotaxi-fleet-34-cars/)
- [Tesla Robotaxi Crash Reports (Electrek)](https://electrek.co/2025/12/15/tesla-reports-another-robotaxi-crash-even-with-supervisor/)
- [AV Crash Statistics 2025 (Craft Law)](https://www.craftlawfirm.com/autonomous-vehicle-accidents-2019-2024-crash-data/)

### Tool Documentation
- [Playwright Python Docs](https://playwright.dev/python/)
- [Crawl4AI GitHub](https://github.com/unclecode/crawl4ai)
- [Firecrawl Docs](https://www.firecrawl.dev/blog/best-open-source-web-scraping-libraries)
- [Puppeteer vs Playwright vs Selenium Comparison](https://www.scrapingbee.com/blog/best-python-web-scraping-libraries/)

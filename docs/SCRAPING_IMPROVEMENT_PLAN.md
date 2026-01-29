# Scraping Improvement Plan

## Root Cause Analysis

### What Actually Happened (Git Forensics)

The scraping failure was **NOT caused by code changes**. Git history proves the scraper
code was byte-for-byte identical when it stopped working:

| Date | Code Hash | Historical Points | Event |
|---|---|---|---|
| Jan 24 13:14 | `a3305e7` | **61** | Working (PR #19 merged) |
| Jan 25 04:47 | `a3305e7` | **61** | Last successful scrape |
| Jan 27 08:17 | `a3305e7` (same!) | **0** | **Site changed — broke** |
| Jan 28+ | `a3305e7` | **0** | Still broken, same code |
| Jan 29 00:04+ | Various new code | **0** | Fix attempts begin (PRs #56-#63) |
| Jan 29 00:45 | `2fc4cd8` | **140** | **Briefly fixed** (3-strategy + validation) |
| Jan 29 01:06+ | `9cd639d`+ | **0** | Over-engineered, broke again |

**Conclusion**: robotaxitracker.com changed their site between Jan 25-27, breaking the
original tooltip hovering approach. The old simple JS mouse event dispatch stopped
triggering Recharts tooltips.

### Why PR #56-#63 Made Things Worse

Each "fix" attempt grew the scraper (798 → 2759 lines) while introducing:
- Strict chart dimension gates (`height >= 100`, `width >= 200`) that reject valid charts
- Retry loops with **random tab/button clicking** that destabilize page state
- `ensure_fleet_chart_visible()` that aggressively scrolls/polls before extraction
- `isFleetData()` validation requiring specific key names ("austin", "bay", "fleet")
- Bar chart mode toggling that may not match current site structure

### The One Version That Worked Post-Change

Commit `2fc4cd8` ("Fix garbage historical data") got **140 points** on Jan 29.
It had:
- 3-strategy approach (API interception → React fiber → native mouse hover)
- Validation and deduplication
- Fleet Growth heading proximity-based chart targeting
- Simple fallback to first `.recharts-wrapper` chart
- **NO** dimension validation gates, **NO** retry loops, **NO** random clicking

The very next commit `9cd639d` added dimension validation and broke it back to 0.

## Problem Statement

The Playwright-based scraper for robotaxitracker.com successfully extracts **current
fleet numbers** (e.g., 73 Austin, 168 Bay Area, 241 total) but fails to extract
**historical chart data** because the site changed its chart rendering between
Jan 25-27, 2026.

## Site Tech Stack

- **Framework**: Next.js (React) — `__NEXT_DATA__`, `self.__next_f`, `/_next/` paths
- **Charts**: Recharts — `.recharts-wrapper`, `svg.recharts-surface` DOM elements
- **Bot Protection**: Returns 403 to simple HTTP fetchers
- **No public repo**: Closed-source, no public API documentation

## Recommended Fix: Revert to 2fc4cd8 Approach

The immediate fix should **revert the chart detection and mouse hover logic** back to
the `2fc4cd8` version (which produced 140 data points with the changed site), then
strip out the over-engineering added by later commits.

### Step 1: Remove Over-Engineering (Critical)

Remove from `9cd639d` and later:
1. **Remove** `ensure_fleet_chart_visible()` — its dimension polling and re-scrolling
   disrupts page state before extraction strategies run
2. **Remove** chart dimension validation gates (`height >= 100`, `width >= 200`) from
   `extract_data_via_mouse_hover()` — let it attempt extraction regardless
3. **Remove** the 5-attempt retry loop with random tab/button clicking in mouse hover
4. **Remove** bar chart mode toggling (`click_bar_chart_mode()`) — this may no longer
   match the site's UI

### Step 2: Restore Simple Chart Finding

The `2fc4cd8` approach that worked:
1. Find Fleet Growth heading via text selector
2. Find the `.recharts-wrapper` chart closest below the heading
3. Get its `svg.recharts-surface` bounding box
4. Fall back to first `.recharts-wrapper` if heading not found
5. Proceed to hover immediately — no dimension validation

### Step 3: Keep Useful Additions

Preserve from the rewrite:
- 3-strategy approach (API interception → React fiber → mouse hover)
- `validate_historical_data()` and `deduplicate_by_date()`
- Active fleet extraction (tab switching, separate historical extraction)
- Network response capture during page load
- Diagnostic screenshots

## Further Improvements (After Revert)

### Phase 1: Broaden React Fiber Extraction

The `isFleetData()` validator is too strict. Changes:
1. Log ALL data arrays found in Recharts fibers (diagnostic-first)
2. Relax to accept arrays with date + numeric values even without region-specific keys
3. Scan `__reactProps$` keys alongside `__reactFiber$`

### Phase 2: Fix Network Interception

Current interception only captures URL-keyword-filtered responses. Changes:
1. Capture ALL responses and search bodies for fleet data patterns
2. Parse Next.js RSC streaming format: decode `self.__next_f.push([1,"..."])` strings
3. Intercept `/_next/data/` routes and `text/x-component` responses

### Phase 3: Direct API Discovery

1. Run Playwright once with full network logging to find all API endpoints
2. If found, call API directly from Python — eliminates browser dependency entirely

### Phase 4: Production Hardening

Use [crawlee-python](https://github.com/apify/crawlee-python) (~5k stars) or
[Scrapling](https://github.com/D4Vinci/Scrapling) (~8.9k stars) for:
- Automatic retry and session management
- Stealth/anti-detection (PatchRight)
- Proxy rotation

## Research: Relevant GitHub Repositories

| Repository | Stars | Key Feature |
|---|---|---|
| [apify/crawlee](https://github.com/apify/crawlee) | ~14k | Production Playwright crawling with retry, proxy rotation, anti-detection |
| [apify/crawlee-python](https://github.com/apify/crawlee-python) | ~5k | Python Playwright crawler with session management |
| [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | ~8.9k | Adaptive scraping with stealth Playwright, PatchRight, Cloudflare bypass |
| [recharts/recharts](https://github.com/recharts/recharts) | ~24k | Source library — reveals internal tooltip triggering mechanism |

### Key Playwright Issues

- [#16296](https://github.com/microsoft/playwright/issues/16296): Use `force: true` on hover for SVG chart elements
- [#17255](https://github.com/microsoft/playwright/issues/17255): Chart tooltip extraction is a known hard problem

## References

- [Playwright Network Interception Docs](https://playwright.dev/docs/network)
- [Intercepting Hidden Data with Playwright (Medium)](https://medium.com/@navanishan/intercepting-network-requests-in-playwright-a-deep-dive-into-scraping-hidden-data-b5fcfabd1eb9)
- [Automating Column Charts with Playwright (Medium)](https://medium.com/@tpshadinijk/automating-column-chart-with-playwright-e1a23076166e)
- [Scrapling Documentation](https://scrapling.readthedocs.io/en/latest/)
- [Crawlee Python Docs](https://crawlee.dev/python/docs/examples/playwright-crawler)

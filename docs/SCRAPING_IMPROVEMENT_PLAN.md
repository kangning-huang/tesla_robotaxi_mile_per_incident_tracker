# Scraping Improvement Plan

## Problem Statement

The Playwright-based scraper for robotaxitracker.com successfully extracts **current fleet numbers** (e.g., 73 Austin, 168 Bay Area, 241 total) but consistently fails to extract **historical data**, **active historical data**, and **NHTSA incidents**. All 4 extraction strategies return empty results.

## Current Architecture

The scraper (`scripts/scrape_fleet_data.py`, 2759 lines) uses Playwright to:
1. Navigate to robotaxitracker.com
2. Extract current fleet numbers via regex/JS evaluation
3. Attempt 4 strategies for historical chart data extraction
4. Switch to "Active" tab and repeat
5. Navigate to `/nhtsa` for incident data

### Why Each Strategy Fails

| Strategy | Approach | Failure Mode |
|---|---|---|
| 1. API Interception | Captures JSON from network requests matching keywords | Next.js RSC apps stream data via `self.__next_f.push()`, not traditional JSON APIs |
| 2. React Fiber | Traverses `__reactFiber$` for `memoizedProps.data` | `isFleetData()` validator requires keys with "austin"/"bay"/"fleet" — actual keys may differ |
| 3. Bar Hover | Locates SVG `<rect>` elements, hovers each one | Chart may be in line mode; bar toggle may fail; Recharts DOM structure may have changed |
| 4. Mouse Sweep | Sweeps mouse across chart area for tooltips | Recharts uses invisible overlay `<rect>` for events; synthetic mouse events may not trigger tooltips |

## Site Tech Stack

- **Framework**: Next.js (React) — evidenced by `__NEXT_DATA__`, `self.__next_f`, `/_next/` paths
- **Charts**: Recharts — evidenced by `.recharts-wrapper`, `svg.recharts-surface` DOM elements
- **Bot Protection**: Returns 403 to simple HTTP fetchers
- **No public repo**: Site is closed-source with no public API documentation

## Research: Relevant GitHub Repositories

| Repository | Stars | Key Feature |
|---|---|---|
| [apify/crawlee](https://github.com/apify/crawlee) | ~14k | Production Playwright crawling with retry, proxy rotation, anti-detection |
| [apify/crawlee-python](https://github.com/apify/crawlee-python) | ~5k | Python Playwright crawler with session management |
| [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | ~8.9k | Adaptive scraping with stealth Playwright, PatchRight, Cloudflare bypass |
| [recharts/recharts](https://github.com/recharts/recharts) | ~24k | Source library — reveals internal tooltip triggering mechanism |

### Key Playwright Issues

- [#16296](https://github.com/microsoft/playwright/issues/16296): Use `force: true` on hover for SVG chart elements
- [#17255](https://github.com/microsoft/playwright/issues/17255): Chart tooltip extraction is a known hard problem (closed without resolution)

## Proposed Solution — Priority-Ordered Phases

### Phase 1: Fix Network Interception (Highest Impact)

The data is being sent to the browser — we just need to capture it in the right format.

**Changes:**
1. Capture ALL network responses (not just URL-keyword-filtered ones)
2. Parse Next.js RSC streaming format: decode `self.__next_f.push([1,"..."])` escaped strings
3. Intercept `/_next/data/` routes (Pages Router JSON payloads)
4. Intercept `text/x-component` responses (App Router RSC format)
5. Add `page.reload()` after initial load to force fresh API calls while intercepting

### Phase 2: Broaden React Fiber Extraction

**Changes:**
1. Relax `isFleetData()` — accept arrays with date + numeric values even without region-specific key names
2. Log ALL data arrays found in Recharts fibers (diagnostic-first approach)
3. Scan `__reactProps$` keys alongside `__reactFiber$` (newer React versions)
4. Access Recharts' internal Redux store directly

### Phase 3: Improve Tooltip Extraction

**Changes:**
1. Use PatchRight or Scrapling's stealth mode to reduce headless detection
2. Target Recharts' internal overlay `<rect>` element specifically for events
3. Use `locator.hover({force: true})` pattern from Playwright Issue #16296
4. Inject `setTimeout(() => { debugger }, 3000)` to freeze tooltip state

### Phase 4: Direct API Discovery (Best Long-term)

**Changes:**
1. Run Playwright once with full network logging to discover ALL API endpoints
2. Look for Supabase, Firebase, or REST API patterns in captured traffic
3. If found, call API directly from Python — eliminates browser dependency entirely
4. Extract auth tokens from page JavaScript/cookies if needed

### Phase 5: Use Crawlee/Scrapling for Production

**Changes:**
1. Replace raw Playwright with crawlee-python for automatic retry and session management
2. Or use Scrapling with StealthyFetcher for Cloudflare bypass
3. Add proxy rotation for reliability

## Implementation Priority

1. **Phase 1** — Single most impactful fix (the data IS being sent to the browser)
2. **Phase 4** — One-time investigation to potentially eliminate browser automation
3. **Phase 2** — Quick diagnostic win to understand actual data shapes
4. **Phase 3** — Fallback improvement
5. **Phase 5** — Long-term production hardening

## References

- [Playwright Network Interception Docs](https://playwright.dev/docs/network)
- [Intercepting Hidden Data with Playwright (Medium)](https://medium.com/@navanishan/intercepting-network-requests-in-playwright-a-deep-dive-into-scraping-hidden-data-b5fcfabd1eb9)
- [Automating Column Charts with Playwright (Medium)](https://medium.com/@tpshadinijk/automating-column-chart-with-playwright-e1a23076166e)
- [Scheduled Web Scraping with Playwright + GitHub Actions](https://www.marcveens.nl/posts/scheduled-web-scraping-made-easy-using-playwright-with-github-actions)
- [Scrapling Documentation](https://scrapling.readthedocs.io/en/latest/)
- [Crawlee Python Docs](https://crawlee.dev/python/docs/examples/playwright-crawler)

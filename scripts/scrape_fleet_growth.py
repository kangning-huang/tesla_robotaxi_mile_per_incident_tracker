#!/usr/bin/env python3
"""
Scrape active fleet growth time series data from robotaxitracker.com.

Uses Playwright to render the page and extract data from the Recharts bar chart
via multiple strategies:

    1. Intercept API responses during page load
    2. Extract from React fiber tree (Recharts component props)
    3. Mouse hover tooltip extraction as fallback

Output: CSV and JSON files with date, austin, bayarea, total columns.
"""

import asyncio
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright is required. Install with:")
    print("  pip install playwright && playwright install chromium")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_JSON_ACTIVE = DATA_DIR / "fleet_growth_active.json"
OUTPUT_CSV_ACTIVE = DATA_DIR / "fleet_growth_active.csv"
OUTPUT_JSON_TOTAL = DATA_DIR / "fleet_growth_total.json"
OUTPUT_CSV_TOTAL = DATA_DIR / "fleet_growth_total.csv"
URL = "https://robotaxitracker.com"


# ---------------------------------------------------------------------------

# Strategy 1: Intercept API responses

# ---------------------------------------------------------------------------

def extract_fleet_data_from_api_responses(captured_responses: list) -> list:
    """Parse captured API responses for fleet growth time-series arrays."""
    results = []
    for resp in captured_responses:
        body = resp.get("body")
        if not body:
            continue
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            continue

        # Recursively search for arrays that look like fleet time-series
        arrays = _find_fleet_arrays(data, depth=0, path="root")
        for arr, source in arrays:
            points = _parse_fleet_array(arr)
            if points:
                results.extend(points)

    return results


def _find_fleet_arrays(obj, depth, path):
    """Recursively find arrays that look like fleet time-series data."""
    found = []
    if depth > 8 or obj is None:
        return found
    if isinstance(obj, list) and len(obj) >= 3:
        if _looks_like_fleet_data(obj):
            found.append((obj, path))
            return found
    if isinstance(obj, dict):
        for key, val in list(obj.items())[:50]:
            found.extend(_find_fleet_arrays(val, depth + 1, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:50]):
            found.extend(_find_fleet_arrays(item, depth + 1, f"{path}[{i}]"))
    return found


def _looks_like_fleet_data(arr):
    """Check if an array looks like fleet growth data."""
    if not arr or not isinstance(arr[0], dict):
        return False
    keys = [k.lower() for k in arr[0].keys()]
    has_date = any("date" in k or "time" in k or "day" in k for k in keys)
    has_fleet = any(
        "austin" in k or "bay" in k or "sf" in k or "fleet" in k or "vehicle" in k
        for k in keys
    )
    return has_date and has_fleet


def _parse_fleet_array(arr):
    """Convert a raw fleet data array to normalized data points."""
    points = []
    for item in arr:
        if not isinstance(item, dict):
            continue
        date_str = _extract_date(item)
        if not date_str:
            continue
        austin, bayarea, total = _extract_counts(item)
        # If austin is missing but total and bayarea are present, compute it.
        # The chart data often only has "unsupervisedAustin" (which we skip)
        # plus "bayArea" and "total". The Austin fleet = total - bayArea.
        if austin is None and total is not None and bayarea is not None:
            austin = total - bayarea
        if austin is not None or bayarea is not None or total is not None:
            points.append({
                "date": date_str,
                "austin": austin,
                "bayarea": bayarea,
                "total": total,
            })
    return points


def _extract_date(item):
    """Extract and normalize a date string from a dict."""
    for key in ["date", "Date", "timestamp", "day", "created_at", "time"]:
        if key in item and item[key] is not None:
            return normalize_date_string(str(item[key]))
    return None


def _extract_counts(item):
    """Extract austin, bayarea, total counts from a dict.

    Skips 'unsupervised' keys to avoid confusing 'Unsupervised Austin'
    (a different chart line) with the total Austin fleet.
    """
    austin = bayarea = total = None
    for key, val in item.items():
        if val is None or not isinstance(val, (int, float)):
            continue
        kl = key.lower().replace("_", "").replace("-", "")
        if "unsupervised" in kl:
            continue  # Skip unsupervised Austin (different chart line)
        if "austin" in kl:
            austin = int(val)
        elif "bay" in kl or "sf" in kl or "sanfran" in kl:
            bayarea = int(val)
        elif "total" in kl or "fleet" in kl:
            total = int(val)
    return austin, bayarea, total


def normalize_date_string(date_val: str) -> str:
    """Normalize various date formats to YYYY-MM-DD."""
    if not date_val:
        return None

    # ISO format: 2025-06-22 or 2025-06-22T...
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_val)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    # Unix timestamp in milliseconds
    if date_val.isdigit() and len(date_val) >= 13:
        try:
            dt = datetime.fromtimestamp(int(date_val) / 1000)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, OSError):
            pass

    # Month Day, Year
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    }
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", date_val)
    if m:
        mn = month_map.get(m.group(1).lower()) or month_map.get(m.group(1).lower()[:3])
        if mn:
            return f"{m.group(3)}-{mn:02d}-{int(m.group(2)):02d}"

    return None


# ---------------------------------------------------------------------------

# Strategy 2: React fiber traversal (Recharts props)

# ---------------------------------------------------------------------------

EXTRACT_CHART_DATA_JS = """
() => {
    const candidates = [];

    function isFleetData(arr) {
        if (!Array.isArray(arr) || arr.length < 3) return false;
        const sample = arr[0];
        if (typeof sample !== 'object' || sample === null) return false;
        const keys = Object.keys(sample).map(k => k.toLowerCase());
        const hasDate = keys.some(k =>
            k.includes('date') || k.includes('time') || k.includes('day')
        );
        const hasFleetKey = keys.some(k =>
            k.includes('austin') || k.includes('bay') || k.includes('sf') ||
            k.includes('sanfran') || k.includes('fleet') || k.includes('vehicle')
        );
        return hasDate && hasFleetKey;
    }

    function findFleetArrays(obj, depth, path) {
        if (depth > 6 || !obj || typeof obj !== 'object') return;
        if (Array.isArray(obj) && isFleetData(obj)) {
            candidates.push({data: obj, source: path, size: obj.length});
            return;
        }
        try {
            const keys = Array.isArray(obj) ? [] : Object.keys(obj);
            for (const key of keys.slice(0, 50)) {
                try { findFleetArrays(obj[key], depth + 1, path + '.' + key); } catch(e) {}
            }
        } catch(e) {}
    }

    // Method 1: __NEXT_DATA__
    if (window.__NEXT_DATA__) {
        findFleetArrays(window.__NEXT_DATA__, 0, '__NEXT_DATA__');
    }

    // Method 2: React fiber traversal - target Fleet Growth chart
    const fleetSection = (() => {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, div, span, p');
        for (const el of headings) {
            const text = (el.textContent || '').trim();
            if (text === 'Fleet Growth' && el.children.length < 5) {
                let parent = el.parentElement;
                for (let i = 0; i < 10 && parent; i++) {
                    if (parent.querySelector('.recharts-wrapper')) return parent;
                    parent = parent.parentElement;
                }
            }
        }
        return null;
    })();

    const chartContainers = fleetSection
        ? fleetSection.querySelectorAll('.recharts-wrapper, .recharts-responsive-container')
        : document.querySelectorAll('.recharts-wrapper, .recharts-responsive-container');

    for (const container of chartContainers) {
        const fiberKeys = Object.keys(container).filter(k =>
            k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$') ||
            k.startsWith('__reactProps$')
        );
        for (const fiberKey of fiberKeys) {
            let fiber = container[fiberKey];
            let visited = 0;
            while (fiber && visited < 50) {
                visited++;
                if (fiber.memoizedProps) {
                    const props = fiber.memoizedProps;
                    if (props.data && isFleetData(props.data)) {
                        candidates.push({
                            data: props.data,
                            source: 'fiber.memoizedProps.data',
                            size: props.data.length
                        });
                    }
                    if (props.children) {
                        const children = Array.isArray(props.children) ? props.children : [props.children];
                        for (const child of children) {
                            if (child && child.props && child.props.data && isFleetData(child.props.data)) {
                                candidates.push({
                                    data: child.props.data,
                                    source: 'fiber.child.props.data',
                                    size: child.props.data.length
                                });
                            }
                        }
                    }
                }
                if (fiber.memoizedState) {
                    findFleetArrays(fiber.memoizedState, 0, 'fiber.memoizedState');
                }
                fiber = fiber.return;
            }
        }
    }

    // Method 3: Scan window/global
    try {
        for (const key of Object.keys(window)) {
            try {
                const val = window[key];
                if (Array.isArray(val) && isFleetData(val)) {
                    candidates.push({data: val, source: 'window.' + key, size: val.length});
                } else if (val && typeof val === 'object' && !Array.isArray(val)) {
                    findFleetArrays(val, 0, 'window.' + key);
                }
            } catch(e) {}
        }
    } catch(e) {}

    // Score candidates
    if (candidates.length > 0) {
        for (const c of candidates) {
            let score = 0;
            const sampleKeys = Object.keys(c.data[0]).map(k => k.toLowerCase());
            if (sampleKeys.some(k => k.includes('austin'))) score += 1000;
            if (sampleKeys.some(k => k.includes('bay') || k.includes('sf'))) score += 1000;
            if (sampleKeys.some(k => k.includes('fleet') || k.includes('vehicle'))) score += 500;
            const dates = new Set();
            for (let i = 0; i < Math.min(c.data.length, 20); i++) {
                for (const k of Object.keys(c.data[i])) {
                    if (k.toLowerCase().includes('date') || k.toLowerCase().includes('time')) {
                        dates.add(String(c.data[i][k]));
                        break;
                    }
                }
            }
            if (dates.size > 5) score += 500;
            else if (dates.size > 2) score += 200;
            score += Math.min(c.size, 200);
            c.score = score;
        }
        candidates.sort((a, b) => b.score - a.score);
        return {
            data: candidates[0].data,
            source: candidates[0].source,
            all_sources: candidates.map(c => c.source + ':' + c.size + ':score=' + c.score)
        };
    }
    return null;

}
"""


async def extract_chart_data_from_react(page) -> list:
    """Extract chart data from React fiber tree / Recharts props."""
    try:
        result = await page.evaluate(EXTRACT_CHART_DATA_JS)
        if result and result.get("data"):
            print(f"  React fiber: found data from '{result['source']}'")
            if result.get("all_sources"):
                print(f"  All candidates: {result['all_sources']}")
            return _parse_fleet_array(result["data"])
    except Exception as e:
        print(f"  React fiber extraction failed: {e}")
    return []


# ---------------------------------------------------------------------------

# Strategy 3: Mouse hover tooltip extraction

# ---------------------------------------------------------------------------

def parse_tooltip_text(text: str) -> dict:
    """Parse Recharts tooltip text to extract date and counts."""
    if not text:
        return None

    result = {}
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10,
        "november": 11, "december": 12,
    }

    # Try date patterns
    date_patterns = [
        (r"(\d{4})-(\d{2})-(\d{2})", "iso"),
        (r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", "month_day_year"),
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "mdy_slash"),
    ]

    for pattern, fmt in date_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            g = m.groups()
            if fmt == "iso":
                result["date"] = f"{g[0]}-{g[1]}-{g[2]}"
            elif fmt == "month_day_year":
                mn = month_map.get(g[0].lower()) or month_map.get(g[0].lower()[:3])
                if mn:
                    result["date"] = f"{g[2]}-{mn:02d}-{int(g[1]):02d}"
            elif fmt == "mdy_slash":
                result["date"] = f"{g[2]}-{int(g[0]):02d}-{int(g[1]):02d}"
            if result.get("date"):
                break

    if not result.get("date"):
        return None

    # Extract counts: "Austin  39" or "Austin39" (tooltip text may lack spaces)
    # Must NOT match "Unsupervised Austin" (a different chart line for unsupervised ADS vehicles)
    austin_m = re.search(r"(?<!Unsupervised\s)(?<!unsupervised\s)(?<!\w)Austin\s*(\d+)", text, re.IGNORECASE)
    bay_m = re.search(r"Bay\s*Area\s*(\d+)", text, re.IGNORECASE)
    total_m = re.search(r"Total\s*(?:Fleet\s*)?(\d+)", text, re.IGNORECASE)

    if austin_m:
        result["austin"] = int(austin_m.group(1))
    if bay_m:
        result["bayarea"] = int(bay_m.group(1))
    if total_m:
        result["total"] = int(total_m.group(1))

    # If we only found a date but no counts, try generic number extraction
    if "austin" not in result and "bayarea" not in result and "total" not in result:
        # Look for label-number pairs (with or without spaces)
        pairs = re.findall(r"([A-Za-z\s]+?)\s*(\d+)", text)
        for label, val in pairs:
            label = label.strip().lower()
            if "unsupervised" in label:
                continue  # Skip unsupervised Austin (different chart line)
            if "austin" in label:
                result["austin"] = int(val)
            elif "bay" in label or "sf" in label:
                result["bayarea"] = int(val)
            elif "total" in label or "fleet" in label:
                result["total"] = int(val)

    # If austin is missing but total and bayarea are present, compute it.
    # The tooltip may only show "Unsupervised Austin" (filtered out above),
    # "Bay Area", and "Total". The Austin fleet = Total - Bay Area.
    if "austin" not in result and "total" in result and "bayarea" in result:
        result["austin"] = result["total"] - result["bayarea"]

    return result if ("austin" in result or "bayarea" in result or "total" in result) else None


async def extract_data_via_mouse_hover(page) -> list:
    """Move mouse across chart bars to capture tooltip data."""
    historical = []

    # Find the Fleet Growth chart and scroll it into view
    bbox = await page.evaluate("""
        () => {
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, div, span, p');
            let headingEl = null;
            for (const el of headings) {
                const text = (el.textContent || '').trim();
                if (text === 'Fleet Growth' && el.children.length < 5) {
                    headingEl = el;
                    break;
                }
            }

            const allCharts = document.querySelectorAll('.recharts-wrapper');
            if (allCharts.length === 0) return null;

            // Filter for full-sized charts (not sparklines)
            const charts = [];
            for (const chart of allCharts) {
                const rect = chart.getBoundingClientRect();
                if (rect.height >= 100 && rect.width >= 200) charts.push(chart);
            }
            if (charts.length === 0) return null;

            let target = null;
            if (headingEl) {
                const headingRect = headingEl.getBoundingClientRect();
                let bestDist = Infinity;
                for (const chart of charts) {
                    const rect = chart.getBoundingClientRect();
                    const dist = Math.abs(rect.top - headingRect.bottom);
                    if (dist < bestDist && rect.top >= headingRect.top - 50) {
                        bestDist = dist;
                        target = chart;
                    }
                }
            }
            if (!target) target = charts[0];

            // CRITICAL: Scroll the chart into the CENTER of the viewport
            target.scrollIntoView({block: 'center', behavior: 'instant'});
            return true;
        }
    """)

    if not bbox:
        print("  Could not find chart element for hover")
        return historical

    # Wait for scroll to settle and re-read bbox in viewport coordinates
    await asyncio.sleep(1)

    bbox = await page.evaluate("""
        () => {
            const allCharts = document.querySelectorAll('.recharts-wrapper');
            for (const chart of allCharts) {
                const rect = chart.getBoundingClientRect();
                if (rect.height >= 100 && rect.width >= 200) {
                    const svg = chart.querySelector('svg.recharts-surface');
                    const el = svg || chart;
                    const r = el.getBoundingClientRect();
                    return {x: r.x, y: r.y, width: r.width, height: r.height};
                }
            }
            return null;
        }
    """)

    if not bbox:
        print("  Could not find chart element for hover")
        return historical

    print(f"  Chart bbox: x={bbox['x']:.0f}, y={bbox['y']:.0f}, "
          f"w={bbox['width']:.0f}, h={bbox['height']:.0f}")

    chart_left = bbox["x"] + 60
    chart_right = bbox["x"] + bbox["width"] - 20
    chart_mid_y = bbox["y"] + bbox["height"] * 0.4

    num_samples = 100
    step = (chart_right - chart_left) / num_samples
    seen_dates = set()

    print(f"  Hovering with {num_samples} positions...")

    # Activate chart
    await page.mouse.move(chart_left, chart_mid_y)
    await asyncio.sleep(0.5)

    for i in range(num_samples + 1):
        x = chart_left + (i * step)
        await page.mouse.move(x, chart_mid_y)
        await asyncio.sleep(0.12)

        tooltip_text = await page.evaluate("""
            () => {
                const el = document.querySelector('.recharts-tooltip-wrapper');
                if (!el) return null;
                const style = window.getComputedStyle(el);
                if (style.visibility === 'hidden' || style.opacity === '0') return null;
                const text = el.textContent || '';
                return text.trim().length > 0 ? text.trim() : null;
            }
        """)

        if tooltip_text:
            if len(seen_dates) < 3:
                print(f"    [RAW TOOLTIP] pos={i}: {repr(tooltip_text[:120])}")
            dp = parse_tooltip_text(tooltip_text)
            if dp and dp.get("date") and dp["date"] not in seen_dates:
                seen_dates.add(dp["date"])
                historical.append(dp)
                if len(historical) <= 3 or len(historical) % 10 == 0:
                    print(f"    [{len(historical)}] {dp['date']} - "
                          f"Austin: {dp.get('austin')}, Bay Area: {dp.get('bayarea')}")

    await page.mouse.move(0, 0)
    return historical


# ---------------------------------------------------------------------------

# Helpers

# ---------------------------------------------------------------------------

def validate_data(data: list) -> bool:
    """Validate that data looks like real fleet growth data."""
    if not data or len(data) < 3:
        return False
    unique_dates = set(d.get("date") for d in data if d.get("date"))
    if len(unique_dates) < 3:
        return False
    has_region = any(
        d.get("austin") is not None or d.get("bayarea") is not None
        for d in data
    )
    return has_region


def deduplicate_by_date(data: list) -> list:
    """Remove duplicate entries, keeping the most complete per date."""
    by_date = {}
    for item in data:
        date = item.get("date")
        if not date:
            continue
        if date not in by_date:
            by_date[date] = item
        else:
            existing = by_date[date]
            new_vals = sum(1 for v in item.values() if v is not None)
            old_vals = sum(1 for v in existing.values() if v is not None)
            if new_vals > old_vals:
                by_date[date] = item
    return sorted(by_date.values(), key=lambda x: x["date"])


async def scroll_and_wait_for_charts(page):
    """Scroll through page to trigger lazy-loaded content, then wait for charts."""
    page_height = await page.evaluate("document.body.scrollHeight")
    pos = 0
    while pos < page_height:
        pos += 540
        await page.evaluate(f"window.scrollTo(0, {pos})")
        await asyncio.sleep(0.4)

    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)

    # Scroll to Fleet Growth
    fleet_section = await page.query_selector("text=Fleet Growth")
    if fleet_section:
        await fleet_section.scroll_into_view_if_needed()
        await asyncio.sleep(2)

    # Wait for a real chart to render
    for attempt in range(8):
        has_chart = await page.evaluate("""
            () => {
                const charts = document.querySelectorAll('.recharts-wrapper');
                for (const chart of charts) {
                    const rect = chart.getBoundingClientRect();
                    if (rect.height >= 100 && rect.width >= 200) {
                        const allSvg = chart.querySelectorAll('svg *');
                        return {height: rect.height, width: rect.width, svgCount: allSvg.length};
                    }
                }
                return null;
            }
        """)
        if has_chart and has_chart["svgCount"] > 10:
            print(f"  Chart rendered ({has_chart['width']:.0f}x{has_chart['height']:.0f}, "
                  f"{has_chart['svgCount']} SVG elements)")
            await asyncio.sleep(1)
            return True
        await asyncio.sleep(2)

    print("  WARNING: No chart rendered after waiting")
    return False


async def click_fleet_tab(page, tab_name: str):
    """Click a tab ('Active' or 'Total') on the Fleet Growth chart."""
    clicked = await page.evaluate("""
        (tabName) => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = btn.textContent.trim();
                if (text === tabName) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }
    """, tab_name)
    if clicked:
        print(f"  Clicked '{tab_name}' tab")
        await asyncio.sleep(3)
    else:
        print(f"  '{tab_name}' button not found (may already be selected)")
    return clicked


# ---------------------------------------------------------------------------

# Main orchestrator

# ---------------------------------------------------------------------------

async def _extract_with_strategies(page, captured_api_responses, label=""):
    """Run all extraction strategies and return the first valid result."""
    prefix = f"[{label}] " if label else ""

    # ---- Strategy 1: API responses ----
    print(f"\n  {prefix}Strategy 1: Captured API responses")
    data = extract_fleet_data_from_api_responses(captured_api_responses)
    if data:
        data = deduplicate_by_date(data)
        if validate_data(data):
            print(f"  {prefix}SUCCESS: {len(data)} valid data points from API responses")
            return data
        else:
            print(f"  {prefix}API data failed validation ({len(data)} points)")
    else:
        print(f"  {prefix}No fleet data found in API responses")

    # ---- Strategy 2: React fiber / Recharts props ----
    print(f"\n  {prefix}Strategy 2: React fiber traversal")
    await page.evaluate("""
        () => {
            const charts = document.querySelectorAll('.recharts-wrapper');
            for (const chart of charts) {
                const rect = chart.getBoundingClientRect();
                if (rect.height >= 100 && rect.width >= 200) {
                    chart.scrollIntoView({block: 'center'});
                    break;
                }
            }
        }
    """)
    await asyncio.sleep(2)
    data = await extract_chart_data_from_react(page)
    if data:
        data = deduplicate_by_date(data)
        if validate_data(data):
            print(f"  {prefix}SUCCESS: {len(data)} valid data points from React state")
            return data
        else:
            print(f"  {prefix}React data failed validation ({len(data)} points)")
    else:
        print(f"  {prefix}No fleet data in React fiber tree")

    # ---- Strategy 3: Mouse hover tooltips ----
    print(f"\n  {prefix}Strategy 3: Mouse hover tooltip extraction")
    data = await extract_data_via_mouse_hover(page)
    if data:
        data = deduplicate_by_date(data)
        if validate_data(data):
            print(f"  {prefix}SUCCESS: {len(data)} valid data points from tooltips")
            return data
        else:
            print(f"  {prefix}Tooltip data failed validation ({len(data)} points)")
    else:
        print(f"  {prefix}No data captured from tooltips")

    return []


async def scrape_fleet_growth():
    """Main scraping function. Returns (active_data, total_data)."""
    captured_api_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        # Intercept API responses
        async def capture_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            if "json" in ct and "/api/" in url:
                try:
                    body = await response.text()
                    captured_api_responses.append({"url": url, "body": body})
                except Exception:
                    pass

        page.on("response", capture_response)

        print("Loading robotaxitracker.com...")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2)

        # Scroll and wait for charts to render
        print("Waiting for charts to render...")
        await scroll_and_wait_for_charts(page)

        # ---- Scrape ACTIVE view ----
        print("\n" + "=" * 50)
        print("Scraping ACTIVE fleet growth...")
        print("=" * 50)
        await click_fleet_tab(page, "Active")
        active_data = await _extract_with_strategies(page, captured_api_responses, "Active")

        # ---- Scrape TOTAL view ----
        print("\n" + "=" * 50)
        print("Scraping TOTAL fleet growth...")
        print("=" * 50)
        await click_fleet_tab(page, "Total")
        # Wait for chart to re-render with new data
        await asyncio.sleep(3)
        total_data = await _extract_with_strategies(page, captured_api_responses, "Total")

        await browser.close()

    return active_data, total_data


def save_results(data: list, json_path: Path, csv_path: Path, description: str):
    """Save results to JSON and CSV."""
    from datetime import timezone

    output = {
        "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
        "source": "robotaxitracker.com",
        "description": description,
        "data_points": len(data),
        "data": data,
    }
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  JSON: {json_path}")

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "austin", "bayarea", "total"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"  CSV:  {csv_path}")


def print_data_summary(data: list, label: str):
    """Print a summary table of the extracted data."""
    print(f"\n{'=' * 60}")
    print(f"{label}: {len(data)} data points")
    print(f"{'=' * 60}")
    if not data:
        print("  (no data)")
        return
    print(f"Date range: {data[0]['date']} to {data[-1]['date']}")
    print(f"\nFirst 5 entries:")
    for d in data[:5]:
        print(f"  {d['date']}  Austin: {str(d.get('austin', '-')):>4}  "
              f"Bay Area: {str(d.get('bayarea', '-')):>4}  Total: {str(d.get('total', '-')):>4}")
    print(f"\nLast 5 entries:")
    for d in data[-5:]:
        print(f"  {d['date']}  Austin: {str(d.get('austin', '-')):>4}  "
              f"Bay Area: {str(d.get('bayarea', '-')):>4}  Total: {str(d.get('total', '-')):>4}")


async def main():
    print("=" * 60)
    print("Robotaxi Tracker - Fleet Growth Scraper")
    print("=" * 60)
    print()

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    active_data, total_data = await scrape_fleet_growth()

    success = False

    if active_data:
        print_data_summary(active_data, "ACTIVE FLEET GROWTH")
        save_results(active_data, OUTPUT_JSON_ACTIVE, OUTPUT_CSV_ACTIVE,
                     "Active fleet growth time series")
        success = True
    else:
        print("\nFAILED: Could not extract ACTIVE fleet growth data")

    if total_data:
        print_data_summary(total_data, "TOTAL FLEET GROWTH")
        save_results(total_data, OUTPUT_JSON_TOTAL, OUTPUT_CSV_TOTAL,
                     "Total fleet growth time series")
        success = True
    else:
        print("\nFAILED: Could not extract TOTAL fleet growth data")

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

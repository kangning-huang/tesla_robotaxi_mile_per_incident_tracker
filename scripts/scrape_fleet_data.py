#!/usr/bin/env python3
"""
Scrape Tesla Robotaxi fleet size data from robotaxitracker.com

This script uses Playwright to:
1. Navigate to robotaxitracker.com
2. Extract current fleet size data
3. Extract historical fleet growth data if available
4. Save to JSON for analysis

The site pings Tesla's API every 5 minutes and tracks:
- Number of vehicles in Austin and Bay Area
- Wait times and availability
- Historical fleet growth

Usage:
    pip install playwright
    playwright install chromium
    python scrape_fleet_data.py
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: playwright is required. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)


# Output files
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "fleet_data_scraped.json"
FLEET_DATA_FILE = DATA_DIR / "fleet_data.json"

# URLs
ROBOTAXI_TRACKER_URL = "https://robotaxitracker.com"
NHTSA_PAGE_URL = "https://robotaxitracker.com/nhtsa"


async def scroll_and_wait_for_charts(page):
    """Scroll through the page to trigger lazy-loaded charts."""
    print("  Scrolling to trigger lazy-loaded content...")

    # Get page height
    page_height = await page.evaluate("document.body.scrollHeight")
    viewport_height = 1080

    # Scroll down in steps to trigger IntersectionObserver for lazy elements
    current_position = 0
    while current_position < page_height:
        current_position += viewport_height // 2
        await page.evaluate(f"window.scrollTo(0, {current_position})")
        await asyncio.sleep(0.5)  # Wait for lazy content to load

    # Scroll back to top
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)

    # Now scroll specifically to Fleet Growth section and wait
    try:
        fleet_section = await page.query_selector("text=Fleet Growth")
        if fleet_section:
            await fleet_section.scroll_into_view_if_needed()
            print("  Found Fleet Growth section, waiting for chart...")
            await asyncio.sleep(2)  # Wait for chart animation to complete
    except Exception as e:
        print(f"  Could not scroll to Fleet Growth: {e}")

    # Wait for a properly-sized Recharts chart to render (not sparklines)
    # Sparklines are ~40px tall; the main Fleet Growth chart is 200-400px
    for attempt in range(6):
        has_chart = await page.evaluate("""
            () => {
                const charts = document.querySelectorAll('.recharts-wrapper');
                for (const chart of charts) {
                    const rect = chart.getBoundingClientRect();
                    if (rect.height >= 100 && rect.width >= 200) {
                        return {height: rect.height, width: rect.width};
                    }
                }
                return null;
            }
        """)
        if has_chart:
            print(f"  Recharts chart detected ({has_chart['width']:.0f}x{has_chart['height']:.0f})")
            await asyncio.sleep(1)  # Extra wait for chart data to populate
            break
        await asyncio.sleep(2)
    else:
        print("  No properly-sized Recharts chart found after waiting")


async def extract_fleet_numbers(page) -> dict:
    """Extract fleet size numbers from the page."""
    fleet_data = {
        "austin_vehicles": None,
        "bayarea_vehicles": None,
        "total_vehicles": None,
        "austin_available": None,
        "bayarea_available": None,
    }

    # Wait for page to load dynamic content
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)  # Extra wait for JS rendering

    # Scroll through page to trigger lazy-loaded charts
    await scroll_and_wait_for_charts(page)

    # Get page content
    content = await page.content()

    # Try to find fleet numbers using various patterns
    # Pattern 1: Look for specific text patterns (based on robotaxitracker.com layout)
    patterns = [
        # Fleet Growth section patterns: "TOTAL FLEET" "BAY AREA" "AUSTIN" followed by numbers
        (r"TOTAL\s*FLEET\s*(\d+)", "total_vehicles"),
        (r"BAY\s*AREA\s*(\d+)", "bayarea_vehicles"),
        (r"AUSTIN\s*(\d+)", "austin_vehicles"),
        # Alternative patterns
        (r"Austin[:\s]*(\d+)\s*(?:vehicles?|cars?)?", "austin_vehicles"),
        (r"Bay\s*Area[:\s]*(\d+)\s*(?:vehicles?|cars?)?", "bayarea_vehicles"),
        (r"Total[:\s]*(\d+)\s*(?:vehicles?|cars?|robotaxis?)?", "total_vehicles"),
        (r"(\d+)\s*(?:vehicles?|cars?)\s*(?:in\s*)?Austin", "austin_vehicles"),
        (r"(\d+)\s*(?:vehicles?|cars?)\s*(?:in\s*)?(?:Bay\s*Area|SF|San\s*Francisco)", "bayarea_vehicles"),
    ]

    for pattern, key in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match and fleet_data[key] is None:
            fleet_data[key] = int(match.group(1))

    # Try to extract from specific elements using JavaScript evaluation
    # This handles dynamic React/Vue components better
    try:
        js_extraction = """
        () => {
            const result = {};
            // Look for text containing fleet numbers in the Fleet Growth section
            const allText = document.body.innerText;

            // Pattern: TOTAL FLEET followed by number on next line or nearby
            const totalMatch = allText.match(/TOTAL\\s*FLEET[\\s\\n]*(\\d+)/i);
            if (totalMatch) result.total = parseInt(totalMatch[1]);

            const bayMatch = allText.match(/BAY\\s*AREA[\\s\\n]*(\\d+)/i);
            if (bayMatch) result.bayarea = parseInt(bayMatch[1]);

            const austinMatch = allText.match(/AUSTIN[\\s\\n]*(\\d+)/i);
            if (austinMatch) result.austin = parseInt(austinMatch[1]);

            return result;
        }
        """
        js_result = await page.evaluate(js_extraction)
        if js_result:
            if js_result.get("total") and fleet_data["total_vehicles"] is None:
                fleet_data["total_vehicles"] = js_result["total"]
            if js_result.get("bayarea") and fleet_data["bayarea_vehicles"] is None:
                fleet_data["bayarea_vehicles"] = js_result["bayarea"]
            if js_result.get("austin") and fleet_data["austin_vehicles"] is None:
                fleet_data["austin_vehicles"] = js_result["austin"]
    except Exception as e:
        print(f"  JS extraction failed: {e}")

    # Try to extract from specific elements
    selectors_to_try = [
        # Common dashboard element patterns
        (".fleet-count", "total_vehicles"),
        (".austin-count", "austin_vehicles"),
        (".bayarea-count", "bayarea_vehicles"),
        ("[data-fleet-austin]", "austin_vehicles"),
        ("[data-fleet-bayarea]", "bayarea_vehicles"),
        # Stats cards
        (".stat-card:has-text('Austin') .stat-value", "austin_vehicles"),
        (".stat-card:has-text('Bay') .stat-value", "bayarea_vehicles"),
    ]

    for selector, key in selectors_to_try:
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
                numbers = re.findall(r'\d+', text)
                if numbers and fleet_data[key] is None:
                    fleet_data[key] = int(numbers[0])
        except Exception:
            pass

    # Calculate total if we have components
    if fleet_data["austin_vehicles"] and fleet_data["bayarea_vehicles"]:
        fleet_data["total_vehicles"] = fleet_data["austin_vehicles"] + fleet_data["bayarea_vehicles"]

    return fleet_data


async def extract_historical_data(page, captured_api_responses=None) -> list:
    """Extract historical fleet data using multiple strategies.

    Strategies tried in order:
    1. Network API interception (most reliable - captures raw JSON from API calls)
    2. React/Next.js state extraction (access chart data from component props)
    3. Playwright native mouse hover (triggers real browser events for tooltips)
    """
    historical = []

    # Strategy 1: Extract from captured API responses
    if captured_api_responses:
        print("  Strategy 1: Checking captured API responses...")
        historical = extract_fleet_data_from_api_responses(captured_api_responses)
        if historical:
            historical = deduplicate_by_date(historical)
            if validate_historical_data(historical, "Strategy 1"):
                print(f"  -> Found {len(historical)} valid data points from API responses")
                historical.sort(key=lambda x: x.get("date", ""))
                return historical
            else:
                print(f"  -> API data rejected by validation, trying next strategy...")
                historical = []
        print("  -> No valid fleet data found in API responses")

    # Strategy 2: Extract from React/Next.js page state
    print("  Strategy 2: Extracting from React/Next.js state...")
    historical = await extract_chart_data_from_scripts(page)
    if historical:
        historical = deduplicate_by_date(historical)
        if validate_historical_data(historical, "Strategy 2"):
            print(f"  -> Found {len(historical)} valid data points from page state")
            historical.sort(key=lambda x: x.get("date", ""))
            return historical
        else:
            print(f"  -> Page state data rejected by validation, trying next strategy...")
            historical = []
    print("  -> No valid data found in page state")

    # Strategy 3: Native mouse hover for tooltip extraction
    print("  Strategy 3: Using native mouse hover for tooltips...")
    try:
        historical = await extract_data_via_mouse_hover(page)
        if historical:
            historical = deduplicate_by_date(historical)
            if validate_historical_data(historical, "Strategy 3"):
                print(f"  -> Found {len(historical)} valid data points from tooltips")
                historical.sort(key=lambda x: x.get("date", ""))
                return historical
            else:
                print(f"  -> Tooltip data rejected by validation")
                historical = []
        print("  -> No valid tooltips captured")
    except Exception as e:
        print(f"  -> Mouse hover failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"  No valid historical data found from any strategy")
    return historical


def extract_fleet_data_from_api_responses(captured_responses: list) -> list:
    """Parse captured API responses for fleet/chart data arrays."""
    historical = []

    for resp in captured_responses:
        body = resp.get("body", "")
        url = resp.get("url", "")

        try:
            # Try to parse as JSON
            data = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            # Try to find JSON arrays embedded in the response
            data = None
            # Look for array patterns containing date-like data
            for match in re.finditer(r'\[[\s\S]*?\{[^}]*"(?:date|Date|timestamp)"[^}]*\}[\s\S]*?\]', body):
                try:
                    data = json.loads(match.group(0))
                    break
                except json.JSONDecodeError:
                    continue

        if data is None:
            continue

        # Handle different response shapes
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Look for arrays nested in the response
            for key in ["data", "result", "results", "items", "fleet", "vehicles",
                        "chartData", "chart_data", "fleetData", "fleet_data",
                        "historicalData", "historical_data", "series", "records"]:
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            # Also check nested structures like { result: { data: [...] } }
            if not items:
                for val in data.values():
                    if isinstance(val, dict):
                        for subkey, subval in val.items():
                            if isinstance(subval, list) and len(subval) > 1:
                                items = subval
                                break
                    if items:
                        break

        # Check if items have fleet-specific keys before processing
        has_fleet_key = False
        for item in items:
            if isinstance(item, dict):
                for key in item.keys():
                    kl = key.lower().replace("_", "").replace("-", "")
                    if any(kw in kl for kw in ["austin", "bay", "sf", "fleet", "vehicle"]):
                        has_fleet_key = True
                        break
            if has_fleet_key:
                break
        if not has_fleet_key:
            continue  # Skip datasets without fleet-specific keys

        fleet_points = []
        for item in items:
            if not isinstance(item, dict):
                continue
            # Look for date field
            date_val = None
            for date_key in ["date", "Date", "timestamp", "day", "created_at", "scraped_at"]:
                if date_key in item:
                    date_val = item[date_key]
                    break
            if not date_val:
                continue

            # Normalize date
            date_str = normalize_date_string(str(date_val))
            if not date_str:
                continue

            # Look for fleet count fields
            austin = None
            bayarea = None
            total = None
            for key, val in item.items():
                key_lower = key.lower().replace("_", "").replace("-", "")
                if val is not None and isinstance(val, (int, float)):
                    val = int(val)
                    if "austin" in key_lower:
                        austin = val
                    elif "bay" in key_lower or "sf" in key_lower or "sanfran" in key_lower:
                        bayarea = val
                    elif "total" in key_lower or "fleet" in key_lower:
                        total = val

            if austin is not None or bayarea is not None or total is not None:
                fleet_points.append({
                    "date": date_str,
                    "austin": austin,
                    "bayarea": bayarea,
                    "total": total,
                })

        if fleet_points and len(fleet_points) > len(historical):
            print(f"    Found {len(fleet_points)} fleet data points from {url[:80]}")
            historical = fleet_points

    return historical


def normalize_date_string(date_val: str) -> str:
    """Normalize various date formats to YYYY-MM-DD."""
    if not date_val:
        return None

    # Already ISO format
    match = re.match(r'^(\d{4})-(\d{2})-(\d{2})', date_val)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    # Unix timestamp (seconds or milliseconds)
    try:
        ts = float(date_val)
        if ts > 1e12:  # milliseconds
            ts = ts / 1000
        if 1e9 < ts < 2e9:  # Reasonable epoch range (2001-2033)
            dt = datetime.fromtimestamp(ts)
            return dt.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        pass

    # Try common date formats
    for fmt in ["%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ"]:
        try:
            dt = datetime.strptime(date_val.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def validate_historical_data(data: list, label: str = "historical") -> bool:
    """Validate that extracted data looks like real fleet historical data.

    Rejects data that is:
    - Too few entries
    - All the same date (not real historical time series)
    - Missing region breakdowns entirely (likely from wrong data source)
    """
    if not data or len(data) < 3:
        print(f"    [{label}] Validation: too few entries ({len(data) if data else 0})")
        return False

    # Check date diversity - real historical data should span multiple dates
    unique_dates = set(item.get("date") for item in data if item.get("date"))
    if len(unique_dates) < 3:
        print(f"    [{label}] Validation failed: only {len(unique_dates)} unique dates "
              f"out of {len(data)} entries")
        return False

    # Check if at least some entries have region-specific data (austin or bayarea)
    entries_with_region = sum(
        1 for item in data
        if item.get("austin") is not None or item.get("bayarea") is not None
    )
    if entries_with_region == 0:
        print(f"    [{label}] Validation failed: no entries have austin/bayarea values")
        return False

    print(f"    [{label}] Validation passed: {len(data)} entries, "
          f"{len(unique_dates)} unique dates, {entries_with_region} with region data")
    return True


def deduplicate_by_date(data: list) -> list:
    """Remove duplicate entries, keeping the most complete entry per date."""
    if not data:
        return data

    by_date = {}
    for item in data:
        date = item.get("date")
        if not date:
            continue
        if date not in by_date:
            by_date[date] = item
        else:
            # Keep the entry with more non-null values
            existing = by_date[date]
            new_non_null = sum(1 for v in item.values() if v is not None)
            old_non_null = sum(1 for v in existing.values() if v is not None)
            if new_non_null > old_non_null:
                by_date[date] = item

    result = list(by_date.values())
    if len(result) < len(data):
        print(f"    Deduplicated: {len(data)} -> {len(result)} entries")
    return result


async def extract_data_via_mouse_hover(page) -> list:
    """Extract chart data using Playwright's native page.mouse.move().

    Unlike synthetic JavaScript MouseEvents, native mouse movements go through
    the browser's event pipeline and reliably trigger Recharts tooltips.
    """
    historical = []

    # Scroll to Fleet Growth section
    fleet_section = await page.query_selector("text=Fleet Growth")
    if not fleet_section:
        fleet_section = await page.query_selector("text=车队增长")
    if fleet_section:
        await fleet_section.scroll_into_view_if_needed()
        await asyncio.sleep(2)

    # Find the Fleet Growth chart specifically (not any chart on the page)
    # Use JS to find the chart closest to the Fleet Growth heading, skipping sparklines
    bbox = await page.evaluate("""
        () => {
            // Find Fleet Growth heading
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, div, span, p');
            let headingRect = null;
            for (const el of headings) {
                const text = (el.textContent || '').trim();
                if ((text === 'Fleet Growth' || text === '车队增长' ||
                     text === 'Flottenentwicklung' || text === 'Croissance de la flotte') &&
                    el.children.length < 5) {
                    headingRect = el.getBoundingClientRect();
                    break;
                }
            }

            // Find all recharts charts, filtering out sparklines (height < 100)
            const allCharts = document.querySelectorAll('.recharts-wrapper');
            if (allCharts.length === 0) return null;

            const charts = [];
            for (const chart of allCharts) {
                const rect = chart.getBoundingClientRect();
                if (rect.height >= 100 && rect.width >= 200) {
                    charts.push(chart);
                }
            }

            // Log for diagnostics
            console.log(`Found ${allCharts.length} total charts, ${charts.length} full-sized`);

            if (charts.length === 0) {
                // If no full-sized charts, fall back to largest chart available
                let largest = null;
                let largestArea = 0;
                for (const chart of allCharts) {
                    const rect = chart.getBoundingClientRect();
                    const area = rect.width * rect.height;
                    if (area > largestArea) {
                        largestArea = area;
                        largest = chart;
                    }
                }
                if (!largest) return null;
                const svg = largest.querySelector('svg.recharts-surface');
                const target = svg || largest;
                const rect = target.getBoundingClientRect();
                return {x: rect.x, y: rect.y, width: rect.width, height: rect.height, fallback: 'largest'};
            }

            let targetChart = null;
            if (headingRect) {
                // Find the full-sized chart closest (below) to the Fleet Growth heading
                let bestDist = Infinity;
                for (const chart of charts) {
                    const rect = chart.getBoundingClientRect();
                    const dist = Math.abs(rect.top - headingRect.bottom);
                    if (dist < bestDist && rect.top >= headingRect.top - 50) {
                        bestDist = dist;
                        targetChart = chart;
                    }
                }
            }

            if (!targetChart) {
                // Fallback: use the first full-sized chart
                targetChart = charts[0];
            }

            const svg = targetChart.querySelector('svg.recharts-surface');
            const target = svg || targetChart;
            const rect = target.getBoundingClientRect();
            return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
        }
    """)

    if not bbox:
        # Fallback: try simple selectors
        chart_selectors = ["svg.recharts-surface", ".recharts-wrapper"]
        chart_element = None
        for selector in chart_selectors:
            chart_element = await page.query_selector(selector)
            if chart_element:
                print(f"  Fallback: found chart via {selector}")
                break
        if not chart_element:
            print("  Could not find any chart element")
            return historical
        await chart_element.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        bbox = await chart_element.bounding_box()

    if not bbox:
        print("  Could not get chart bounding box")
        return historical

    if bbox.get('fallback') == 'largest':
        print(f"  WARNING: No full-sized chart found, using largest available")

    print(f"  Chart bbox: x={bbox['x']:.0f}, y={bbox['y']:.0f}, "
          f"w={bbox['width']:.0f}, h={bbox['height']:.0f}")

    if bbox['height'] < 100:
        print(f"  WARNING: Chart too small (height={bbox['height']:.0f}px), likely a sparkline")
        print("  The main Fleet Growth chart may not have loaded. Skipping hover.")
        return historical

    # Calculate hover area - stay within the plot area (inside axes)
    chart_left = bbox['x'] + 60   # Skip y-axis labels
    chart_right = bbox['x'] + bbox['width'] - 20  # Skip right padding
    chart_mid_y = bbox['y'] + bbox['height'] * 0.4  # Slightly above middle (hit bar area)

    num_samples = 80  # More samples for better coverage
    step = (chart_right - chart_left) / num_samples
    seen_dates = set()
    debug_tooltip_count = 0

    print(f"  Hovering across chart with {num_samples} positions using native mouse...")

    # First move to chart area to activate it
    await page.mouse.move(chart_left, chart_mid_y)
    await asyncio.sleep(0.5)

    for i in range(num_samples + 1):
        x = chart_left + (i * step)

        # Use Playwright's native mouse.move - this generates real browser events
        # that Recharts' internal event handler on the SVG overlay will pick up
        await page.mouse.move(x, chart_mid_y)
        await asyncio.sleep(0.15)  # Give tooltip time to render

        # Check for tooltip content - use only Recharts-specific selector
        tooltip_text = await page.evaluate("""
            () => {
                // Only look at Recharts tooltip wrapper (not generic tooltips)
                const el = document.querySelector('.recharts-tooltip-wrapper');
                if (!el) return null;

                const style = window.getComputedStyle(el);
                // Recharts hides tooltip with visibility:hidden or opacity:0
                if (style.visibility === 'hidden' || style.opacity === '0') {
                    return null;
                }

                const text = el.textContent || '';
                if (text.trim().length > 0) {
                    return text.trim();
                }
                return null;
            }
        """)

        if tooltip_text:
            # Debug: log first few raw tooltip texts
            if debug_tooltip_count < 5:
                print(f"    [RAW TOOLTIP {debug_tooltip_count}] pos={i}/{num_samples}: {repr(tooltip_text[:150])}")
                debug_tooltip_count += 1

            data_point = parse_tooltip_text(tooltip_text)
            if data_point and data_point.get("date") and data_point["date"] not in seen_dates:
                seen_dates.add(data_point["date"])
                historical.append(data_point)
                if len(historical) <= 3 or len(historical) % 10 == 0:
                    print(f"    [{len(historical)}] {data_point['date']} - "
                          f"Austin: {data_point.get('austin')}, "
                          f"Bay Area: {data_point.get('bayarea')}, "
                          f"Total: {data_point.get('total')}")

    # Move mouse away to dismiss tooltip
    await page.mouse.move(0, 0)

    return historical


async def extract_chart_data_from_scripts(page) -> list:
    """Try to extract chart data from React/Next.js state, scripts, or DOM.

    Strategies:
    1. __NEXT_DATA__ (Next.js server-side props)
    2. React fiber traversal (finds chart data in component props)
    3. Window/global object scan
    4. Script tag parsing
    5. Recharts internal state via all .recharts-wrapper elements
    """
    historical = []

    try:
        chart_data = await page.evaluate("""
            () => {
                const candidates = [];

                // Helper: check if an array looks like fleet data
                function isFleetData(arr) {
                    if (!Array.isArray(arr) || arr.length < 3) return false;
                    const sample = arr[0];
                    if (typeof sample !== 'object' || sample === null) return false;
                    const keys = Object.keys(sample).map(k => k.toLowerCase());
                    // Must have something date-like
                    const hasDate = keys.some(k =>
                        k.includes('date') || k.includes('time') || k.includes('day')
                    );
                    // Must have fleet-specific or region-specific keys
                    // Generic 'total' or 'count' alone is NOT sufficient (too many false positives)
                    const hasFleetKey = keys.some(k =>
                        k.includes('austin') || k.includes('bay') || k.includes('sf') ||
                        k.includes('sanfran') || k.includes('fleet') || k.includes('vehicle')
                    );
                    return hasDate && hasFleetKey;
                }

                // Helper: recursively search object for fleet data arrays
                function findFleetArrays(obj, depth, path) {
                    if (depth > 6 || !obj || typeof obj !== 'object') return;
                    if (Array.isArray(obj) && isFleetData(obj)) {
                        candidates.push({data: obj, source: path, size: obj.length});
                        return;
                    }
                    try {
                        const keys = Array.isArray(obj) ? [] : Object.keys(obj);
                        for (const key of keys.slice(0, 50)) { // Limit keys to avoid perf issues
                            try {
                                findFleetArrays(obj[key], depth + 1, path + '.' + key);
                            } catch(e) {}
                        }
                    } catch(e) {}
                }

                // Method 1: __NEXT_DATA__ (Next.js apps store page props here)
                if (window.__NEXT_DATA__) {
                    console.log('[scraper] Found __NEXT_DATA__');
                    findFleetArrays(window.__NEXT_DATA__, 0, '__NEXT_DATA__');
                }

                // Method 2: React fiber traversal - target Fleet Growth chart specifically
                // First, find the Fleet Growth section to narrow our search
                const fleetSection = (() => {
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, div, span, p');
                    for (const el of headings) {
                        const text = (el.textContent || '').trim();
                        // Match the exact heading text (not deeply nested content)
                        if ((text === 'Fleet Growth' || text === '车队增长' ||
                             text === 'Flottenentwicklung' || text === 'Croissance de la flotte') &&
                            el.children.length < 5) {
                            // Walk up to find the containing section with a chart
                            let parent = el.parentElement;
                            for (let i = 0; i < 10 && parent; i++) {
                                if (parent.querySelector('.recharts-wrapper')) {
                                    return parent;
                                }
                                parent = parent.parentElement;
                            }
                        }
                    }
                    return null;
                })();

                const chartContainers = fleetSection
                    ? fleetSection.querySelectorAll('.recharts-wrapper, .recharts-responsive-container')
                    : document.querySelectorAll('.recharts-wrapper, .recharts-responsive-container, [class*="chart"], [class*="Chart"]');
                console.log('[scraper] Targeting ' + (fleetSection ? 'Fleet Growth section' : 'all charts') +
                    ': found ' + chartContainers.length + ' chart containers');
                for (const container of chartContainers) {
                    // React fiber keys are randomized per build, find them dynamically
                    const fiberKeys = Object.keys(container).filter(k =>
                        k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$') ||
                        k.startsWith('__reactProps$')
                    );
                    for (const fiberKey of fiberKeys) {
                        let fiber = container[fiberKey];
                        let visited = 0;
                        while (fiber && visited < 50) {
                            visited++;
                            // Check memoizedProps.data (Recharts passes data as prop)
                            if (fiber.memoizedProps) {
                                const props = fiber.memoizedProps;
                                if (props.data && isFleetData(props.data)) {
                                    candidates.push({
                                        data: props.data,
                                        source: 'fiber.memoizedProps.data',
                                        size: props.data.length
                                    });
                                }
                                // Also check children props
                                if (props.children) {
                                    const children = Array.isArray(props.children)
                                        ? props.children : [props.children];
                                    for (const child of children) {
                                        if (child && child.props && child.props.data &&
                                            isFleetData(child.props.data)) {
                                            candidates.push({
                                                data: child.props.data,
                                                source: 'fiber.child.props.data',
                                                size: child.props.data.length
                                            });
                                        }
                                    }
                                }
                            }
                            // Check memoizedState (hooks data)
                            if (fiber.memoizedState) {
                                findFleetArrays(fiber.memoizedState, 0, 'fiber.memoizedState');
                            }
                            fiber = fiber.return;
                        }
                    }
                }

                // Method 3: Scan window/global for data
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

                // Method 4: Parse script tags for embedded JSON data
                const scripts = document.querySelectorAll('script');
                for (const script of scripts) {
                    const text = script.textContent || '';
                    if (text.length < 100 || text.length > 500000) continue;
                    // Look for JSON arrays with date fields
                    const patterns = [
                        /\[\s*\{[^}]*"date"[^]*?\}\s*\]/g,
                        /\[\s*\{[^}]*"Date"[^]*?\}\s*\]/g,
                        /\[\s*\{[^}]*"timestamp"[^]*?\}\s*\]/g,
                    ];
                    for (const pattern of patterns) {
                        let match;
                        while ((match = pattern.exec(text)) !== null) {
                            try {
                                const parsed = JSON.parse(match[0]);
                                if (isFleetData(parsed)) {
                                    candidates.push({
                                        data: parsed,
                                        source: 'script_tag',
                                        size: parsed.length
                                    });
                                }
                            } catch(e) {}
                        }
                    }
                    // Also look for self.__next_f.push patterns (Next.js RSC payload)
                    if (text.includes('self.__next_f')) {
                        // Extract JSON chunks from RSC payload
                        const rscMatches = text.matchAll(/self\.__next_f\.push\(\s*\[\s*\d+\s*,\s*"([^"]+)"/g);
                        for (const rscMatch of rscMatches) {
                            try {
                                const decoded = rscMatch[1]
                                    .replace(/\\n/g, '')
                                    .replace(/\\"/g, '"')
                                    .replace(/\\\\/g, '\\\\');
                                // Find JSON arrays in the decoded chunk
                                const arrMatch = decoded.match(/\[[\s\S]*?\{[^}]*date[^}]*\}[\s\S]*?\]/i);
                                if (arrMatch) {
                                    const parsed = JSON.parse(arrMatch[0]);
                                    if (isFleetData(parsed)) {
                                        candidates.push({
                                            data: parsed,
                                            source: 'next_rsc_payload',
                                            size: parsed.length
                                        });
                                    }
                                }
                            } catch(e) {}
                        }
                    }
                }

                // Score and rank candidates by fleet-likeness (not just size)
                if (candidates.length > 0) {
                    for (const c of candidates) {
                        let score = 0;
                        const sampleKeys = Object.keys(c.data[0]).map(k => k.toLowerCase());
                        // Region-specific keys are strong signals
                        if (sampleKeys.some(k => k.includes('austin'))) score += 1000;
                        if (sampleKeys.some(k => k.includes('bay') || k.includes('sf'))) score += 1000;
                        if (sampleKeys.some(k => k.includes('fleet') || k.includes('vehicle'))) score += 500;
                        // Check date diversity (sample first 20 items)
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
                        // Larger datasets slightly preferred (capped)
                        score += Math.min(c.size, 200);
                        c.score = score;
                    }
                    candidates.sort((a, b) => b.score - a.score);
                    console.log('[scraper] Found ' + candidates.length + ' candidates, best: ' +
                        candidates[0].source + ' (score=' + candidates[0].score +
                        ', ' + candidates[0].size + ' items)');
                    for (const c of candidates.slice(0, 5)) {
                        console.log('  - ' + c.source + ': score=' + c.score + ', size=' + c.size);
                    }
                    return {
                        data: candidates[0].data,
                        source: candidates[0].source,
                        all_sources: candidates.map(c => c.source + ':' + c.size + ':score=' + c.score)
                    };
                }

                return null;
            }
        """)

        if chart_data and chart_data.get("data"):
            source = chart_data.get("source", "unknown")
            all_sources = chart_data.get("all_sources", [])
            print(f"    Best source: {source}")
            if all_sources:
                print(f"    All sources found: {all_sources}")

            for item in chart_data["data"]:
                if isinstance(item, dict):
                    # Flexible field extraction
                    date_val = None
                    for key in ["date", "Date", "timestamp", "day", "created_at"]:
                        if key in item:
                            date_val = str(item[key])
                            break
                    if not date_val:
                        continue

                    date_str = normalize_date_string(date_val)
                    if not date_str:
                        continue

                    # Extract counts with flexible field names
                    austin = None
                    bayarea = None
                    total = None
                    for key, val in item.items():
                        if val is None or not isinstance(val, (int, float)):
                            continue
                        key_lower = key.lower().replace("_", "").replace("-", "")
                        if "austin" in key_lower:
                            austin = int(val)
                        elif "bay" in key_lower or "sf" in key_lower:
                            bayarea = int(val)
                        elif "total" in key_lower or "fleet" in key_lower:
                            total = int(val)

                    if austin is not None or bayarea is not None or total is not None:
                        historical.append({
                            "date": date_str,
                            "bayarea": bayarea,
                            "austin": austin,
                            "total": total,
                        })

            print(f"  Found {len(historical)} data points from page state ({source})")
    except Exception as e:
        print(f"  Could not extract chart data from scripts: {e}")
        import traceback
        traceback.print_exc()

    return historical


def parse_tooltip_text(text: str) -> dict:
    """Parse tooltip text to extract date and fleet numbers."""
    if not text:
        return None

    result = {}

    # Clean up the text
    text = text.strip()

    # Debug: print first few tooltip texts to understand format
    if not hasattr(parse_tooltip_text, '_debug_count'):
        parse_tooltip_text._debug_count = 0
    if parse_tooltip_text._debug_count < 5:
        print(f"    [DEBUG] Tooltip text: {repr(text[:200])}")
        parse_tooltip_text._debug_count += 1

    # Comprehensive month name mappings for multiple languages
    month_map = {
        # English short
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        # English full
        "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        # German
        "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
        "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,
        # French
        "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
        "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
        # Spanish
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    }

    # Try to extract date - various formats ordered by specificity
    # Most specific patterns first to avoid false matches
    date_patterns = [
        # Asian formats (most specific due to unique characters)
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', 'cjk'),  # Chinese/Japanese: 2025年6月22日
        (r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', 'korean'),  # Korean: 2025년 6월 22일

        # ISO format (very specific)
        (r'(\d{4})-(\d{2})-(\d{2})', 'iso'),  # ISO: 2025-06-22

        # Full month name formats (before short names to avoid partial matches)
        (r'([A-Za-zäöüéèàùâêîôûëïç]+)\s+(\d{1,2}),?\s+(\d{4})', 'month_day_year'),  # June 22, 2025
        (r'(\d{1,2})\.?\s+([A-Za-zäöüéèàùâêîôûëïç]+),?\s+(\d{4})', 'day_month_year'),  # 22 June 2025 or 22. Juni 2025

        # Numeric formats (least specific, check last)
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'mdy_slash'),  # US: 6/22/2025 (assume M/D/Y for en-US locale)
        (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', 'dmy_dot'),  # European: 22.06.2025
    ]

    for pattern, fmt_name in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            try:
                if fmt_name == 'cjk' or fmt_name == 'korean':
                    # Year, Month, Day order
                    result["date"] = f"{groups[0]}-{int(groups[1]):02d}-{int(groups[2]):02d}"
                elif fmt_name == 'iso':
                    result["date"] = f"{groups[0]}-{groups[1]}-{groups[2]}"
                elif fmt_name == 'month_day_year':
                    # Month name, Day, Year (e.g., "June 22, 2025")
                    month_name = groups[0].lower()
                    month_num = month_map.get(month_name) or month_map.get(month_name[:3])
                    if month_num:
                        result["date"] = f"{groups[2]}-{month_num:02d}-{int(groups[1]):02d}"
                elif fmt_name == 'day_month_year':
                    # Day, Month name, Year (e.g., "22 June 2025")
                    month_name = groups[1].lower()
                    month_num = month_map.get(month_name) or month_map.get(month_name[:3])
                    if month_num:
                        result["date"] = f"{groups[2]}-{month_num:02d}-{int(groups[0]):02d}"
                elif fmt_name == 'mdy_slash':
                    # US format: Month/Day/Year
                    result["date"] = f"{groups[2]}-{int(groups[0]):02d}-{int(groups[1]):02d}"
                elif fmt_name == 'dmy_dot':
                    # European format: Day.Month.Year
                    result["date"] = f"{groups[2]}-{int(groups[1]):02d}-{int(groups[0]):02d}"

                if result.get("date"):
                    # Debug: show which pattern matched
                    if parse_tooltip_text._debug_count <= 5:
                        print(f"    [DEBUG] Matched pattern '{fmt_name}': {groups} -> {result.get('date')}")
                    break
            except (ValueError, IndexError) as e:
                # If parsing fails, try next pattern
                if parse_tooltip_text._debug_count <= 5:
                    print(f"    [DEBUG] Pattern '{fmt_name}' failed: {e}")
                continue

    if not result.get("date"):
        return None

    # Extract Bay Area number
    bay_match = re.search(r'Bay\s*Area[:\s]*(\d+)', text, re.IGNORECASE)
    if bay_match:
        result["bayarea"] = int(bay_match.group(1))

    # Extract Austin number
    austin_match = re.search(r'Austin[:\s]*(\d+)', text, re.IGNORECASE)
    if austin_match:
        result["austin"] = int(austin_match.group(1))

    # Extract total (总车队 in Chinese or "Total")
    total_match = re.search(r'(?:总车队|Total)[:\s]*(\d+)', text, re.IGNORECASE)
    if total_match:
        result["total"] = int(total_match.group(1))

    return result


async def click_fleet_tab(page, tab_name: str) -> bool:
    """Click the 'Active' or 'Total' tab on the Fleet Growth chart.

    Args:
        page: Playwright page object.
        tab_name: 'Active' or 'Total' (English). Also matches Chinese: '活跃' / '总计'.

    Returns:
        True if tab was found and clicked, False otherwise.
    """
    # Map of tab names in various languages
    tab_variants = {
        "Active": ["Active", "活跃", "Aktiv", "Actif", "Activo"],
        "Total": ["Total", "总计", "Gesamt", "Totale"],
    }

    variants = tab_variants.get(tab_name, [tab_name])

    # First scroll to Fleet Growth section
    try:
        fleet_section = await page.query_selector("text=Fleet Growth")
        if not fleet_section:
            fleet_section = await page.query_selector("text=车队增长")
        if fleet_section:
            await fleet_section.scroll_into_view_if_needed()
            await asyncio.sleep(1)
    except Exception:
        pass

    # Try clicking tab using text selectors
    for variant in variants:
        try:
            # Try exact text match on button-like elements
            selectors = [
                f"button:has-text('{variant}')",
                f"[role='tab']:has-text('{variant}')",
                f"text='{variant}'",
                f"span:has-text('{variant}')",
                f"div:has-text('{variant}')",
            ]
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            await element.click()
                            print(f"  Clicked '{variant}' tab (selector: {selector})")
                            await asyncio.sleep(2)  # Wait for chart to re-render
                            return True
                except Exception:
                    continue
        except Exception:
            continue

    # Fallback: try JavaScript click
    try:
        clicked = await page.evaluate("""
            (variants) => {
                // Find all clickable elements near the Fleet Growth section
                const elements = document.querySelectorAll('button, [role="tab"], span, div');
                for (const el of elements) {
                    const text = (el.textContent || '').trim();
                    for (const variant of variants) {
                        if (text === variant || text.toLowerCase() === variant.toLowerCase()) {
                            el.click();
                            return true;
                        }
                    }
                }
                return false;
            }
        """, variants)
        if clicked:
            print(f"  Clicked '{tab_name}' tab via JavaScript")
            await asyncio.sleep(2)
            return True
    except Exception as e:
        print(f"  JS tab click failed: {e}")

    print(f"  Warning: Could not find '{tab_name}' tab")
    return False


async def extract_active_fleet_numbers(page) -> dict:
    """Extract active fleet numbers after clicking the Active tab.

    Returns dict with active fleet counts, or empty values if not found.
    """
    active_data = {
        "austin_active": None,
        "bayarea_active": None,
        "total_active": None,
    }

    content = await page.content()

    # The Active view shows a "Total Fleet" or "总车队" number
    # Look for patterns in the visible text
    try:
        js_result = await page.evaluate("""
            () => {
                const result = {};
                const allText = document.body.innerText;

                // After clicking Active tab, the total fleet number updates
                // Look for "TOTAL FLEET" or "总车队" followed by a number
                const totalMatch = allText.match(/(?:TOTAL\\s*FLEET|总车队)[\\s\\n]*(\\d+)/i);
                if (totalMatch) result.total = parseInt(totalMatch[1]);

                // Look for region-specific numbers
                const austinMatch = allText.match(/AUSTIN[\\s\\n]*(\\d+)/i);
                if (austinMatch) result.austin = parseInt(austinMatch[1]);

                const bayMatch = allText.match(/BAY\\s*AREA[\\s\\n]*(\\d+)/i);
                if (bayMatch) result.bayarea = parseInt(bayMatch[1]);

                return result;
            }
        """)
        if js_result:
            if js_result.get("total"):
                active_data["total_active"] = js_result["total"]
            if js_result.get("austin"):
                active_data["austin_active"] = js_result["austin"]
            if js_result.get("bayarea"):
                active_data["bayarea_active"] = js_result["bayarea"]
    except Exception as e:
        print(f"  JS active fleet extraction failed: {e}")

    # Also try regex on HTML content
    patterns = [
        (r"TOTAL\s*FLEET\s*(\d+)", "total_active"),
        (r"总车队\s*(\d+)", "total_active"),
        (r"AUSTIN\s*(\d+)", "austin_active"),
        (r"BAY\s*AREA\s*(\d+)", "bayarea_active"),
    ]
    for pattern, key in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match and active_data[key] is None:
            active_data[key] = int(match.group(1))

    return active_data


async def extract_active_historical_data(page, captured_api_responses=None) -> list:
    """Extract historical active fleet data after clicking the Active tab.

    Uses the same multi-strategy approach as extract_historical_data():
    1. React/Next.js state extraction (chart data should reflect Active tab)
    2. Native mouse hover for tooltip extraction

    Note: captured_api_responses from before the tab click are NOT used here,
    since they contain Total fleet data, not Active fleet data.
    """
    # After clicking Active tab, the React state should now hold active data.
    # Re-run extraction strategies on the updated page state.
    print("  Extracting active chart data from page state...")
    historical = await extract_chart_data_from_scripts(page)
    if historical:
        historical = deduplicate_by_date(historical)
        if validate_historical_data(historical, "Active-State"):
            print(f"  -> Found {len(historical)} valid active data points from page state")
            historical.sort(key=lambda x: x.get("date", ""))
            return historical
        else:
            print(f"  -> Active state data rejected by validation")
            historical = []

    # Fallback: native mouse hover on active chart
    print("  -> Trying native mouse hover on active chart...")
    try:
        historical = await extract_data_via_mouse_hover(page)
        if historical:
            historical = deduplicate_by_date(historical)
            if validate_historical_data(historical, "Active-Hover"):
                print(f"  -> Found {len(historical)} valid active data points from tooltips")
                historical.sort(key=lambda x: x.get("date", ""))
                return historical
            else:
                print(f"  -> Active tooltip data rejected by validation")
                historical = []
        print("  -> No valid active tooltips captured")
    except Exception as e:
        print(f"  -> Mouse hover failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"  No valid active historical data found from any strategy")
    return historical


async def extract_nhtsa_incidents(page) -> list:
    """Extract NHTSA incident data from the /nhtsa page."""
    incidents = []

    try:
        await page.goto(NHTSA_PAGE_URL)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # Look for incident rows/cards
        incident_selectors = [
            ".incident-row",
            ".incident-card",
            "[data-incident]",
            "table tr",
            ".crash-report",
        ]

        for selector in incident_selectors:
            elements = await page.query_selector_all(selector)
            if elements and len(elements) > 1:  # More than header row
                for elem in elements[1:]:  # Skip header
                    text = await elem.text_content()
                    if text and ("Tesla" in text or "crash" in text.lower() or "incident" in text.lower()):
                        # Try to parse date
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})', text)
                        incidents.append({
                            "raw_text": text.strip()[:500],
                            "date": date_match.group(1) if date_match else None,
                            "source": "robotaxitracker.com/nhtsa"
                        })
                break

    except Exception as e:
        print(f"Warning: Could not extract NHTSA data: {e}")

    return incidents


async def take_screenshot(page, name: str):
    """Take a screenshot for debugging."""
    screenshot_path = DATA_DIR / f"screenshot_{name}.png"
    await page.screenshot(path=str(screenshot_path), full_page=True)
    print(f"Screenshot saved: {screenshot_path}")


async def scrape_robotaxi_tracker():
    """Main scraping function."""
    print("=" * 60)
    print("ROBOTAXI TRACKER SCRAPER")
    print("=" * 60)
    print(f"\nTarget: {ROBOTAXI_TRACKER_URL}")
    print(f"Time: {datetime.now().isoformat()}")

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Collect API responses during page load for fleet data extraction
    captured_api_responses = []

    async def capture_response(response):
        """Capture API responses that may contain fleet/chart data."""
        url = response.url
        try:
            # Look for API responses that might contain fleet data
            if any(keyword in url.lower() for keyword in [
                "api", "fleet", "vehicle", "chart", "data", "graphql",
                "trpc", "supabase", "firebase", "json"
            ]):
                content_type = response.headers.get("content-type", "")
                if "json" in content_type or "javascript" in content_type:
                    body = await response.text()
                    if body and len(body) > 10:
                        captured_api_responses.append({
                            "url": url,
                            "status": response.status,
                            "body": body[:50000],  # Cap at 50KB
                        })
                        print(f"  [API] Captured: {url[:100]} ({len(body)} bytes)")
        except Exception:
            pass  # Some responses can't be read (e.g., streaming)

    async with async_playwright() as p:
        # Launch browser
        print("\nLaunching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        # Create context with realistic settings and explicit locale
        # Setting locale to en-US ensures consistent date formats in the website
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',  # Force English US locale for consistent date formats
            timezone_id='America/Los_Angeles',  # US Pacific timezone
        )

        page = await context.new_page()

        # Listen for network responses to capture API data
        page.on("response", capture_response)

        try:
            # Navigate to main page
            print(f"\nNavigating to {ROBOTAXI_TRACKER_URL}...")
            await page.goto(ROBOTAXI_TRACKER_URL, wait_until="domcontentloaded", timeout=30000)

            # Wait for initial load
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            # Take initial screenshot (before scrolling)
            await take_screenshot(page, "main_page_initial")

            # Extract fleet data (this now includes scrolling to trigger lazy content)
            print("\nExtracting fleet data...")
            fleet_data = await extract_fleet_numbers(page)
            print(f"  Austin vehicles: {fleet_data['austin_vehicles']}")
            print(f"  Bay Area vehicles: {fleet_data['bayarea_vehicles']}")
            print(f"  Total vehicles: {fleet_data['total_vehicles']}")

            # Scroll to Fleet Growth section and take screenshot
            try:
                fleet_section = await page.query_selector("text=Fleet Growth")
                if fleet_section:
                    await fleet_section.scroll_into_view_if_needed()
                    await asyncio.sleep(2)  # Wait for chart to render
                    await take_screenshot(page, "fleet_growth_section")
            except Exception as e:
                print(f"  Could not screenshot Fleet Growth section: {e}")

            # Take full page screenshot after all content loaded
            await take_screenshot(page, "main_page_full")

            # Extract historical data (Total fleet - default view)
            print(f"\n  Captured {len(captured_api_responses)} API responses during page load")
            print("\nExtracting historical data (Total fleet)...")
            historical = await extract_historical_data(page, captured_api_responses)
            print(f"  Found {len(historical)} total historical data points")

            # --- Active Fleet Extraction ---
            # The site has "Active" / "Total" tabs on the Fleet Growth chart
            # Active fleet = vehicles actually on the road (more meaningful for MPI)
            print("\n" + "-" * 40)
            print("EXTRACTING ACTIVE FLEET DATA")
            print("-" * 40)

            active_fleet = {
                "austin_active": None,
                "bayarea_active": None,
                "total_active": None,
            }
            active_historical = []

            # Navigate back to main page if needed (after NHTSA extraction later)
            # Click the "Active" tab on Fleet Growth chart
            active_tab_clicked = await click_fleet_tab(page, "Active")
            if active_tab_clicked:
                await take_screenshot(page, "fleet_growth_active")

                # Extract active fleet numbers
                print("\nExtracting active fleet numbers...")
                active_fleet = await extract_active_fleet_numbers(page)
                print(f"  Austin active: {active_fleet['austin_active']}")
                print(f"  Bay Area active: {active_fleet['bayarea_active']}")
                print(f"  Total active: {active_fleet['total_active']}")

                # Extract active historical data from chart tooltips
                print("\nExtracting active historical data...")
                active_historical = await extract_active_historical_data(page, captured_api_responses)
                print(f"  Found {len(active_historical)} active historical data points")

                # Switch back to Total tab for consistency
                await click_fleet_tab(page, "Total")
            else:
                print("  Active tab not found - skipping active fleet extraction")

            # Extract NHTSA incidents
            print("\nExtracting NHTSA incidents...")
            incidents = await extract_nhtsa_incidents(page)
            print(f"  Found {len(incidents)} incidents")

            # Take screenshot of NHTSA page
            await take_screenshot(page, "nhtsa_page")

            # Compile results
            result = {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "source": ROBOTAXI_TRACKER_URL,
                    "scraper_version": "2.0.0"
                },
                "current_fleet": fleet_data,
                "active_fleet": active_fleet,
                "historical_data": historical,
                "active_historical_data": active_historical,
                "nhtsa_incidents": incidents
            }

            # Save to file
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nData saved to: {OUTPUT_FILE}")

            return result

        except PlaywrightTimeout as e:
            print(f"\nTimeout error: {e}")
            print("The site may be blocking automated access.")
            await take_screenshot(page, "error_timeout")
            return None

        except Exception as e:
            print(f"\nError during scraping: {e}")
            await take_screenshot(page, "error")
            raise

        finally:
            await browser.close()
            print("\nBrowser closed.")


def merge_scraped_to_fleet_data(scraped_data: dict) -> bool:
    """
    Merge scraped historical data into fleet_data.json.

    This function:
    1. Loads existing fleet_data.json
    2. Converts scraped data to snapshot format
    3. Merges new data points (skips duplicates by date)
    4. Merges active fleet data into existing snapshots by date
    5. Sorts by date
    6. Saves updated fleet_data.json

    Returns True if merge was successful and changes were made, False otherwise.
    """
    has_total_data = scraped_data and scraped_data.get("historical_data")
    has_active_data = scraped_data and scraped_data.get("active_historical_data")

    if not has_total_data and not has_active_data:
        print("No historical data to merge")
        return False

    # Load existing fleet_data.json
    if not FLEET_DATA_FILE.exists():
        print(f"Warning: {FLEET_DATA_FILE} does not exist, skipping merge")
        return False

    try:
        with open(FLEET_DATA_FILE, 'r') as f:
            fleet_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {FLEET_DATA_FILE}: {e}")
        return False

    changes_made = False

    # --- Merge total fleet historical data (existing behavior) ---
    existing_dates = {s["date"] for s in fleet_data.get("snapshots", [])}
    initial_count = len(existing_dates)

    if has_total_data:
        new_snapshots = []
        for item in scraped_data["historical_data"]:
            date = item.get("date")
            if not date or date in existing_dates:
                continue

            austin = item.get("austin")
            bayarea = item.get("bayarea")

            if austin is None and bayarea is None:
                continue

            snapshot = {
                "date": date,
                "austin_vehicles": austin,
                "bayarea_vehicles": bayarea,
                "total_robotaxi": austin,
                "source": "robotaxitracker.com",
                "notes": "Scraped from chart"
            }

            new_snapshots.append(snapshot)
            existing_dates.add(date)

        if new_snapshots:
            fleet_data["snapshots"].extend(new_snapshots)
            changes_made = True
            print(f"  Added {len(new_snapshots)} new total fleet snapshots")

    # --- Merge active fleet historical data ---
    if has_active_data:
        # Build a lookup of existing snapshots by date for updating
        snapshot_by_date = {s["date"]: s for s in fleet_data.get("snapshots", [])}
        active_merged_count = 0
        active_new_count = 0

        for item in scraped_data["active_historical_data"]:
            date = item.get("date")
            if not date:
                continue

            austin_active = item.get("austin")
            bayarea_active = item.get("bayarea")

            if austin_active is None and bayarea_active is None:
                continue

            if date in snapshot_by_date:
                # Update existing snapshot with active fleet data
                snapshot = snapshot_by_date[date]
                updated = False
                if austin_active is not None and snapshot.get("austin_active_vehicles") != austin_active:
                    snapshot["austin_active_vehicles"] = austin_active
                    updated = True
                if bayarea_active is not None and snapshot.get("bayarea_active_vehicles") != bayarea_active:
                    snapshot["bayarea_active_vehicles"] = bayarea_active
                    updated = True
                if updated:
                    active_merged_count += 1
                    changes_made = True
            else:
                # Create a new snapshot with active data only
                snapshot = {
                    "date": date,
                    "austin_vehicles": None,
                    "bayarea_vehicles": None,
                    "total_robotaxi": None,
                    "austin_active_vehicles": austin_active,
                    "bayarea_active_vehicles": bayarea_active,
                    "source": "robotaxitracker.com",
                    "notes": "Active fleet scraped from chart"
                }
                fleet_data["snapshots"].append(snapshot)
                snapshot_by_date[date] = snapshot
                active_new_count += 1
                changes_made = True

        if active_merged_count > 0 or active_new_count > 0:
            print(f"  Active fleet: updated {active_merged_count} existing snapshots, added {active_new_count} new")

    if not changes_made:
        print("No new data points to merge")
        return False

    # Sort all snapshots by date
    fleet_data["snapshots"].sort(key=lambda x: x["date"])

    # Update metadata
    fleet_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Update the last snapshot's notes with current fleet totals if available
    current_fleet = scraped_data.get("current_fleet", {})
    active_fleet = scraped_data.get("active_fleet", {})
    if current_fleet.get("austin_vehicles") and current_fleet.get("bayarea_vehicles"):
        last_snapshot = fleet_data["snapshots"][-1]
        austin = current_fleet["austin_vehicles"]
        bayarea = current_fleet["bayarea_vehicles"]
        total = austin + bayarea
        notes = f"Current fleet: {austin} Austin + {bayarea} Bay Area = {total} total"

        # Add active fleet info to notes if available
        austin_active = active_fleet.get("austin_active")
        total_active = active_fleet.get("total_active")
        if austin_active is not None:
            notes += f" (active: {austin_active} Austin"
            if total_active is not None:
                notes += f", {total_active} total"
            notes += ")"

        last_snapshot["notes"] = notes

        # Also set active fields on last snapshot from current data
        if austin_active is not None:
            last_snapshot["austin_active_vehicles"] = austin_active
        bayarea_active = active_fleet.get("bayarea_active")
        if bayarea_active is not None:
            last_snapshot["bayarea_active_vehicles"] = bayarea_active

    # Save updated fleet_data.json
    try:
        with open(FLEET_DATA_FILE, 'w') as f:
            json.dump(fleet_data, f, indent=2)

        final_count = len(fleet_data["snapshots"])
        print(f"\nMerge complete: {final_count - initial_count} new snapshots added")
        print(f"  Total snapshots: {final_count}")
        print(f"  Updated: {FLEET_DATA_FILE}")
        return True

    except IOError as e:
        print(f"Error writing {FLEET_DATA_FILE}: {e}")
        return False


def main():
    """Entry point."""
    result = asyncio.run(scrape_robotaxi_tracker())

    if result:
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)

        if result["current_fleet"]["total_vehicles"]:
            print(f"\nCurrent Total Fleet Size: {result['current_fleet']['total_vehicles']}")
        else:
            print("\nWarning: Could not extract fleet numbers.")
            print("Check screenshots in data/ folder for debugging.")
            print("The site may have changed structure or be blocking scrapers.")

        # Print active fleet info
        active_fleet = result.get("active_fleet", {})
        if active_fleet.get("total_active") or active_fleet.get("austin_active"):
            print(f"\nActive Fleet:")
            print(f"  Austin active: {active_fleet.get('austin_active')}")
            print(f"  Bay Area active: {active_fleet.get('bayarea_active')}")
            print(f"  Total active: {active_fleet.get('total_active')}")
            active_hist = result.get("active_historical_data", [])
            print(f"  Active historical data points: {len(active_hist)}")
        else:
            print("\nNote: Active fleet data not available (tab may not exist yet).")

        # Merge scraped data into fleet_data.json
        print("\n" + "-" * 60)
        print("MERGING TO FLEET DATA")
        print("-" * 60)
        merged = merge_scraped_to_fleet_data(result)
        if merged:
            print("Fleet data updated successfully.")
        else:
            print("No changes made to fleet data.")

        return 0
    else:
        print("\nScraping failed. See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

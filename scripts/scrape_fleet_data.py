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


# Output file
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "fleet_data_scraped.json"

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

    # Wait for any canvas or SVG charts to render
    try:
        await page.wait_for_selector("canvas, svg path", timeout=5000)
        print("  Chart elements detected")
        await asyncio.sleep(1)  # Extra wait for chart data to populate
    except Exception:
        print("  No chart canvas/SVG found within timeout")


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


async def extract_historical_data(page) -> list:
    """Extract historical fleet data by hovering over chart bars to get tooltips."""
    historical = []

    try:
        # First, scroll to the Fleet Growth section and ensure it's visible
        fleet_section = await page.query_selector("text=Fleet Growth")
        if fleet_section:
            await fleet_section.scroll_into_view_if_needed()
            await asyncio.sleep(2)

        # Find the chart container - Recharts uses svg.recharts-surface
        chart_element = await page.query_selector("svg.recharts-surface")
        if not chart_element:
            # Try alternative selectors
            for selector in ["canvas", ".recharts-wrapper", "[class*='chart']"]:
                chart_element = await page.query_selector(selector)
                if chart_element:
                    print(f"  Found chart element with selector: {selector}")
                    break
        else:
            print("  Found chart element with selector: svg.recharts-surface")

        if not chart_element:
            print("  Could not find chart element for tooltip extraction")
            return historical

        # Scroll chart into view and get bounding box
        await chart_element.scroll_into_view_if_needed()
        await asyncio.sleep(1)

        bbox = await chart_element.bounding_box()
        if not bbox:
            print("  Could not get chart bounding box")
            return historical

        print(f"  Chart bounding box: x={bbox['x']:.0f}, y={bbox['y']:.0f}, w={bbox['width']:.0f}, h={bbox['height']:.0f}")

        # For Recharts, we need to find the actual bar elements and hover on them
        # Look for rect elements (bars) within the chart
        bars = await page.query_selector_all("svg.recharts-surface rect.recharts-bar-rectangle")
        if not bars:
            bars = await page.query_selector_all("svg.recharts-surface rect")

        print(f"  Found {len(bars)} bar elements in chart")

        # Calculate hover positions across the chart
        chart_left = bbox['x'] + 60  # Skip y-axis
        chart_right = bbox['x'] + bbox['width'] - 20
        # Hover at multiple y positions to ensure we hit the bars
        chart_y_positions = [
            bbox['y'] + bbox['height'] * 0.3,  # Upper third
            bbox['y'] + bbox['height'] * 0.5,  # Middle
            bbox['y'] + bbox['height'] * 0.7,  # Lower third
        ]

        num_samples = 60
        step = (chart_right - chart_left) / num_samples
        seen_dates = set()

        print(f"  Scanning chart with {num_samples} hover positions...")

        for i in range(num_samples + 1):
            x = chart_left + (i * step)

            # Try multiple y positions
            for y in chart_y_positions:
                # Use JavaScript to dispatch proper mouse events
                await page.evaluate(f"""
                    (coords) => {{
                        const element = document.elementFromPoint(coords.x, coords.y);
                        if (element) {{
                            const mouseEnter = new MouseEvent('mouseenter', {{
                                bubbles: true, clientX: coords.x, clientY: coords.y
                            }});
                            const mouseMove = new MouseEvent('mousemove', {{
                                bubbles: true, clientX: coords.x, clientY: coords.y
                            }});
                            const mouseOver = new MouseEvent('mouseover', {{
                                bubbles: true, clientX: coords.x, clientY: coords.y
                            }});
                            element.dispatchEvent(mouseEnter);
                            element.dispatchEvent(mouseOver);
                            element.dispatchEvent(mouseMove);
                        }}
                    }}
                """, {"x": x, "y": y})

                await asyncio.sleep(0.1)

                # Try to find tooltip - Recharts uses various tooltip containers
                tooltip_selectors = [
                    ".recharts-tooltip-wrapper:not([style*='visibility: hidden'])",
                    ".recharts-tooltip-wrapper",
                    ".recharts-default-tooltip",
                    "[class*='tooltip']",
                    "[role='tooltip']",
                ]

                for tooltip_selector in tooltip_selectors:
                    try:
                        tooltip = await page.query_selector(tooltip_selector)
                        if tooltip:
                            # Check if tooltip is visible
                            is_visible = await tooltip.is_visible()
                            if not is_visible:
                                continue

                            tooltip_text = await tooltip.text_content()
                            if tooltip_text and tooltip_text.strip():
                                # Parse the tooltip text
                                data_point = parse_tooltip_text(tooltip_text)
                                if data_point and data_point.get("date") and data_point.get("date") not in seen_dates:
                                    seen_dates.add(data_point["date"])
                                    historical.append(data_point)
                                    print(f"    Found: {data_point['date']} - Bay Area: {data_point.get('bayarea')}, Austin: {data_point.get('austin')}")
                                break
                    except Exception:
                        pass

        # If still no data, try to extract from the page's JavaScript data
        if not historical:
            print("  No tooltips found, trying to extract chart data from page scripts...")
            historical = await extract_chart_data_from_scripts(page)

        # Sort by date
        historical.sort(key=lambda x: x.get("date", ""))
        print(f"  Extracted {len(historical)} historical data points")

    except Exception as e:
        print(f"Warning: Could not extract historical data: {e}")
        import traceback
        traceback.print_exc()

    return historical


async def extract_chart_data_from_scripts(page) -> list:
    """Try to extract chart data directly from page scripts or React state."""
    historical = []

    try:
        # Try to access React component state or chart data
        chart_data = await page.evaluate("""
            () => {
                // Try to find chart data in window or React state
                const results = [];

                // Method 1: Look for data in window object
                for (const key of Object.keys(window)) {
                    if (key.includes('chart') || key.includes('fleet') || key.includes('data')) {
                        const val = window[key];
                        if (Array.isArray(val) && val.length > 0 && val[0].date) {
                            return val;
                        }
                    }
                }

                // Method 2: Try to find Recharts internal data
                const rechartsWrapper = document.querySelector('.recharts-wrapper');
                if (rechartsWrapper && rechartsWrapper.__reactFiber$) {
                    // React fiber might have props with data
                    let fiber = rechartsWrapper.__reactFiber$;
                    while (fiber) {
                        if (fiber.memoizedProps && fiber.memoizedProps.data) {
                            return fiber.memoizedProps.data;
                        }
                        fiber = fiber.return;
                    }
                }

                // Method 3: Parse script tags for data
                const scripts = document.querySelectorAll('script');
                for (const script of scripts) {
                    const text = script.textContent || '';
                    // Look for array patterns with dates
                    const match = text.match(/\\[\\s*\\{[^\\]]*"date"[^\\]]*\\}\\s*\\]/);
                    if (match) {
                        try {
                            return JSON.parse(match[0]);
                        } catch(e) {}
                    }
                }

                return results;
            }
        """)

        if chart_data and isinstance(chart_data, list):
            for item in chart_data:
                if isinstance(item, dict) and item.get("date"):
                    historical.append({
                        "date": item.get("date"),
                        "bayarea": item.get("bayArea") or item.get("bayarea") or item.get("Bay Area"),
                        "austin": item.get("austin") or item.get("Austin"),
                        "total": item.get("total") or item.get("Total"),
                    })
            print(f"  Found {len(historical)} data points from scripts")
    except Exception as e:
        print(f"  Could not extract chart data from scripts: {e}")

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

            # Extract historical data
            print("\nExtracting historical data...")
            historical = await extract_historical_data(page)
            print(f"  Found {len(historical)} historical data points")

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
                    "scraper_version": "1.0.0"
                },
                "current_fleet": fleet_data,
                "historical_data": historical,
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


def main():
    """Entry point."""
    result = asyncio.run(scrape_robotaxi_tracker())

    if result:
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)

        if result["current_fleet"]["total_vehicles"]:
            print(f"\nCurrent Fleet Size: {result['current_fleet']['total_vehicles']}")
        else:
            print("\nWarning: Could not extract fleet numbers.")
            print("Check screenshots in data/ folder for debugging.")
            print("The site may have changed structure or be blocking scrapers.")

        return 0
    else:
        print("\nScraping failed. See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

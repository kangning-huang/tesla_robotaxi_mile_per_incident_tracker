# Tesla Robotaxi Expansion Cities Tracker: Complete Implementation Guide

## Overview

This guide walks you through creating a dedicated page that tracks Tesla's robotaxi expansion across cities. This page will:
1. Target high-search-volume queries like "Tesla robotaxi cities", "Tesla robotaxi expansion 2026"
2. Provide real-time status updates that become a go-to reference
3. Include schema markup for enhanced SEO/AEO
4. Complement your existing safety tracker with geographic context

---

## Data Architecture

### City Status Categories

Based on current announcements and operations, use these status categories:

| Status | Description | Color Code |
|--------|-------------|------------|
| **Live - Unsupervised** | True Level 4 ADS, no safety monitor | 🟢 Green |
| **Live - Supervised** | Operating with safety driver | 🟡 Yellow |
| **Announced** | Officially confirmed, launch pending | 🔵 Blue |
| **Testing** | Vehicles spotted testing, not public | ⚪ Gray |
| **Rumored** | Speculation only, not confirmed | ⚫ Dark Gray |

### Current City Data (as of January 30, 2026)

```javascript
const cities = [
  // LIVE
  {
    city: "Austin",
    state: "TX",
    status: "live-unsupervised",
    launchDate: "2025-06-22",
    unsupervisedDate: "2025-12-15",
    fleetSize: 72,
    fleetSource: "RobotaxiTracker.com",
    notes: "First city with unsupervised rides. Fleet growing rapidly.",
    incidents: 10,
    incidentsSource: "NHTSA SGO",
    latitude: 30.2672,
    longitude: -97.7431
  },
  {
    city: "San Francisco Bay Area",
    state: "CA",
    status: "live-supervised",
    launchDate: "2025-07-15",
    unsupervisedDate: null,
    fleetSize: 168,
    fleetSource: "RobotaxiTracker.com",
    notes: "Largest fleet. Safety drivers required by CA regulations.",
    incidents: 0,
    incidentsSource: "N/A (supervised)",
    latitude: 37.7749,
    longitude: -122.4194
  },
  
  // ANNOUNCED - H1 2026
  {
    city: "Dallas",
    state: "TX",
    status: "announced",
    announcedDate: "2026-01-28",
    expectedLaunch: "H1 2026",
    fleetSize: null,
    notes: "Part of 7-city H1 2026 expansion announced at Q4 earnings.",
    latitude: 32.7767,
    longitude: -96.7970
  },
  {
    city: "Houston",
    state: "TX",
    status: "announced",
    announcedDate: "2026-01-28",
    expectedLaunch: "H1 2026",
    fleetSize: null,
    notes: "Part of 7-city H1 2026 expansion announced at Q4 earnings.",
    latitude: 29.7604,
    longitude: -95.3698
  },
  {
    city: "Phoenix",
    state: "AZ",
    status: "announced",
    announcedDate: "2026-01-28",
    expectedLaunch: "H1 2026",
    fleetSize: null,
    notes: "AZ permits obtained. Waymo competitor market.",
    latitude: 33.4484,
    longitude: -112.0740
  },
  {
    city: "Miami",
    state: "FL",
    status: "announced",
    announcedDate: "2026-01-28",
    expectedLaunch: "H1 2026",
    fleetSize: null,
    notes: "Part of 7-city H1 2026 expansion announced at Q4 earnings.",
    latitude: 25.7617,
    longitude: -80.1918
  },
  {
    city: "Orlando",
    state: "FL",
    status: "announced",
    announcedDate: "2026-01-28",
    expectedLaunch: "H1 2026",
    fleetSize: null,
    notes: "Added to expansion list at Q4 2025 earnings call.",
    latitude: 28.5383,
    longitude: -81.3792
  },
  {
    city: "Tampa",
    state: "FL",
    status: "announced",
    announcedDate: "2026-01-28",
    expectedLaunch: "H1 2026",
    fleetSize: null,
    notes: "Added to expansion list at Q4 2025 earnings call.",
    latitude: 27.9506,
    longitude: -82.4572
  },
  {
    city: "Las Vegas",
    state: "NV",
    status: "announced",
    announcedDate: "2026-01-28",
    expectedLaunch: "H1 2026",
    fleetSize: null,
    notes: "NV has favorable AV regulations.",
    latitude: 36.1699,
    longitude: -115.1398
  }
];
```

---

## Step 1: Create the Page Structure

### Option A: New HTML Page (Recommended)

Create a new file: `expansion.html` or set up a route `/expansion`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <!-- SEO Meta Tags -->
  <title>Tesla Robotaxi Expansion Tracker | Cities & Launch Timeline 2026</title>
  <meta name="description" content="Track Tesla's robotaxi expansion across US cities. Real-time status for Austin, Bay Area, Dallas, Houston, Phoenix, Miami, and more. Updated daily.">
  <meta name="keywords" content="Tesla robotaxi cities, Tesla robotaxi expansion, Tesla robotaxi 2026, Tesla robotaxi Dallas, Tesla robotaxi Houston, Tesla robotaxi Phoenix">
  
  <!-- Open Graph -->
  <meta property="og:title" content="Tesla Robotaxi Expansion Tracker | City-by-City Status">
  <meta property="og:description" content="Track Tesla's robotaxi rollout across US cities with real-time fleet data and launch timelines.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://robotaxi-safety-tracker.com/expansion">
  
  <!-- Canonical URL -->
  <link rel="canonical" href="https://robotaxi-safety-tracker.com/expansion">
  
  <!-- Schema Markup (see Step 5) -->
  <script type="application/ld+json">
  <!-- Insert schema here -->
  </script>
  
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <!-- Navigation -->
  <nav>
    <a href="/">Safety Tracker</a>
    <a href="/expansion" class="active">Expansion</a>
    <a href="/#faq">FAQ</a>
    <a href="/#methodology">Methodology</a>
  </nav>

  <!-- Hero Section -->
  <header class="expansion-hero">
    <h1>Tesla Robotaxi Expansion Tracker</h1>
    <p class="subtitle">City-by-city status of Tesla's autonomous ride-hailing rollout</p>
    
    <!-- Summary Stats -->
    <div class="stats-row">
      <div class="stat">
        <span class="stat-number" id="live-cities">2</span>
        <span class="stat-label">Cities Live</span>
      </div>
      <div class="stat">
        <span class="stat-number" id="announced-cities">7</span>
        <span class="stat-label">Announced</span>
      </div>
      <div class="stat">
        <span class="stat-number" id="total-fleet">240+</span>
        <span class="stat-label">Total Fleet</span>
      </div>
      <div class="stat">
        <span class="stat-number" id="last-update">Jan 30</span>
        <span class="stat-label">Last Updated</span>
      </div>
    </div>
  </header>

  <!-- Map Section (Optional) -->
  <section id="map" class="expansion-map">
    <h2>Expansion Map</h2>
    <div id="city-map"></div>
  </section>

  <!-- City Status Table -->
  <section id="cities" class="city-table-section">
    <h2>City-by-City Status</h2>
    
    <!-- Filter Buttons -->
    <div class="filter-buttons">
      <button class="filter-btn active" data-filter="all">All</button>
      <button class="filter-btn" data-filter="live">Live</button>
      <button class="filter-btn" data-filter="announced">Announced</button>
    </div>
    
    <!-- Status Table -->
    <div class="table-wrapper">
      <table id="city-status-table">
        <thead>
          <tr>
            <th>City</th>
            <th>State</th>
            <th>Status</th>
            <th>Launch Date</th>
            <th>Fleet Size</th>
            <th>Incidents</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <!-- Populated by JavaScript -->
        </tbody>
      </table>
    </div>
  </section>

  <!-- Timeline Section -->
  <section id="timeline" class="timeline-section">
    <h2>Expansion Timeline</h2>
    <div class="timeline">
      <!-- Timeline items populated by JS -->
    </div>
  </section>

  <!-- Comparison with Waymo -->
  <section id="comparison" class="comparison-section">
    <h2>Tesla vs Waymo: City Coverage</h2>
    <div class="comparison-grid">
      <div class="company-column">
        <h3>Tesla Robotaxi</h3>
        <ul id="tesla-cities-list">
          <!-- Populated by JS -->
        </ul>
      </div>
      <div class="company-column">
        <h3>Waymo</h3>
        <ul>
          <li>✅ Phoenix, AZ</li>
          <li>✅ San Francisco, CA</li>
          <li>✅ Los Angeles, CA</li>
          <li>✅ Austin, TX</li>
          <li>✅ Miami, FL</li>
          <li>✅ Dallas, TX (2026)</li>
          <li>✅ Houston, TX (2026)</li>
          <li>🔵 20+ more cities planned</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- FAQ Section for this page -->
  <section id="expansion-faq" class="faq-section">
    <h2>Expansion FAQ</h2>
    <div class="faq-grid">
      <!-- City-specific FAQs -->
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <p>Data sources: Tesla Q4 2025 Earnings, RobotaxiTracker.com, NHTSA SGO</p>
    <p>Last updated: <time datetime="2026-01-30">January 30, 2026</time></p>
  </footer>

  <script src="expansion.js"></script>
</body>
</html>
```

---

## Step 2: CSS Styling

Add these styles to match your existing dark theme:

```css
/* ===== EXPANSION PAGE STYLES ===== */

/* Hero Section */
.expansion-hero {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
}

.expansion-hero h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: #fff;
}

.expansion-hero .subtitle {
  color: #888;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

/* Stats Row */
.stats-row {
  display: flex;
  justify-content: center;
  gap: 3rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  color: #3b82f6;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Map Section */
.expansion-map {
  padding: 3rem 2rem;
  background: #0f0f0f;
}

.expansion-map h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #fff;
}

#city-map {
  height: 400px;
  background: #1a1a1a;
  border-radius: 8px;
  max-width: 1000px;
  margin: 0 auto;
}

/* Filter Buttons */
.filter-buttons {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.filter-btn {
  padding: 0.5rem 1.25rem;
  border: 1px solid #333;
  background: transparent;
  color: #888;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.filter-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

/* City Table */
.city-table-section {
  padding: 3rem 2rem;
  background: #0a0a0a;
}

.city-table-section h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #fff;
}

.table-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  overflow-x: auto;
}

#city-status-table {
  width: 100%;
  border-collapse: collapse;
}

#city-status-table th,
#city-status-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #222;
}

#city-status-table th {
  color: #888;
  font-weight: 500;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

#city-status-table td {
  color: #ddd;
}

#city-status-table tbody tr:hover {
  background: #111;
}

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.live-unsupervised {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.status-badge.live-supervised {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.status-badge.announced {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.status-badge.testing {
  background: rgba(156, 163, 175, 0.2);
  color: #9ca3af;
}

/* Timeline */
.timeline-section {
  padding: 3rem 2rem;
  background: #0f0f0f;
}

.timeline-section h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #fff;
}

.timeline {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #333;
}

.timeline-item {
  position: relative;
  padding-bottom: 2rem;
  padding-left: 30px;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -35px;
  top: 5px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3b82f6;
  border: 2px solid #0f0f0f;
}

.timeline-item.past::before {
  background: #22c55e;
}

.timeline-item.future::before {
  background: #333;
  border: 2px solid #3b82f6;
}

.timeline-date {
  font-size: 0.85rem;
  color: #3b82f6;
  margin-bottom: 0.25rem;
}

.timeline-title {
  font-size: 1.1rem;
  color: #fff;
  margin-bottom: 0.25rem;
}

.timeline-desc {
  color: #888;
  font-size: 0.95rem;
}

/* Comparison Grid */
.comparison-section {
  padding: 3rem 2rem;
  background: #0a0a0a;
}

.comparison-section h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #fff;
}

.comparison-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.company-column {
  background: #111;
  border-radius: 8px;
  padding: 1.5rem;
}

.company-column h3 {
  color: #fff;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #333;
}

.company-column ul {
  list-style: none;
  padding: 0;
}

.company-column li {
  padding: 0.5rem 0;
  color: #aaa;
  border-bottom: 1px solid #222;
}

.company-column li:last-child {
  border-bottom: none;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-row {
    gap: 1.5rem;
  }
  
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  
  #city-status-table th,
  #city-status-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.9rem;
  }
}
```

---

## Step 3: JavaScript for Dynamic Content

Create `expansion.js`:

```javascript
// ===== TESLA ROBOTAXI EXPANSION TRACKER =====

// City Data
const cities = [
  {
    city: "Austin",
    state: "TX",
    status: "live-unsupervised",
    statusLabel: "Live - Unsupervised",
    launchDate: "2025-06-22",
    fleetSize: 72,
    incidents: 10,
    notes: "First city with unsupervised rides"
  },
  {
    city: "San Francisco Bay Area",
    state: "CA",
    status: "live-supervised",
    statusLabel: "Live - Supervised",
    launchDate: "2025-07-15",
    fleetSize: 168,
    incidents: "N/A",
    notes: "Safety drivers required by CA regulations"
  },
  {
    city: "Dallas",
    state: "TX",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "—",
    notes: "Q4 2025 earnings announcement"
  },
  {
    city: "Houston",
    state: "TX",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "—",
    notes: "Q4 2025 earnings announcement"
  },
  {
    city: "Phoenix",
    state: "AZ",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "—",
    notes: "AZ permits obtained"
  },
  {
    city: "Miami",
    state: "FL",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "—",
    notes: "Q4 2025 earnings announcement"
  },
  {
    city: "Orlando",
    state: "FL",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "—",
    notes: "Added at Q4 2025 call"
  },
  {
    city: "Tampa",
    state: "FL",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "—",
    notes: "Added at Q4 2025 call"
  },
  {
    city: "Las Vegas",
    state: "NV",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "—",
    notes: "NV favorable AV regulations"
  }
];

// Timeline Events
const timelineEvents = [
  {
    date: "June 22, 2025",
    title: "Austin Launch",
    description: "Tesla launches robotaxi pilot with safety monitors in passenger seat",
    past: true
  },
  {
    date: "July 15, 2025",
    title: "Bay Area Launch",
    description: "Service expands to San Francisco with safety drivers",
    past: true
  },
  {
    date: "December 15, 2025",
    title: "Austin Goes Unsupervised",
    description: "First unsupervised (no safety monitor) rides begin in Austin",
    past: true
  },
  {
    date: "January 28, 2026",
    title: "7-City Expansion Announced",
    description: "Q4 earnings call confirms Dallas, Houston, Phoenix, Miami, Orlando, Tampa, Las Vegas for H1 2026",
    past: true
  },
  {
    date: "H1 2026",
    title: "Multi-City Expansion",
    description: "Planned launch in 7 new cities pending regulatory approvals",
    past: false
  },
  {
    date: "April 2026",
    title: "Cybercab Production",
    description: "Purpose-built robotaxi expected to begin production",
    past: false
  }
];

// Populate City Table
function populateCityTable(filter = 'all') {
  const tbody = document.querySelector('#city-status-table tbody');
  tbody.innerHTML = '';
  
  const filteredCities = filter === 'all' 
    ? cities 
    : cities.filter(c => {
        if (filter === 'live') return c.status.includes('live');
        if (filter === 'announced') return c.status === 'announced';
        return true;
      });
  
  filteredCities.forEach(city => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><strong>${city.city}</strong></td>
      <td>${city.state}</td>
      <td><span class="status-badge ${city.status}">${city.statusLabel}</span></td>
      <td>${city.launchDate}</td>
      <td>${city.fleetSize}</td>
      <td>${city.incidents}</td>
      <td>${city.notes}</td>
    `;
    tbody.appendChild(row);
  });
}

// Populate Timeline
function populateTimeline() {
  const timeline = document.querySelector('.timeline');
  timeline.innerHTML = '';
  
  timelineEvents.forEach(event => {
    const item = document.createElement('div');
    item.className = `timeline-item ${event.past ? 'past' : 'future'}`;
    item.innerHTML = `
      <div class="timeline-date">${event.date}</div>
      <div class="timeline-title">${event.title}</div>
      <div class="timeline-desc">${event.description}</div>
    `;
    timeline.appendChild(item);
  });
}

// Update Stats
function updateStats() {
  const liveCities = cities.filter(c => c.status.includes('live')).length;
  const announcedCities = cities.filter(c => c.status === 'announced').length;
  const totalFleet = cities.reduce((sum, c) => {
    return sum + (typeof c.fleetSize === 'number' ? c.fleetSize : 0);
  }, 0);
  
  document.getElementById('live-cities').textContent = liveCities;
  document.getElementById('announced-cities').textContent = announcedCities;
  document.getElementById('total-fleet').textContent = totalFleet + '+';
}

// Filter Button Handlers
function setupFilters() {
  const buttons = document.querySelectorAll('.filter-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      populateCityTable(btn.dataset.filter);
    });
  });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  populateCityTable();
  populateTimeline();
  updateStats();
  setupFilters();
});
```

---

## Step 4: Add an Interactive Map (Optional)

Use Leaflet.js for a simple, free map:

```html
<!-- Add to <head> -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

```javascript
// Add to expansion.js

const cityCoordinates = [
  { city: "Austin", lat: 30.2672, lng: -97.7431, status: "live-unsupervised" },
  { city: "Bay Area", lat: 37.7749, lng: -122.4194, status: "live-supervised" },
  { city: "Dallas", lat: 32.7767, lng: -96.7970, status: "announced" },
  { city: "Houston", lat: 29.7604, lng: -95.3698, status: "announced" },
  { city: "Phoenix", lat: 33.4484, lng: -112.0740, status: "announced" },
  { city: "Miami", lat: 25.7617, lng: -80.1918, status: "announced" },
  { city: "Orlando", lat: 28.5383, lng: -81.3792, status: "announced" },
  { city: "Tampa", lat: 27.9506, lng: -82.4572, status: "announced" },
  { city: "Las Vegas", lat: 36.1699, lng: -115.1398, status: "announced" }
];

function initMap() {
  const map = L.map('city-map').setView([37.0902, -95.7129], 4);
  
  // Dark tile layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap contributors © CARTO'
  }).addTo(map);
  
  // Add markers
  cityCoordinates.forEach(city => {
    const color = city.status === 'live-unsupervised' ? '#22c55e' 
                : city.status === 'live-supervised' ? '#eab308' 
                : '#3b82f6';
    
    const marker = L.circleMarker([city.lat, city.lng], {
      radius: city.status.includes('live') ? 10 : 7,
      fillColor: color,
      color: color,
      weight: 2,
      opacity: 1,
      fillOpacity: 0.6
    }).addTo(map);
    
    marker.bindPopup(`<strong>${city.city}</strong><br>${city.status.replace('-', ' ')}`);
  });
}

// Call in DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  // ... other init code
  initMap();
});
```

---

## Step 5: Schema Markup for SEO/AEO

Add this JSON-LD to the `<head>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Tesla Robotaxi City Expansion Tracker",
  "description": "Real-time tracking of Tesla's robotaxi expansion across US cities, including launch dates, fleet sizes, and operational status.",
  "url": "https://robotaxi-safety-tracker.com/expansion",
  "creator": {
    "@type": "Person",
    "name": "Kangning Huang",
    "url": "https://kangninghuang.substack.com"
  },
  "temporalCoverage": "2025-06/..",
  "spatialCoverage": {
    "@type": "Place",
    "name": "United States"
  },
  "variableMeasured": [
    {
      "@type": "PropertyValue",
      "name": "Fleet Size",
      "description": "Number of robotaxi vehicles in each city"
    },
    {
      "@type": "PropertyValue",
      "name": "Launch Status",
      "description": "Operational status: Live-Unsupervised, Live-Supervised, Announced, Testing"
    }
  ],
  "dateModified": "2026-01-30"
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What cities have Tesla robotaxis?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "As of January 2026, Tesla robotaxis operate in Austin, Texas (with unsupervised rides) and the San Francisco Bay Area (with safety drivers). Tesla has announced expansion to Dallas, Houston, Phoenix, Miami, Orlando, Tampa, and Las Vegas for the first half of 2026."
      }
    },
    {
      "@type": "Question",
      "name": "When will Tesla robotaxi come to Dallas?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tesla announced at its Q4 2025 earnings call that Dallas is planned for H1 2026 (first half of 2026), pending regulatory approvals."
      }
    },
    {
      "@type": "Question",
      "name": "When will Tesla robotaxi come to Houston?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tesla announced at its Q4 2025 earnings call that Houston is planned for H1 2026 (first half of 2026), pending regulatory approvals."
      }
    },
    {
      "@type": "Question",
      "name": "When will Tesla robotaxi come to Phoenix?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tesla announced at its Q4 2025 earnings call that Phoenix is planned for H1 2026. Arizona has already granted Tesla the necessary permits for autonomous vehicle testing."
      }
    },
    {
      "@type": "Question",
      "name": "When will Tesla robotaxi come to Miami?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tesla announced at its Q4 2025 earnings call that Miami is planned for H1 2026 (first half of 2026), pending regulatory approvals."
      }
    },
    {
      "@type": "Question",
      "name": "When will Tesla robotaxi come to Las Vegas?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tesla announced at its Q4 2025 earnings call that Las Vegas is planned for H1 2026. Nevada has favorable autonomous vehicle regulations."
      }
    },
    {
      "@type": "Question",
      "name": "How many Tesla robotaxis are there?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "As of January 2026, Tesla has approximately 240+ robotaxis across two markets: about 168 in the Bay Area and 72 in Austin. At the Q4 2025 earnings call, Musk stated the fleet is 'well over 500' vehicles including both markets."
      }
    }
  ]
}
</script>
```

---

## Step 6: Link from Main Site

Update your main navigation and add internal links:

```html
<!-- In your main index.html navigation -->
<nav>
  <a href="/#trend">Trend</a>
  <a href="/expansion">Cities</a>  <!-- Add this -->
  <a href="/#methodology">Methodology</a>
  <a href="/#faq">FAQ</a>
  <a href="/#creator">Creator</a>
</nav>
```

Also add a CTA block on your homepage:

```html
<!-- Add after your main chart section -->
<section class="expansion-cta">
  <h3>Track the Expansion</h3>
  <p>See which cities Tesla is launching next →</p>
  <a href="/expansion" class="btn-primary">View City Tracker</a>
</section>
```

---

## Step 7: Data Update Process

Create a simple data update workflow:

### Manual Update Checklist

When updating city data:

1. **Check RobotaxiTracker.com** for latest fleet counts
2. **Check NHTSA SGO** for new incidents
3. **Check Tesla IR** for new city announcements
4. **Update the `cities` array** in expansion.js
5. **Update the `dateModified`** in schema markup
6. **Update the summary stats**

### Suggested Update Frequency

| Data Point | Update Frequency |
|------------|------------------|
| Fleet sizes | Weekly |
| Incident counts | After each NHTSA report |
| City status changes | As announced |
| Launch dates | As announced |

---

## Step 8: SEO Checklist

- [ ] Page title includes "Tesla Robotaxi" + "Cities" or "Expansion"
- [ ] Meta description under 160 chars with key cities mentioned
- [ ] H1 contains primary keyword
- [ ] Internal links from homepage
- [ ] Schema markup validated
- [ ] Mobile responsive
- [ ] Fast load time (< 3s)
- [ ] Canonical URL set
- [ ] Last updated date visible

---

## Expected SEO/AEO Benefits

### Target Queries This Page Will Rank For:

- "Tesla robotaxi cities"
- "Tesla robotaxi expansion 2026"
- "Tesla robotaxi Dallas" / "Houston" / "Phoenix" / etc.
- "When will Tesla robotaxi launch in [city]"
- "Where is Tesla robotaxi available"
- "Tesla robotaxi vs Waymo cities"
- "Tesla robotaxi fleet size"

### AEO Benefits:

AI systems will be able to directly answer:
- "What cities have Tesla robotaxis?"
- "When is Tesla robotaxi coming to [city]?"
- "How many Tesla robotaxis are there?"

---

## Quick Implementation Checklist

- [ ] Create expansion.html page
- [ ] Add CSS styling
- [ ] Add JavaScript for dynamic content
- [ ] Add JSON-LD schema (Dataset + FAQPage)
- [ ] Add navigation link from main site
- [ ] Add map (optional but recommended)
- [ ] Validate schema with Google Rich Results Test
- [ ] Test on mobile
- [ ] Submit to Google Search Console

---

## Questions?

If you need help with:
- Integrating this with your existing codebase
- Setting up automated data updates
- Adding more cities or data points
- Creating the comparison with Waymo page

Just let me know!

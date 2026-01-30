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
    notes: "First city with unsupervised rides",
    lat: 30.2672,
    lng: -97.7431
  },
  {
    city: "San Francisco Bay Area",
    state: "CA",
    status: "live-supervised",
    statusLabel: "Live - Supervised",
    launchDate: "2025-07-15",
    fleetSize: 168,
    incidents: "N/A",
    notes: "Safety drivers required by CA regulations",
    lat: 37.7749,
    lng: -122.4194
  },
  {
    city: "Dallas",
    state: "TX",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "\u2014",
    notes: "Q4 2025 earnings announcement",
    lat: 32.7767,
    lng: -96.7970
  },
  {
    city: "Houston",
    state: "TX",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "\u2014",
    notes: "Q4 2025 earnings announcement",
    lat: 29.7604,
    lng: -95.3698
  },
  {
    city: "Phoenix",
    state: "AZ",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "\u2014",
    notes: "AZ permits obtained",
    lat: 33.4484,
    lng: -112.0740
  },
  {
    city: "Miami",
    state: "FL",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "\u2014",
    notes: "Q4 2025 earnings announcement",
    lat: 25.7617,
    lng: -80.1918
  },
  {
    city: "Orlando",
    state: "FL",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "\u2014",
    notes: "Added at Q4 2025 call",
    lat: 28.5383,
    lng: -81.3792
  },
  {
    city: "Tampa",
    state: "FL",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "\u2014",
    notes: "Added at Q4 2025 call",
    lat: 27.9506,
    lng: -82.4572
  },
  {
    city: "Las Vegas",
    state: "NV",
    status: "announced",
    statusLabel: "Announced",
    launchDate: "H1 2026",
    fleetSize: "TBD",
    incidents: "\u2014",
    notes: "NV favorable AV regulations",
    lat: 36.1699,
    lng: -115.1398
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
function populateCityTable(filter) {
  if (filter === undefined) filter = 'all';
  var tbody = document.querySelector('#city-status-table tbody');
  tbody.innerHTML = '';

  var filteredCities = filter === 'all'
    ? cities
    : cities.filter(function(c) {
        if (filter === 'live') return c.status.indexOf('live') !== -1;
        if (filter === 'announced') return c.status === 'announced';
        return true;
      });

  filteredCities.forEach(function(city) {
    var row = document.createElement('tr');
    row.innerHTML =
      '<td><strong>' + city.city + '</strong></td>' +
      '<td>' + city.state + '</td>' +
      '<td><span class="status-badge ' + city.status + '">' + city.statusLabel + '</span></td>' +
      '<td>' + city.launchDate + '</td>' +
      '<td>' + city.fleetSize + '</td>' +
      '<td>' + city.incidents + '</td>' +
      '<td>' + city.notes + '</td>';
    tbody.appendChild(row);
  });
}

// Populate Timeline
function populateTimeline() {
  var timeline = document.querySelector('.timeline');
  timeline.innerHTML = '';

  timelineEvents.forEach(function(event) {
    var item = document.createElement('div');
    item.className = 'timeline-item ' + (event.past ? 'past' : 'future');
    item.innerHTML =
      '<div class="timeline-date">' + event.date + '</div>' +
      '<div class="timeline-title">' + event.title + '</div>' +
      '<div class="timeline-desc">' + event.description + '</div>';
    timeline.appendChild(item);
  });
}

// Populate Tesla Cities List for comparison section
function populateTeslaCities() {
  var list = document.getElementById('tesla-cities-list');
  if (!list) return;
  list.innerHTML = '';

  cities.forEach(function(city) {
    var li = document.createElement('li');
    var dotClass = city.status.indexOf('live') !== -1 ? 'live' : 'announced';
    var label = city.city + ', ' + city.state;
    if (city.status === 'announced') {
      label += ' (H1 2026)';
    }
    li.innerHTML = '<span class="status-dot ' + dotClass + '"></span> ' + label;
    list.appendChild(li);
  });
}

// Update Stats
function updateStats() {
  var liveCities = cities.filter(function(c) { return c.status.indexOf('live') !== -1; }).length;
  var announcedCities = cities.filter(function(c) { return c.status === 'announced'; }).length;
  var totalFleet = cities.reduce(function(sum, c) {
    return sum + (typeof c.fleetSize === 'number' ? c.fleetSize : 0);
  }, 0);

  document.getElementById('live-cities').textContent = liveCities;
  document.getElementById('announced-cities').textContent = announcedCities;
  document.getElementById('total-fleet').textContent = totalFleet + '+';
}

// Filter Button Handlers
function setupFilters() {
  var buttons = document.querySelectorAll('.filter-btn');
  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      buttons.forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      populateCityTable(btn.dataset.filter);
    });
  });
}

// FAQ Accordion
function setupFaq() {
  var faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function(item) {
    var button = item.querySelector('.faq-question');
    button.addEventListener('click', function() {
      var isActive = item.classList.contains('active');

      // Close all items
      faqItems.forEach(function(i) {
        i.classList.remove('active');
        i.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
      });

      // Open clicked item (if it wasn't already open)
      if (!isActive) {
        item.classList.add('active');
        button.setAttribute('aria-expanded', 'true');
      }
    });
  });
}

// Initialize Map
function initMap() {
  var mapEl = document.getElementById('city-map');
  if (!mapEl) return;

  var map = L.map('city-map', {
    scrollWheelZoom: false
  }).setView([33.0, -98.0], 4);

  // Dark tile layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
  }).addTo(map);

  // Add markers for each city
  cities.forEach(function(city) {
    var color = city.status === 'live-unsupervised' ? '#22c55e'
              : city.status === 'live-supervised' ? '#eab308'
              : '#3b82f6';

    var radius = city.status.indexOf('live') !== -1 ? 10 : 7;

    var marker = L.circleMarker([city.lat, city.lng], {
      radius: radius,
      fillColor: color,
      color: color,
      weight: 2,
      opacity: 1,
      fillOpacity: 0.6
    }).addTo(map);

    var popupContent =
      '<strong>' + city.city + ', ' + city.state + '</strong><br>' +
      '<span style="color: ' + color + ';">' + city.statusLabel + '</span>';

    if (typeof city.fleetSize === 'number') {
      popupContent += '<br>Fleet: ' + city.fleetSize + ' vehicles';
    }

    if (city.launchDate) {
      popupContent += '<br>Launch: ' + city.launchDate;
    }

    marker.bindPopup(popupContent);
  });

  // Handle light theme detection for map tiles
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    // Switch to light tiles
    map.eachLayer(function(layer) {
      if (layer instanceof L.TileLayer) {
        map.removeLayer(layer);
      }
    });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
    }).addTo(map);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  populateCityTable();
  populateTimeline();
  populateTeslaCities();
  updateStats();
  setupFilters();
  setupFaq();
  initMap();
});

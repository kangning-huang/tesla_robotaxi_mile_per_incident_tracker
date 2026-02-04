// FAQ Page JavaScript
// Handles dynamic data loading, value updates, accordion functionality, and FAQPage schema generation
// Uses the same incident data and calculations as app.js for consistency

// ===== SHARED DATA (must match app.js) =====
// Updated with 115 mi/day/vehicle (validated from Tesla's 250K miles Q3 2025 report)
// Fleet sizes use total Austin fleet from fleet_data.json
const incidentData = [
    { date: '2025-07-05', days: 10, fleet: 11, miles: 14100, mpi: 14100 },
    { date: '2025-07-18', days: 13, fleet: 13, miles: 21000, mpi: 21000 },
    { date: '2025-08-02', days: 15, fleet: 14, miles: 25800, mpi: 25800 },
    { date: '2025-08-20', days: 18, fleet: 14, miles: 31400, mpi: 31400 },
    { date: '2025-09-05', days: 16, fleet: 15, miles: 29400, mpi: 29400 },
    { date: '2025-09-22', days: 17, fleet: 18, miles: 37000, mpi: 37000 },
    { date: '2025-10-08', days: 16, fleet: 18, miles: 35200, mpi: 35200 },
    { date: '2025-10-25', days: 17, fleet: 18, miles: 37300, mpi: 37300 },
    { date: '2025-11-12', days: 18, fleet: 20, miles: 42800, mpi: 42800 },
    { date: '2025-12-10', days: 28, fleet: 28, miles: 92500, mpi: 92500 },
];

// Total fleet size data (Austin unsupervised robotaxis)
// Interpolated daily from fleet_data.json austin_vehicles field
const fleetData = [
    { date: '2025-06-25', size: 10 },
    { date: '2025-06-26', size: 10 },
    { date: '2025-06-27', size: 10 },
    { date: '2025-06-28', size: 11 },
    { date: '2025-06-29', size: 11 },
    { date: '2025-06-30', size: 11 },
    { date: '2025-07-01', size: 12 },
    { date: '2025-07-02', size: 12 },
    { date: '2025-07-03', size: 12 },
    { date: '2025-07-04', size: 12 },
    { date: '2025-07-05', size: 12 },
    { date: '2025-07-06', size: 12 },
    { date: '2025-07-07', size: 12 },
    { date: '2025-07-08', size: 13 },
    { date: '2025-07-09', size: 13 },
    { date: '2025-07-10', size: 13 },
    { date: '2025-07-11', size: 13 },
    { date: '2025-07-12', size: 13 },
    { date: '2025-07-13', size: 13 },
    { date: '2025-07-14', size: 13 },
    { date: '2025-07-15', size: 14 },
    { date: '2025-07-16', size: 14 },
    { date: '2025-07-17', size: 14 },
    { date: '2025-07-18', size: 14 },
    { date: '2025-07-19', size: 14 },
    { date: '2025-07-20', size: 14 },
    { date: '2025-07-21', size: 14 },
    { date: '2025-07-22', size: 14 },
    { date: '2025-07-23', size: 14 },
    { date: '2025-07-24', size: 14 },
    { date: '2025-07-25', size: 14 },
    { date: '2025-07-26', size: 14 },
    { date: '2025-07-27', size: 14 },
    { date: '2025-07-28', size: 14 },
    { date: '2025-07-29', size: 14 },
    { date: '2025-07-30', size: 14 },
    { date: '2025-07-31', size: 14 },
    { date: '2025-08-01', size: 14 },
    { date: '2025-08-02', size: 14 },
    { date: '2025-08-03', size: 14 },
    { date: '2025-08-04', size: 14 },
    { date: '2025-08-05', size: 14 },
    { date: '2025-08-06', size: 14 },
    { date: '2025-08-07', size: 14 },
    { date: '2025-08-08', size: 14 },
    { date: '2025-08-09', size: 14 },
    { date: '2025-08-10', size: 14 },
    { date: '2025-08-11', size: 14 },
    { date: '2025-08-12', size: 14 },
    { date: '2025-08-13', size: 14 },
    { date: '2025-08-14', size: 15 },
    { date: '2025-08-15', size: 15 },
    { date: '2025-08-16', size: 15 },
    { date: '2025-08-17', size: 15 },
    { date: '2025-08-18', size: 15 },
    { date: '2025-08-19', size: 15 },
    { date: '2025-08-20', size: 15 },
    { date: '2025-08-21', size: 15 },
    { date: '2025-08-22', size: 15 },
    { date: '2025-08-23', size: 15 },
    { date: '2025-08-24', size: 15 },
    { date: '2025-08-25', size: 15 },
    { date: '2025-08-26', size: 15 },
    { date: '2025-08-27', size: 15 },
    { date: '2025-08-28', size: 15 },
    { date: '2025-08-29', size: 15 },
    { date: '2025-08-30', size: 15 },
    { date: '2025-08-31', size: 15 },
    { date: '2025-09-01', size: 15 },
    { date: '2025-09-02', size: 15 },
    { date: '2025-09-03', size: 15 },
    { date: '2025-09-04', size: 15 },
    { date: '2025-09-05', size: 16 },
    { date: '2025-09-06', size: 18 },
    { date: '2025-09-07', size: 18 },
    { date: '2025-09-08', size: 18 },
    { date: '2025-09-09', size: 18 },
    { date: '2025-09-10', size: 18 },
    { date: '2025-09-11', size: 18 },
    { date: '2025-09-12', size: 18 },
    { date: '2025-09-13', size: 18 },
    { date: '2025-09-14', size: 18 },
    { date: '2025-09-15', size: 18 },
    { date: '2025-09-16', size: 18 },
    { date: '2025-09-17', size: 18 },
    { date: '2025-09-18', size: 18 },
    { date: '2025-09-19', size: 18 },
    { date: '2025-09-20', size: 18 },
    { date: '2025-09-21', size: 18 },
    { date: '2025-09-22', size: 18 },
    { date: '2025-09-23', size: 18 },
    { date: '2025-09-24', size: 18 },
    { date: '2025-09-25', size: 18 },
    { date: '2025-09-26', size: 18 },
    { date: '2025-09-27', size: 18 },
    { date: '2025-09-28', size: 18 },
    { date: '2025-09-29', size: 18 },
    { date: '2025-09-30', size: 18 },
    { date: '2025-10-01', size: 18 },
    { date: '2025-10-02', size: 18 },
    { date: '2025-10-03', size: 18 },
    { date: '2025-10-04', size: 18 },
    { date: '2025-10-05', size: 18 },
    { date: '2025-10-06', size: 18 },
    { date: '2025-10-07', size: 18 },
    { date: '2025-10-08', size: 18 },
    { date: '2025-10-09', size: 18 },
    { date: '2025-10-10', size: 18 },
    { date: '2025-10-11', size: 18 },
    { date: '2025-10-12', size: 18 },
    { date: '2025-10-13', size: 18 },
    { date: '2025-10-14', size: 18 },
    { date: '2025-10-15', size: 18 },
    { date: '2025-10-16', size: 18 },
    { date: '2025-10-17', size: 18 },
    { date: '2025-10-18', size: 18 },
    { date: '2025-10-19', size: 18 },
    { date: '2025-10-20', size: 18 },
    { date: '2025-10-21', size: 18 },
    { date: '2025-10-22', size: 18 },
    { date: '2025-10-23', size: 18 },
    { date: '2025-10-24', size: 18 },
    { date: '2025-10-25', size: 18 },
    { date: '2025-10-26', size: 18 },
    { date: '2025-10-27', size: 18 },
    { date: '2025-10-28', size: 18 },
    { date: '2025-10-29', size: 18 },
    { date: '2025-10-30', size: 19 },
    { date: '2025-10-31', size: 19 },
    { date: '2025-11-01', size: 19 },
    { date: '2025-11-02', size: 19 },
    { date: '2025-11-03', size: 19 },
    { date: '2025-11-04', size: 20 },
    { date: '2025-11-05', size: 20 },
    { date: '2025-11-06', size: 20 },
    { date: '2025-11-07', size: 20 },
    { date: '2025-11-08', size: 21 },
    { date: '2025-11-09', size: 21 },
    { date: '2025-11-10', size: 21 },
    { date: '2025-11-11', size: 22 },
    { date: '2025-11-12', size: 22 },
    { date: '2025-11-13', size: 23 },
    { date: '2025-11-14', size: 23 },
    { date: '2025-11-15', size: 24 },
    { date: '2025-11-16', size: 24 },
    { date: '2025-11-17', size: 25 },
    { date: '2025-11-18', size: 28 },
    { date: '2025-11-19', size: 28 },
    { date: '2025-11-20', size: 28 },
    { date: '2025-11-21', size: 28 },
    { date: '2025-11-22', size: 29 },
    { date: '2025-11-23', size: 29 },
    { date: '2025-11-24', size: 29 },
    { date: '2025-11-25', size: 29 },
    { date: '2025-11-26', size: 29 },
    { date: '2025-11-27', size: 29 },
    { date: '2025-11-28', size: 29 },
    { date: '2025-11-29', size: 29 },
    { date: '2025-11-30', size: 29 },
    { date: '2025-12-01', size: 29 },
    { date: '2025-12-02', size: 29 },
    { date: '2025-12-03', size: 29 },
    { date: '2025-12-04', size: 29 },
    { date: '2025-12-05', size: 29 },
    { date: '2025-12-06', size: 29 },
    { date: '2025-12-07', size: 29 },
    { date: '2025-12-08', size: 29 },
    { date: '2025-12-09', size: 29 },
    { date: '2025-12-10', size: 29 },
    { date: '2025-12-11', size: 29 },
    { date: '2025-12-12', size: 29 },
    { date: '2025-12-13', size: 29 },
    { date: '2025-12-14', size: 29 },
    { date: '2025-12-15', size: 29 },
    { date: '2025-12-16', size: 29 },
    { date: '2025-12-17', size: 29 },
    { date: '2025-12-18', size: 29 },
    { date: '2025-12-19', size: 29 },
    { date: '2025-12-20', size: 29 },
    { date: '2025-12-21', size: 30 },
    { date: '2025-12-22', size: 30 },
    { date: '2025-12-23', size: 30 },
    { date: '2025-12-24', size: 30 },
    { date: '2025-12-25', size: 30 },
    { date: '2025-12-26', size: 31 },
    { date: '2025-12-27', size: 31 },
    { date: '2025-12-28', size: 31 },
    { date: '2025-12-29', size: 32 },
    { date: '2025-12-30', size: 32 },
    { date: '2025-12-31', size: 32 },
    { date: '2026-01-01', size: 33 },
    { date: '2026-01-02', size: 34 },
    { date: '2026-01-03', size: 34 },
    { date: '2026-01-04', size: 34 },
    { date: '2026-01-05', size: 35 },
    { date: '2026-01-06', size: 37 },
    { date: '2026-01-07', size: 37 },
    { date: '2026-01-08', size: 37 },
    { date: '2026-01-09', size: 38 },
    { date: '2026-01-10', size: 38 },
    { date: '2026-01-11', size: 39 },
    { date: '2026-01-12', size: 41 },
    { date: '2026-01-13', size: 41 },
    { date: '2026-01-14', size: 44 },
    { date: '2026-01-15', size: 45 },
    { date: '2026-01-16', size: 47 },
    { date: '2026-01-17', size: 50 },
    { date: '2026-01-18', size: 52 },
    { date: '2026-01-19', size: 54 },
    { date: '2026-01-20', size: 56 },
    { date: '2026-01-21', size: 57 },
    { date: '2026-01-22', size: 62 },
    { date: '2026-01-23', size: 75 },
    { date: '2026-01-24', size: 78 },
    { date: '2026-01-25', size: 78 },
    { date: '2026-01-26', size: 78 },
    { date: '2026-01-27', size: 78 },
    { date: '2026-01-28', size: 78 },
    { date: '2026-01-29', size: 80 },
];

// Service stoppage dates — days when Tesla Robotaxi was not operating (0 miles accumulated)
// January 2026 winter storm: ice storm, roads impassable, CapMetro suspended, city facilities closed
const serviceStoppageDates = new Set([
    '2026-01-25',
    '2026-01-26',
]);

// Helper: count stoppage days in a date range (exclusive of start, inclusive of end)
function countStoppageDays(startDate, endDate) {
    let count = 0;
    const current = new Date(startDate);
    current.setDate(current.getDate() + 1); // start day after
    while (current <= endDate) {
        const dateStr = current.toISOString().split('T')[0];
        if (serviceStoppageDates.has(dateStr)) count++;
        current.setDate(current.getDate() + 1);
    }
    return count;
}

// Compute exponential trend parameters via log-linear regression on incidentData
// Fits MPI = a * exp(b * t) by regressing ln(MPI) = ln(a) + b * t
function computeExponentialFit(data) {
    const startDate = new Date(data[0].date);
    const n = data.length;
    const x = []; // days since first incident
    const Y = []; // ln(MPI)

    for (const d of data) {
        const days = Math.floor((new Date(d.date) - startDate) / (1000 * 60 * 60 * 24));
        x.push(days);
        Y.push(Math.log(d.mpi));
    }

    // Linear regression on (x, Y)
    let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
    for (let i = 0; i < n; i++) {
        sumX += x[i];
        sumY += Y[i];
        sumXY += x[i] * Y[i];
        sumX2 += x[i] * x[i];
    }
    const meanX = sumX / n;
    const meanY = sumY / n;
    const b = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const A = meanY - b * meanX;
    const a = Math.exp(A);

    // R² on original scale (non-linear)
    const meanMPI = data.reduce((s, d) => s + d.mpi, 0) / n;
    let ssRes = 0, ssTot = 0;
    for (let i = 0; i < n; i++) {
        const pred = a * Math.exp(b * x[i]);
        ssRes += (data[i].mpi - pred) ** 2;
        ssTot += (data[i].mpi - meanMPI) ** 2;
    }
    const rSquared = ssTot > 0 ? 1 - ssRes / ssTot : 0;

    const doublingTime = b > 0 ? Math.round(Math.log(2) / b) : Infinity;
    // 30-day forecast from last data point
    const lastDays = x[x.length - 1];
    const forecast30Day = Math.round(a * Math.exp(b * (lastDays + 30)));

    return { a, b, rSquared, doublingTime, dailyGrowth: b, forecast30Day };
}

// Compute trend parameters from incident data
const fit = computeExponentialFit(incidentData);
const trendParams = {
    exponential: { a: fit.a, b: fit.b },
    rSquared: fit.rSquared,
    doublingTime: fit.doublingTime,
    dailyGrowth: fit.dailyGrowth,
    forecast30Day: fit.forecast30Day
};

// ===== Initialize FAQ Page =====
(function initFaqPage() {
    // Extract key metrics from incident data (same as app.js)
    const totalIncidents = incidentData.length;
    const latestMpi = incidentData[incidentData.length - 1].mpi;
    const avgMpi = Math.round(incidentData.reduce((sum, d) => sum + d.mpi, 0) / totalIncidents);
    const totalMiles = incidentData.reduce((sum, d) => sum + d.miles, 0);
    const rSquared = trendParams.rSquared;
    const doublingTime = trendParams.doublingTime;

    // Get latest fleet size from fleet data
    const currentFleetSize = fleetData[fleetData.length - 1].size;

    // Get last incident date
    const lastIncidentDateStr = incidentData[incidentData.length - 1].date;
    const lastIncidentDate = new Date(lastIncidentDateStr);

    // Calculate current streak (miles since last incident, excluding stoppage days)
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const currentStreak = activeDays * currentFleetSize * 115;

    // Calculate comparison ratios
    const humanPoliceReportedMpi = 500000;
    const humanInsuranceMpi = 300000;
    const waymoMpi = 1000000;

    const vsHumanRatio = (humanPoliceReportedMpi / latestMpi).toFixed(1);
    const vsInsuranceRatio = (humanInsuranceMpi / latestMpi).toFixed(1);
    const vsWaymoRatio = (waymoMpi / latestMpi).toFixed(1);

    // Format numbers
    const formatNumber = (num) => {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return Math.round(num).toLocaleString();
        }
        return num.toString();
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    };

    // Data through date (latest fleet data date)
    const dataThrough = formatDate(fleetData[fleetData.length - 1].date);

    // Update all dynamic values
    const setValue = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    };

    // Stats banner
    setValue('stat-latest-mpi', formatNumber(latestMpi));
    setValue('stat-doubling-time', doublingTime);
    setValue('stat-total-incidents', totalIncidents);
    setValue('stat-data-through', dataThrough);

    // Methodology section
    setValue('faq-method-r-squared', rSquared.toFixed(2));
    setValue('faq-method-fleet', currentFleetSize);

    // Reporting lag section
    setValue('faq-lag-data-through', dataThrough);
    setValue('faq-lag-latest-incident', formatDate(lastIncidentDateStr));
    setValue('faq-lag-streak', formatNumber(currentStreak));

    // Comparisons section
    setValue('faq-compare-latest-mpi', formatNumber(latestMpi));
    setValue('faq-compare-waymo-ratio', vsWaymoRatio);
    setValue('faq-compare-doubling', doublingTime);

    // Charts section
    setValue('faq-chart-doubling', doublingTime);
    setValue('faq-chart-r-squared', rSquared.toFixed(2));
    setValue('faq-chart-total', totalIncidents);
    setValue('faq-chart-latest-mpi', formatNumber(latestMpi));

    // Misconceptions section
    setValue('faq-misc-simple-avg', formatNumber(avgMpi));
    setValue('faq-misc-latest-mpi', formatNumber(latestMpi));
    setValue('faq-misc-total', totalIncidents);

    // Initialize FAQ accordion
    initFaqAccordion();

    // Update FAQ Schema
    updateFaqSchema();
})();

// FAQ Accordion Functionality
function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all other items in the same category
            const category = item.closest('.faq-grid');
            if (category) {
                category.querySelectorAll('.faq-item').forEach(otherItem => {
                    otherItem.classList.remove('active');
                    otherItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
                });
            }

            // Toggle current item
            if (!isActive) {
                item.classList.add('active');
                question.setAttribute('aria-expanded', 'true');
            }
        });
    });
}

// Update FAQPage Schema for SEO
function updateFaqSchema() {
    const faqSchema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    };

    // Get all FAQ items and generate schema
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const questionEl = item.querySelector('.faq-question h3');
        const answerEl = item.querySelector('.faq-answer');

        if (questionEl && answerEl) {
            const questionText = questionEl.textContent.trim();
            // Get text content, stripping HTML but preserving structure
            const answerText = answerEl.textContent.trim().replace(/\s+/g, ' ');

            faqSchema.mainEntity.push({
                "@type": "Question",
                "name": questionText,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answerText
                }
            });
        }
    });

    // Update the schema script tag
    const schemaEl = document.getElementById('faq-schema');
    if (schemaEl) {
        schemaEl.textContent = JSON.stringify(faqSchema, null, 2);
    }
}

// Smooth scroll for table of contents links
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.faq-toc-item').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetEl = document.getElementById(targetId);
            if (targetEl) {
                const headerHeight = 72; // Account for fixed header
                const targetPosition = targetEl.offsetTop - headerHeight - 20;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});

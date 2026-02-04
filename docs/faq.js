// FAQ Page JavaScript
// Handles dynamic data loading, value updates, accordion functionality, and FAQPage schema generation

(async function initFaqPage() {
    // Load data from JSON files
    let analysisData = null;
    let fleetData = null;

    try {
        const [analysisResponse, fleetResponse] = await Promise.all([
            fetch('../data/analysis_results.json'),
            fetch('../data/fleet_data.json')
        ]);
        analysisData = await analysisResponse.json();
        fleetData = await fleetResponse.json();
    } catch (error) {
        console.error('Failed to load data:', error);
        // Use fallback values
        analysisData = {
            incident_count: 10,
            summary: {
                latest_mpi: 66585,
                average_mpi: 24828,
                total_miles: 248285
            },
            trend_analysis: {
                best_fit: {
                    r_squared: 0.36,
                    doubling_time_days: 41
                }
            },
            incidents: []
        };
    }

    // Extract key metrics
    const totalIncidents = analysisData.incident_count || 10;
    const latestMpi = analysisData.summary?.latest_mpi || 66585;
    const avgMpi = analysisData.summary?.average_mpi || 24828;
    const totalMiles = analysisData.summary?.total_miles || 248285;
    const rSquared = analysisData.trend_analysis?.best_fit?.r_squared || 0.36;
    const doublingTime = Math.round(analysisData.trend_analysis?.best_fit?.doubling_time_days || 41);

    // Get latest fleet size from fleet data
    let currentFleetSize = 81;
    if (fleetData && fleetData.snapshots && fleetData.snapshots.length > 0) {
        const latestSnapshot = fleetData.snapshots[fleetData.snapshots.length - 1];
        currentFleetSize = latestSnapshot.austin_vehicles || 81;
    }

    // Get last incident date
    let lastIncidentDate = '2025-11-01';
    if (analysisData.incidents && analysisData.incidents.length > 0) {
        lastIncidentDate = analysisData.incidents[analysisData.incidents.length - 1].incident_date;
    }

    // Calculate current streak (miles since last incident)
    const today = new Date();
    const lastIncident = new Date(lastIncidentDate);
    const daysSinceIncident = Math.floor((today - lastIncident) / (1000 * 60 * 60 * 24));
    const currentStreak = currentFleetSize * 115 * daysSinceIncident;

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
    let dataThrough = 'Feb 3, 2026';
    if (fleetData && fleetData.snapshots && fleetData.snapshots.length > 0) {
        dataThrough = formatDate(fleetData.snapshots[fleetData.snapshots.length - 1].date);
    }

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
    setValue('faq-lag-latest-incident', formatDate(lastIncidentDate));
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

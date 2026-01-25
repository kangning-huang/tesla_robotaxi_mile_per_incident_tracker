// ===== Data =====
// Updated with 115 mi/day/vehicle (validated from Tesla's 250K miles Q3 2025 report)
const incidentData = [
    { date: '2025-07-05', days: 10, fleet: 11, miles: 14100, mpi: 14100 },
    { date: '2025-07-18', days: 13, fleet: 14, miles: 22200, mpi: 22200 },
    { date: '2025-08-02', days: 15, fleet: 16, miles: 30100, mpi: 30100 },
    { date: '2025-08-20', days: 18, fleet: 19, miles: 41500, mpi: 41500 },
    { date: '2025-09-05', days: 16, fleet: 21, miles: 41200, mpi: 41200 },
    { date: '2025-09-22', days: 17, fleet: 24, miles: 50000, mpi: 50000 },
    { date: '2025-10-08', days: 16, fleet: 27, miles: 53400, mpi: 53400 },
    { date: '2025-10-25', days: 17, fleet: 30, miles: 61300, mpi: 61300 },
    { date: '2025-11-12', days: 18, fleet: 31, miles: 66900, mpi: 66900 },
    { date: '2025-12-10', days: 28, fleet: 32, miles: 107500, mpi: 107500 },
];

// Fleet size data (Austin unsupervised robotaxis only) - sampled from fleet_data.json
const fleetData = [
    { date: '2025-06-25', size: 10 },
    { date: '2025-07-15', size: 14 },
    { date: '2025-08-14', size: 15 },
    { date: '2025-09-05', size: 16 },
    { date: '2025-09-06', size: 18 },
    { date: '2025-10-30', size: 19 },
    { date: '2025-11-08', size: 21 },
    { date: '2025-11-17', size: 25 },
    { date: '2025-11-22', size: 29 },
    { date: '2025-12-25', size: 31 },
    { date: '2025-12-31', size: 33 },
    { date: '2026-01-06', size: 36 },
    { date: '2026-01-16', size: 42 },
    { date: '2026-01-19', size: 48 },
    { date: '2026-01-22', size: 60 },
    { date: '2026-01-23', size: 68 },
];

// Trend analysis parameters (from Python analysis, updated for 115 mi/day)
const trendParams = {
    exponential: { a: 20970, b: 0.009998 },
    rSquared: 0.955,
    doublingTime: 69,
    dailyGrowth: 0.01,
    forecast30Day: 137400
};

// ===== Chart Configuration =====
const chartColors = {
    primary: '#3b82f6',
    danger: '#ef4444',
    success: '#22c55e',
    warning: '#f59e0b',
    muted: '#71717a',
    grid: '#27272a',
    background: '#161616'
};

// Common chart options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        intersect: true,
        mode: 'nearest'
    },
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            backgroundColor: '#1a1a1a',
            titleColor: '#ffffff',
            bodyColor: '#a1a1aa',
            borderColor: '#27272a',
            borderWidth: 1,
            padding: 8,
            displayColors: false,
            callbacks: {
                title: function() {
                    return ''; // Hide title to save space
                },
                label: function(context) {
                    const value = context.parsed.y;
                    if (value === null) return null;
                    if (value >= 1000) {
                        return Math.round(value / 1000) + 'K miles';
                    }
                    return value.toLocaleString() + ' miles';
                }
            }
        }
    },
    scales: {
        x: {
            grid: {
                color: chartColors.grid,
                drawBorder: false
            },
            ticks: {
                color: chartColors.muted,
                font: {
                    family: "'Inter', sans-serif",
                    size: 11
                }
            }
        },
        y: {
            grid: {
                color: chartColors.grid,
                drawBorder: false
            },
            ticks: {
                color: chartColors.muted,
                font: {
                    family: "'JetBrains Mono', monospace",
                    size: 11
                },
                callback: function(value) {
                    return value.toLocaleString();
                }
            }
        }
    }
};

// ===== Initialize Charts =====
function initMPIChart() {
    const ctx = document.getElementById('mpiChart').getContext('2d');

    // Prepare base data from incidents
    const startDate = new Date(incidentData[0].date);
    const lastIncidentDate = new Date(incidentData[incidentData.length - 1].date);
    const today = new Date();

    // Generate labels from first incident to today
    const labels = [];
    const mpiValues = [];
    const trendData = [];
    const humanBenchmarkPolice = [];    // 500K - police-reported crashes
    const humanBenchmarkInsurance = []; // 300K - insurance claims (Swiss Re)
    const ongoingProgress = []; // Cumulative miles since last incident

    // Add all incident data points
    incidentData.forEach(d => {
        labels.push(d.date);
        mpiValues.push(d.mpi);
        const currentDate = new Date(d.date);
        const daysSinceStart = Math.floor((currentDate - startDate) / (1000 * 60 * 60 * 24));
        trendData.push(Math.round(trendParams.exponential.a * Math.exp(trendParams.exponential.b * daysSinceStart)));
        humanBenchmarkPolice.push(500000);
        humanBenchmarkInsurance.push(300000);
        ongoingProgress.push(null); // No ongoing data for past incidents
    });

    // Extend projection to today (add monthly points after last incident)
    let projectionDate = new Date(lastIncidentDate);
    projectionDate.setDate(projectionDate.getDate() + 30); // Start 30 days after last incident

    while (projectionDate <= today) {
        const dateStr = projectionDate.toISOString().split('T')[0];
        labels.push(dateStr);
        mpiValues.push(null); // No actual incident data
        const daysSinceStart = Math.floor((projectionDate - startDate) / (1000 * 60 * 60 * 24));
        trendData.push(Math.round(trendParams.exponential.a * Math.exp(trendParams.exponential.b * daysSinceStart)));
        humanBenchmarkPolice.push(500000);
        humanBenchmarkInsurance.push(300000);
        ongoingProgress.push(null);
        projectionDate.setDate(projectionDate.getDate() + 30); // Monthly intervals
    }

    // Add today as final point with cumulative miles since last incident
    if (today > lastIncidentDate) {
        const todayStr = today.toISOString().split('T')[0];
        if (!labels.includes(todayStr)) {
            labels.push(todayStr);
            mpiValues.push(null);
            const daysSinceStart = Math.floor((today - startDate) / (1000 * 60 * 60 * 24));
            trendData.push(Math.round(trendParams.exponential.a * Math.exp(trendParams.exponential.b * daysSinceStart)));
            humanBenchmarkPolice.push(500000);
            humanBenchmarkInsurance.push(300000);

            // Calculate cumulative miles since last incident
            const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
            const currentFleetSize = fleetData[fleetData.length - 1].size; // Latest fleet size
            const cumulativeMiles = daysSinceLastIncident * currentFleetSize * 115; // 115 mi/day/vehicle
            ongoingProgress.push(cumulativeMiles);
        } else {
            // Today already in labels, find its index and set ongoing progress
            const todayIndex = labels.indexOf(todayStr);
            const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
            const currentFleetSize = fleetData[fleetData.length - 1].size;
            const cumulativeMiles = daysSinceLastIncident * currentFleetSize * 115;
            ongoingProgress[todayIndex] = cumulativeMiles;
        }
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Miles per Incident',
                    data: mpiValues,
                    borderColor: chartColors.danger,
                    backgroundColor: chartColors.danger,
                    borderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: chartColors.danger,
                    pointBorderColor: '#0a0a0a',
                    pointBorderWidth: 2,
                    tension: 0,
                    spanGaps: false,
                    order: 1
                },
                {
                    label: 'Exponential Trend (Projected)',
                    data: trendData,
                    borderColor: chartColors.primary,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [],
                    pointRadius: 0,
                    tension: 0,
                    order: 2
                },
                {
                    label: 'Human Benchmark - Police Reports (500K)',
                    data: humanBenchmarkPolice,
                    borderColor: chartColors.success,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [8, 4],
                    pointRadius: 0,
                    order: 3
                },
                {
                    label: 'Human Benchmark - Insurance Claims (300K)',
                    data: humanBenchmarkInsurance,
                    borderColor: '#a855f7',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [4, 4],
                    pointRadius: 0,
                    order: 4
                },
                {
                    label: 'Miles Since Last Incident',
                    data: ongoingProgress,
                    borderColor: chartColors.warning,
                    backgroundColor: 'transparent',
                    borderWidth: 0,
                    pointRadius: 8,
                    pointHoverRadius: 10,
                    pointBackgroundColor: 'transparent',
                    pointBorderColor: chartColors.warning,
                    pointBorderWidth: 3,
                    pointStyle: 'circle',
                    showLine: false,
                    order: 5
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                x: commonOptions.scales.x,
                y: {
                    type: 'logarithmic',
                    grid: {
                        color: chartColors.grid,
                        drawBorder: false
                    },
                    min: 10000,
                    max: 1000000,
                    afterBuildTicks: function(axis) {
                        axis.ticks = [
                            { value: 10000 },
                            { value: 20000 },
                            { value: 50000 },
                            { value: 100000 },
                            { value: 200000 },
                            { value: 300000 },
                            { value: 500000 },
                            { value: 1000000 }
                        ];
                    },
                    ticks: {
                        color: chartColors.muted,
                        font: { family: "'JetBrains Mono', monospace", size: 11 },
                        callback: function(value) {
                            if (value === 10000) return '10K';
                            if (value === 20000) return '20K';
                            if (value === 50000) return '50K';
                            if (value === 100000) return '100K';
                            if (value === 200000) return '200K';
                            if (value === 300000) return '300K';
                            if (value === 500000) return '500K';
                            if (value === 1000000) return '1M';
                            return '';
                        }
                    }
                }
            },
            plugins: {
                ...commonOptions.plugins,
                annotation: {
                    annotations: {
                        humanLinePolice: {
                            type: 'line',
                            yMin: 500000,
                            yMax: 500000,
                            borderColor: chartColors.success,
                            borderWidth: 2,
                            borderDash: [8, 4]
                        },
                        humanLineInsurance: {
                            type: 'line',
                            yMin: 300000,
                            yMax: 300000,
                            borderColor: '#a855f7',
                            borderWidth: 2,
                            borderDash: [4, 4]
                        }
                    }
                }
            }
        }
    });
}

function initFleetChart() {
    const ctx = document.getElementById('fleetChart').getContext('2d');

    const labels = fleetData.map(d => d.date);
    const sizes = fleetData.map(d => d.size);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Fleet Size',
                data: sizes,
                backgroundColor: (context) => {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;
                    if (!chartArea) return chartColors.primary;

                    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
                    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.8)');
                    return gradient;
                },
                borderColor: chartColors.primary,
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        title: function() {
                            return ''; // Hide title to save space
                        },
                        label: function(context) {
                            const value = context.parsed.y;
                            if (value === null) return null;
                            return value.toLocaleString() + ' vehicles';
                        }
                    }
                }
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    beginAtZero: true,
                    max: 80
                }
            }
        }
    });
}

// ===== Populate Table =====
function populateIncidentTable() {
    const tbody = document.getElementById('incident-table-body');

    incidentData.forEach((incident, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${incident.date}</td>
            <td>${incident.days}</td>
            <td>${incident.fleet}</td>
            <td>${incident.miles.toLocaleString()}</td>
            <td>${incident.mpi.toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// ===== Update Metrics =====
function updateMetrics() {
    // Calculate metrics
    const latestMPI = incidentData[incidentData.length - 1].mpi;
    const previousMPI = incidentData[incidentData.length - 2].mpi;
    const avgMPI = Math.round(incidentData.reduce((sum, d) => sum + d.mpi, 0) / incidentData.length);
    const totalIncidents = incidentData.length;
    const vsHuman = (500000 / latestMPI).toFixed(1);

    // Calculate change percentage
    const changePercent = Math.round(((latestMPI - previousMPI) / previousMPI) * 100);

    // Update DOM
    document.getElementById('latest-mpi').textContent = latestMPI.toLocaleString();
    document.getElementById('avg-mpi').textContent = avgMPI.toLocaleString();
    document.getElementById('total-incidents').textContent = totalIncidents;
    document.getElementById('vs-human').textContent = vsHuman + 'x';

    // Update change indicator
    const changeEl = document.querySelector('.metric-change');
    if (changeEl) {
        changeEl.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 15l-6-6-6 6"/>
            </svg>
            +${changePercent}% from previous
        `;
    }
}

// ===== Smooth Scroll =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== Animate Comparison Bars =====
function animateComparisonBars() {
    const bars = document.querySelectorAll('.comparison-bar');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.width = entry.target.dataset.width || entry.target.style.width;
            }
        });
    }, { threshold: 0.5 });

    bars.forEach(bar => {
        bar.dataset.width = bar.style.width;
        bar.style.width = '0%';
        observer.observe(bar);
    });
}

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    initMPIChart();
    initFleetChart();
    populateIncidentTable();
    updateMetrics();
    animateComparisonBars();

    // Update date
    document.getElementById('last-updated').textContent = new Date().toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
});

// ===== Fetch Latest Data (for future use) =====
async function fetchLatestData() {
    try {
        const response = await fetch('../data/analysis_results.json');
        if (response.ok) {
            const data = await response.json();
            console.log('Latest analysis data:', data);
            // Could update charts with live data here
        }
    } catch (error) {
        console.log('Using embedded data (JSON fetch not available)');
    }
}

// Try to fetch latest data
fetchLatestData();

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

// Fleet size data (Austin unsupervised robotaxis only) - all data points from fleet_data.json
const fleetData = [
    { date: '2025-06-25', size: 10 },
    { date: '2025-07-01', size: 12 },
    { date: '2025-07-15', size: 14 },
    { date: '2025-08-14', size: 15 },
    { date: '2025-08-21', size: 15 },
    { date: '2025-08-31', size: 15 },
    { date: '2025-09-03', size: 15 },
    { date: '2025-09-04', size: 15 },
    { date: '2025-09-05', size: 16 },
    { date: '2025-09-06', size: 18 },
    { date: '2025-09-13', size: 18 },
    { date: '2025-09-17', size: 18 },
    { date: '2025-09-19', size: 18 },
    { date: '2025-10-01', size: 18 },
    { date: '2025-10-02', size: 18 },
    { date: '2025-10-05', size: 18 },
    { date: '2025-10-07', size: 18 },
    { date: '2025-10-09', size: 18 },
    { date: '2025-10-18', size: 18 },
    { date: '2025-10-22', size: 18 },
    { date: '2025-10-26', size: 18 },
    { date: '2025-10-30', size: 19 },
    { date: '2025-11-04', size: 20 },
    { date: '2025-11-08', size: 21 },
    { date: '2025-11-09', size: 21 },
    { date: '2025-11-11', size: 22 },
    { date: '2025-11-17', size: 25 },
    { date: '2025-11-18', size: 28 },
    { date: '2025-11-20', size: 28 },
    { date: '2025-11-22', size: 29 },
    { date: '2025-11-23', size: 29 },
    { date: '2025-11-24', size: 29 },
    { date: '2025-11-25', size: 29 },
    { date: '2025-11-26', size: 29 },
    { date: '2025-11-27', size: 29 },
    { date: '2025-11-29', size: 29 },
    { date: '2025-11-30', size: 29 },
    { date: '2025-12-01', size: 29 },
    { date: '2025-12-02', size: 29 },
    { date: '2025-12-08', size: 29 },
    { date: '2025-12-10', size: 29 },
    { date: '2025-12-12', size: 29 },
    { date: '2025-12-15', size: 29 },
    { date: '2025-12-16', size: 29 },
    { date: '2025-12-19', size: 29 },
    { date: '2025-12-25', size: 31 },
    { date: '2025-12-28', size: 31 },
    { date: '2025-12-29', size: 32 },
    { date: '2025-12-30', size: 32 },
    { date: '2025-12-31', size: 33 },
    { date: '2026-01-01', size: 34 },
    { date: '2026-01-02', size: 34 },
    { date: '2026-01-03', size: 34 },
    { date: '2026-01-04', size: 35 },
    { date: '2026-01-05', size: 35 },
    { date: '2026-01-06', size: 36 },
    { date: '2026-01-07', size: 36 },
    { date: '2026-01-08', size: 37 },
    { date: '2026-01-09', size: 37 },
    { date: '2026-01-10', size: 38 },
    { date: '2026-01-11', size: 38 },
    { date: '2026-01-12', size: 38 },
    { date: '2026-01-13', size: 38 },
    { date: '2026-01-15', size: 39 },
    { date: '2026-01-16', size: 42 },
    { date: '2026-01-17', size: 43 },
    { date: '2026-01-18', size: 46 },
    { date: '2026-01-19', size: 48 },
    { date: '2026-01-20', size: 49 },
    { date: '2026-01-21', size: 50 },
    { date: '2026-01-22', size: 60 },
    { date: '2026-01-23', size: 68 },
    { date: '2026-01-24', size: 72 },
];

// Trend analysis parameters (from Python analysis, updated for 115 mi/day)
const trendParams = {
    exponential: { a: 20970, b: 0.009998 },
    rSquared: 0.955,
    doublingTime: 69,
    dailyGrowth: 0.01,
    forecast30Day: 137400
};

// ===== Theme Detection =====
function isDarkMode() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

// ===== Chart Configuration =====
const darkChartColors = {
    primary: '#3b82f6',
    danger: '#ef4444',
    success: '#22c55e',
    warning: '#f59e0b',
    muted: '#71717a',
    grid: '#27272a',
    background: '#161616',
    tooltipBg: '#1a1a1a',
    tooltipTitle: '#ffffff',
    tooltipBody: '#a1a1aa',
    tooltipBorder: '#27272a',
    pointBorder: '#0a0a0a',
    purple: '#a855f7'
};

const lightChartColors = {
    primary: '#2563eb',
    danger: '#dc2626',
    success: '#16a34a',
    warning: '#d97706',
    muted: '#64748b',
    grid: '#e2e8f0',
    background: '#ffffff',
    tooltipBg: '#ffffff',
    tooltipTitle: '#0f172a',
    tooltipBody: '#475569',
    tooltipBorder: '#e2e8f0',
    pointBorder: '#ffffff',
    purple: '#7c3aed'
};

function getChartColors() {
    return isDarkMode() ? darkChartColors : lightChartColors;
}

// Initialize with current theme
let chartColors = getChartColors();

// Common chart options (function to get fresh colors)
function getCommonOptions() {
    const colors = getChartColors();
    return {
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
                backgroundColor: colors.tooltipBg,
                titleColor: colors.tooltipTitle,
                bodyColor: colors.tooltipBody,
                borderColor: colors.tooltipBorder,
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
                    color: colors.grid,
                    drawBorder: false
                },
                ticks: {
                    color: colors.muted,
                    font: {
                        family: "'Inter', sans-serif",
                        size: 11
                    }
                }
            },
            y: {
                grid: {
                    color: colors.grid,
                    drawBorder: false
                },
                ticks: {
                    color: colors.muted,
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
}

// Keep backward compatibility
const commonOptions = getCommonOptions();

// ===== Initialize Charts =====
// Store chart instances for theme updates
let mpiChartInstance = null;
let fleetChartInstance = null;

function initMPIChart() {
    const ctx = document.getElementById('mpiChart').getContext('2d');
    const colors = getChartColors();
    const options = getCommonOptions();

    // Destroy existing chart if present
    if (mpiChartInstance) {
        mpiChartInstance.destroy();
    }

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

    mpiChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Miles per Incident',
                    data: mpiValues,
                    borderColor: colors.danger,
                    backgroundColor: colors.danger,
                    borderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: colors.danger,
                    pointBorderColor: colors.pointBorder,
                    pointBorderWidth: 2,
                    tension: 0,
                    spanGaps: false,
                    order: 1
                },
                {
                    label: 'Exponential Trend (Projected)',
                    data: trendData,
                    borderColor: colors.primary,
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
                    borderColor: colors.success,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [8, 4],
                    pointRadius: 0,
                    order: 3
                },
                {
                    label: 'Human Benchmark - Insurance Claims (300K)',
                    data: humanBenchmarkInsurance,
                    borderColor: colors.purple,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [4, 4],
                    pointRadius: 0,
                    order: 4
                },
                {
                    label: 'Miles Since Last Incident',
                    data: ongoingProgress,
                    borderColor: colors.warning,
                    backgroundColor: 'transparent',
                    borderWidth: 0,
                    pointRadius: 8,
                    pointHoverRadius: 10,
                    pointBackgroundColor: 'transparent',
                    pointBorderColor: colors.warning,
                    pointBorderWidth: 3,
                    pointStyle: 'circle',
                    showLine: false,
                    order: 5
                }
            ]
        },
        options: {
            ...options,
            scales: {
                x: options.scales.x,
                y: {
                    type: 'logarithmic',
                    grid: {
                        color: colors.grid,
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
                        color: colors.muted,
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
                ...options.plugins,
                annotation: {
                    annotations: {
                        humanLinePolice: {
                            type: 'line',
                            yMin: 500000,
                            yMax: 500000,
                            borderColor: colors.success,
                            borderWidth: 2,
                            borderDash: [8, 4]
                        },
                        humanLineInsurance: {
                            type: 'line',
                            yMin: 300000,
                            yMax: 300000,
                            borderColor: colors.purple,
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
    const colors = getChartColors();
    const options = getCommonOptions();

    // Destroy existing chart if present
    if (fleetChartInstance) {
        fleetChartInstance.destroy();
    }

    const labels = fleetData.map(d => d.date);
    const sizes = fleetData.map(d => d.size);

    // Get gradient colors based on theme
    const gradientStartAlpha = isDarkMode() ? 0.05 : 0.1;
    const gradientEndAlpha = isDarkMode() ? 0.4 : 0.3;

    fleetChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Fleet Size',
                data: sizes,
                fill: true,
                backgroundColor: (context) => {
                    const chart = context.chart;
                    const { ctx: chartCtx, chartArea } = chart;
                    if (!chartArea) return `rgba(59, 130, 246, ${gradientEndAlpha})`;

                    const gradient = chartCtx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                    gradient.addColorStop(0, `rgba(37, 99, 235, ${gradientStartAlpha})`);
                    gradient.addColorStop(1, `rgba(37, 99, 235, ${gradientEndAlpha})`);
                    return gradient;
                },
                borderColor: colors.primary,
                borderWidth: 2,
                pointRadius: 2,
                pointHoverRadius: 5,
                pointBackgroundColor: colors.primary,
                pointBorderColor: colors.primary,
                tension: 0.1
            }]
        },
        options: {
            ...options,
            plugins: {
                ...options.plugins,
                tooltip: {
                    ...options.plugins.tooltip,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
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
                ...options.scales,
                y: {
                    ...options.scales.y,
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
        `;
        tbody.appendChild(row);
    });
}

// ===== Update Metrics =====
function updateMetrics() {
    // Calculate metrics
    const latestMPI = incidentData[incidentData.length - 1].mpi;
    const previousMPI = incidentData[incidentData.length - 2].mpi;
    const totalIncidents = incidentData.length;
    const vsHuman = (500000 / latestMPI).toFixed(1);

    // Calculate miles since last incident
    const lastIncident = incidentData[incidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const currentFleetSize = fleetData[fleetData.length - 1].size;
    const milesSinceLastIncident = daysSinceLastIncident * currentFleetSize * 115;

    // Calculate change percentage
    const changePercent = Math.round(((latestMPI - previousMPI) / previousMPI) * 100);

    // Update DOM
    document.getElementById('latest-mpi').textContent = latestMPI.toLocaleString();
    document.getElementById('miles-since-incident').textContent = milesSinceLastIncident.toLocaleString();
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

// ===== Update Current Streak Comparison =====
function updateCurrentStreakComparison() {
    const lastIncident = incidentData[incidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const currentFleetSize = fleetData[fleetData.length - 1].size;
    const milesSinceLastIncident = daysSinceLastIncident * currentFleetSize * 115;

    // Update the value display
    const valueEl = document.getElementById('current-streak-value');
    if (valueEl) {
        valueEl.textContent = milesSinceLastIncident.toLocaleString();
    }

    // Update the bar width (relative to 1,000,000 as max)
    const barEl = document.getElementById('current-streak-bar');
    if (barEl) {
        const widthPercent = Math.min((milesSinceLastIncident / 1000000) * 100, 100);
        barEl.style.width = widthPercent.toFixed(2) + '%';
    }
}

// ===== Update Hero Streak Card =====
function updateHeroStreak() {
    const lastIncident = incidentData[incidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const currentFleetSize = fleetData[fleetData.length - 1].size;
    const milesSinceLastIncident = daysSinceLastIncident * currentFleetSize * 115;

    // Update the hero streak value
    const heroValueEl = document.getElementById('hero-streak-value');
    if (heroValueEl) {
        heroValueEl.textContent = milesSinceLastIncident.toLocaleString();
    }

    // Update the progress bar (relative to 500K target)
    const heroBarEl = document.getElementById('hero-streak-bar');
    if (heroBarEl) {
        const targetMiles = 500000;
        const widthPercent = Math.min((milesSinceLastIncident / targetMiles) * 100, 100);
        // Set width directly without animation delay to ensure correct value
        heroBarEl.style.width = widthPercent.toFixed(1) + '%';
    }
}

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
    updateHeroStreak();
    updateCurrentStreakComparison();
    animateComparisonBars();

    // Update date
    document.getElementById('last-updated').textContent = new Date().toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    // Listen for system theme changes and reinitialize charts
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            // Update chart colors
            chartColors = getChartColors();
            // Reinitialize charts with new theme colors
            initMPIChart();
            initFleetChart();
        });
    }
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

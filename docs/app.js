// ===== Data =====
// Updated with 115 mi/day/vehicle (validated from Tesla's 250K miles Q3 2025 report)
// Fleet sizes use total Austin fleet from fleet_data.json
//
// Data arrays are organized by filter combination:
// - Base: no backing incidents, no stationary incidents (most filtered, DEFAULT)
// - Stationary: no backing, WITH stationary incidents
// - Backing: WITH backing, no stationary incidents
// - All: WITH backing, WITH stationary incidents (least filtered)

// ===== Total Fleet Data (all filter combinations) =====
// Base: no backing, no stationary (11 incidents)
const incidentDataBase = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 12765, mpi: 3191, count: 4 },
    { date: '2025-09-15', days: 62, fleet: 14, miles: 96140, mpi: 32046, count: 3 },
    { date: '2025-10-15', days: 30, fleet: 17, miles: 60720, mpi: 30360, count: 2 },
    { date: '2025-12-10', days: 61, fleet: 24, miles: 168360, mpi: 168360, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 29, miles: 103385, mpi: 103385, count: 1 },
];

// Stationary: no backing, WITH stationary (15 incidents) - previous default
const incidentDataStationary = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 14145, mpi: 2829, count: 5 },
    { date: '2025-09-15', days: 62, fleet: 14, miles: 97865, mpi: 24466, count: 4 },
    { date: '2025-10-15', days: 30, fleet: 17, miles: 60720, mpi: 30360, count: 2 },
    { date: '2025-11-12', days: 31, fleet: 18, miles: 64170, mpi: 64170, count: 1 },
    { date: '2025-12-10', days: 30, fleet: 24, miles: 82800, mpi: 82800, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 31, miles: 107295, mpi: 53647, count: 2 },
];

// Backing: WITH backing, no stationary (13 incidents)
const incidentDataBacking = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 12765, mpi: 3191, count: 4 },
    { date: '2025-09-15', days: 62, fleet: 14, miles: 96140, mpi: 32046, count: 3 },
    { date: '2025-10-15', days: 30, fleet: 17, miles: 60720, mpi: 30360, count: 2 },
    { date: '2025-12-10', days: 61, fleet: 24, miles: 168360, mpi: 168360, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 32, miles: 111205, mpi: 37068, count: 3 },
];

// All: WITH backing, WITH stationary (17 incidents)
const incidentDataAll = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 14145, mpi: 2829, count: 5 },
    { date: '2025-09-15', days: 62, fleet: 14, miles: 97865, mpi: 24466, count: 4 },
    { date: '2025-10-15', days: 30, fleet: 17, miles: 60720, mpi: 30360, count: 2 },
    { date: '2025-11-12', days: 31, fleet: 18, miles: 64170, mpi: 64170, count: 1 },
    { date: '2025-12-10', days: 30, fleet: 24, miles: 82800, mpi: 82800, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 32, miles: 115115, mpi: 28778, count: 4 },
];

// ===== Active Fleet Data (all filter combinations) =====
// Base: no backing, no stationary
const incidentDataActiveBase = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 12650, mpi: 3162, count: 4 },
    { date: '2025-09-15', days: 62, fleet: 12, miles: 88550, mpi: 29516, count: 3 },
    { date: '2025-10-15', days: 30, fleet: 20, miles: 67965, mpi: 33982, count: 2 },
    { date: '2025-12-10', days: 61, fleet: 26, miles: 182390, mpi: 182390, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 26, miles: 92690, mpi: 92690, count: 1 },
];

// Stationary: no backing, WITH stationary
const incidentDataActiveStationary = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 13915, mpi: 2783, count: 5 },
    { date: '2025-09-15', days: 62, fleet: 12, miles: 90045, mpi: 22511, count: 4 },
    { date: '2025-10-15', days: 30, fleet: 20, miles: 67965, mpi: 33982, count: 2 },
    { date: '2025-11-12', days: 31, fleet: 21, miles: 74865, mpi: 74865, count: 1 },
    { date: '2025-12-10', days: 30, fleet: 26, miles: 89700, mpi: 89700, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 26, miles: 95795, mpi: 47897, count: 2 },
];

// Backing: WITH backing, no stationary
const incidentDataActiveBacking = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 12650, mpi: 3162, count: 4 },
    { date: '2025-09-15', days: 62, fleet: 12, miles: 88550, mpi: 29516, count: 3 },
    { date: '2025-10-15', days: 30, fleet: 20, miles: 67965, mpi: 33982, count: 2 },
    { date: '2025-12-10', days: 61, fleet: 26, miles: 182390, mpi: 182390, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 26, miles: 98900, mpi: 32966, count: 3 },
];

// All: WITH backing, WITH stationary
const incidentDataActiveAll = [
    { date: '2025-07-15', days: 6, fleet: 11, miles: 13915, mpi: 2783, count: 5 },
    { date: '2025-09-15', days: 62, fleet: 12, miles: 90045, mpi: 22511, count: 4 },
    { date: '2025-10-15', days: 30, fleet: 20, miles: 67965, mpi: 33982, count: 2 },
    { date: '2025-11-12', days: 31, fleet: 21, miles: 74865, mpi: 74865, count: 1 },
    { date: '2025-12-10', days: 30, fleet: 26, miles: 89700, mpi: 89700, count: 1 },
    { date: '2026-01-10', days: 31, fleet: 26, miles: 102005, mpi: 25501, count: 4 },
];

// Legacy aliases for backward compatibility
const incidentData = incidentDataStationary;
const incidentDataActive = incidentDataActiveStationary;

// Latest active fleet size (from fleet_growth_active.json)
const latestActiveFleetSize = 76428;

// Fleet mode toggle state: 'total' or 'active'
let fleetMode = 'total';

// Incident filter state: by default both are OFF (excluded)
let includeBackingIncidents = false;
let includeStationaryIncidents = false;

// Get current incident data based on fleet mode and filter settings
function getIncidentData() {
    const isActive = fleetMode === 'active';

    // Select the appropriate dataset based on filter combination
    if (includeBackingIncidents && includeStationaryIncidents) {
        return isActive ? incidentDataActiveAll : incidentDataAll;
    } else if (includeBackingIncidents) {
        return isActive ? incidentDataActiveBacking : incidentDataBacking;
    } else if (includeStationaryIncidents) {
        return isActive ? incidentDataActiveStationary : incidentDataStationary;
    } else {
        // Default: both filters OFF (most filtered data)
        return isActive ? incidentDataActiveBase : incidentDataBase;
    }
}

// Get current fleet size based on fleet mode
function getCurrentFleetSize() {
    return fleetMode === 'active' ? latestActiveFleetSize : fleetData[fleetData.length - 1].size;
}

// Total fleet size data (Austin unsupervised robotaxis)
// Interpolated daily from fleet_data.json austin_vehicles field
// Used for fleet growth chart and total fleet MPI calculations
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
    { date: '2026-01-25', size: 78 },
    { date: '2026-01-29', size: 80 },
    { date: '2026-01-31', size: 80 },
    { date: '2026-02-01', size: 81 },
    { date: '2026-02-02', size: 81 },
    { date: '2026-02-03', size: 81 },
    { date: '2026-02-04', size: 81 },
    { date: '2026-02-05', size: 82 },
    { date: '2026-02-06', size: 82 },
    { date: '2026-02-07', size: 82 },
    { date: '2026-02-08', size: 83 },
    { date: '2026-02-09', size: 85 },
    { date: '2026-02-10', size: 86 },
    { date: '2026-02-11', size: 86 },
    { date: '2026-02-12', size: 86 },
    { date: '2026-02-13', size: 86 },
    { date: '2026-02-14', size: 88 },
    { date: '2026-02-15', size: 88 },
    { date: '2026-02-16', size: 89 },
    { date: '2026-02-17', size: 89 },
    { date: '2026-02-18', size: 89 },
    { date: '2026-02-19', size: 89 },
    { date: '2026-02-20', size: 19 },
];

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

    // R² on log scale (appropriate for exponential regression)
    // Since we fit ln(MPI) = A + b*t, we compute R² in log space
    // This ensures R² is always between 0 and 1 for the log-linear model
    let ssResLog = 0, ssTotLog = 0;
    for (let i = 0; i < n; i++) {
        const predLog = A + b * x[i];  // predicted ln(MPI)
        ssResLog += (Y[i] - predLog) ** 2;
        ssTotLog += (Y[i] - meanY) ** 2;
    }
    const rSquared = ssTotLog > 0 ? 1 - ssResLog / ssTotLog : 0;

    const doublingTime = b > 0 ? Math.round(Math.log(2) / b) : Infinity;
    // 30-day forecast from last data point
    const lastDays = x[x.length - 1];
    const forecast30Day = Math.round(a * Math.exp(b * (lastDays + 30)));

    return { a, b, rSquared, doublingTime, dailyGrowth: b, forecast30Day };
}

const fit = computeExponentialFit(incidentData);
let trendParams = {
    exponential: { a: fit.a, b: fit.b },
    rSquared: fit.rSquared,
    doublingTime: fit.doublingTime,
    dailyGrowth: fit.dailyGrowth,
    forecast30Day: fit.forecast30Day
};

// Recompute trend params for the current fleet mode
function recomputeTrendParams() {
    const currentData = getIncidentData();
    const currentFit = computeExponentialFit(currentData);
    trendParams = {
        exponential: { a: currentFit.a, b: currentFit.b },
        rSquared: currentFit.rSquared,
        doublingTime: currentFit.doublingTime,
        dailyGrowth: currentFit.dailyGrowth,
        forecast30Day: currentFit.forecast30Day
    };
}

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

    // Prepare base data from incidents (uses current fleet mode)
    const currentIncidentData = getIncidentData();
    const startDate = new Date(currentIncidentData[0].date);
    const lastIncidentDate = new Date(currentIncidentData[currentIncidentData.length - 1].date);
    const today = new Date();

    // Build data arrays as {x, y} objects for time scale
    const mpiData = [];
    const trendDataPoints = [];
    const ongoingProgressData = [];

    // Add all incident data points (include full data for tooltip)
    currentIncidentData.forEach(d => {
        mpiData.push({ x: d.date, y: d.mpi, count: d.count || 1, miles: d.miles });
        const currentDate = new Date(d.date);
        const daysSinceStart = Math.floor((currentDate - startDate) / (1000 * 60 * 60 * 24));
        trendDataPoints.push({ x: d.date, y: Math.round(trendParams.exponential.a * Math.exp(trendParams.exponential.b * daysSinceStart)) });
    });

    // Extend trend projection to today (add monthly points after last incident)
    let projectionDate = new Date(lastIncidentDate);
    projectionDate.setDate(projectionDate.getDate() + 30);

    while (projectionDate <= today) {
        const dateStr = projectionDate.toISOString().split('T')[0];
        const daysSinceStart = Math.floor((projectionDate - startDate) / (1000 * 60 * 60 * 24));
        trendDataPoints.push({ x: dateStr, y: Math.round(trendParams.exponential.a * Math.exp(trendParams.exponential.b * daysSinceStart)) });
        projectionDate.setDate(projectionDate.getDate() + 30);
    }

    // Add today as final point with cumulative miles since last incident
    if (today > lastIncidentDate) {
        const todayStr = today.toISOString().split('T')[0];

        // Add trend for today if not already the last point
        const lastTrendDate = trendDataPoints[trendDataPoints.length - 1].x;
        if (lastTrendDate !== todayStr) {
            const daysSinceStart = Math.floor((today - startDate) / (1000 * 60 * 60 * 24));
            trendDataPoints.push({ x: todayStr, y: Math.round(trendParams.exponential.a * Math.exp(trendParams.exponential.b * daysSinceStart)) });
        }

        // Calculate cumulative miles since last incident (excluding stoppage days)
        const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
        const stoppageDays = countStoppageDays(lastIncidentDate, today);
        const activeDays = daysSinceLastIncident - stoppageDays;
        const currentFleetSize = getCurrentFleetSize();
        const cumulativeMiles = activeDays * currentFleetSize * 115;
        ongoingProgressData.push({ x: todayStr, y: cumulativeMiles });
    }

    // Benchmark lines - two points each (start to end) for constant horizontal lines
    const firstDate = currentIncidentData[0].date;
    const lastDate = today.toISOString().split('T')[0];
    const humanBenchmarkPoliceData = [
        { x: firstDate, y: 500000 },
        { x: lastDate, y: 500000 }
    ];
    const humanBenchmarkInsuranceData = [
        { x: firstDate, y: 300000 },
        { x: lastDate, y: 300000 }
    ];

    mpiChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Miles per Incident',
                    data: mpiData,
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
                    label: 'Exponential Trend',
                    data: trendDataPoints,
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
                    data: humanBenchmarkPoliceData,
                    borderColor: colors.success,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [8, 4],
                    pointRadius: 0,
                    order: 3
                },
                {
                    label: 'Human Benchmark - Insurance Claims (300K)',
                    data: humanBenchmarkInsuranceData,
                    borderColor: colors.purple,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [4, 4],
                    pointRadius: 0,
                    order: 4
                },
                {
                    label: 'Miles Since Last Incident',
                    data: ongoingProgressData,
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
                x: {
                    type: 'time',
                    time: {
                        unit: 'month',
                        displayFormats: {
                            month: 'yyyy-MM-dd'
                        }
                    },
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
                y: chartScaleMode === 'log' ? {
                    type: 'logarithmic',
                    grid: {
                        color: colors.grid,
                        drawBorder: false
                    },
                    min: 1000,
                    max: 1000000,
                    afterBuildTicks: function(axis) {
                        axis.ticks = [
                            { value: 1000 },
                            { value: 2000 },
                            { value: 5000 },
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
                            if (value === 1000) return '1K';
                            if (value === 2000) return '2K';
                            if (value === 5000) return '5K';
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
                } : {
                    type: 'linear',
                    grid: {
                        color: colors.grid,
                        drawBorder: false
                    },
                    min: 0,
                    beginAtZero: true,
                    ticks: {
                        color: colors.muted,
                        font: { family: "'JetBrains Mono', monospace", size: 11 },
                        callback: function(value) {
                            if (value === 0) return '0';
                            if (value >= 1000000) return (value / 1000000) + 'M';
                            return (value / 1000) + 'K';
                        }
                    }
                }
            },
            plugins: {
                ...options.plugins,
                tooltip: {
                    ...options.plugins.tooltip,
                    callbacks: {
                        title: function(context) {
                            // Format as "Month YYYY"
                            const date = new Date(context[0].raw.x);
                            return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
                        },
                        label: function(context) {
                            const raw = context.raw;
                            // Only show detailed info for MPI data points (red dots)
                            if (context.dataset.label === 'Miles per Incident' && raw.count !== undefined) {
                                return [
                                    'Incidents: ' + raw.count,
                                    'Total Miles: ' + raw.miles.toLocaleString(),
                                    'MPI: ' + raw.y.toLocaleString()
                                ];
                            }
                            // Default label for other datasets
                            const value = context.parsed.y;
                            if (value === null) return null;
                            if (value >= 1000) {
                                return Math.round(value / 1000) + 'K miles';
                            }
                            return value.toLocaleString() + ' miles';
                        }
                    }
                },
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
                pointRadius: 0,
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
                    max: 100
                }
            }
        }
    });
}

// ===== Populate Table =====
function populateIncidentTable() {
    const tbody = document.getElementById('incident-table-body');
    tbody.innerHTML = '';
    const currentIncidentData = getIncidentData();

    // Format date as "Month YYYY" (e.g., "Jul 2025")
    const formatMonth = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    };

    currentIncidentData.forEach((incident) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatMonth(incident.date)}</td>
            <td>${incident.count || 1}</td>
            <td>${incident.fleet}</td>
            <td>${incident.miles.toLocaleString()}</td>
            <td>${incident.mpi.toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// ===== Update Metrics =====
function updateMetrics() {
    // Calculate metrics (uses current fleet mode)
    const currentIncidentData = getIncidentData();
    const latestMPI = currentIncidentData[currentIncidentData.length - 1].mpi;
    const previousMPI = currentIncidentData[currentIncidentData.length - 2].mpi;
    const totalIncidents = currentIncidentData.reduce((sum, d) => sum + (d.count || 1), 0);
    const vsHuman = (500000 / latestMPI).toFixed(1);

    // Calculate miles since last incident (excluding stoppage days)
    const lastIncident = currentIncidentData[currentIncidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const currentFleetSize = getCurrentFleetSize();
    const milesSinceLastIncident = activeDays * currentFleetSize * 115;

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
document.querySelectorAll('a[href^="#"]:not(.share-icon):not(.btn-share-x):not(.btn-share-reddit)').forEach(anchor => {
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
    const currentIncidentData = getIncidentData();
    const lastIncident = currentIncidentData[currentIncidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const currentFleetSize = getCurrentFleetSize();
    const milesSinceLastIncident = activeDays * currentFleetSize * 115;

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
    const currentIncidentData = getIncidentData();
    const lastIncident = currentIncidentData[currentIncidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const currentFleetSize = getCurrentFleetSize();
    const milesSinceLastIncident = activeDays * currentFleetSize * 115;

    const targetMiles = 500000;
    const exceededHumanLevel = milesSinceLastIncident >= targetMiles;

    // Update the hero streak value
    const heroValueEl = document.getElementById('hero-streak-value');
    if (heroValueEl) {
        heroValueEl.textContent = milesSinceLastIncident.toLocaleString();
    }

    // Get all elements we need to update
    const heroBarEl = document.getElementById('hero-streak-bar');
    const heroTargetEl = document.getElementById('hero-streak-target');
    const heroContextEl = document.getElementById('hero-streak-context');
    const heroLabelEl = document.getElementById('hero-streak-label');
    const heroSublabelEl = document.getElementById('hero-streak-sublabel');
    const heroCardEl = document.querySelector('.hero-streak-card');

    if (exceededHumanLevel) {
        // Calculate how many times safer than human drivers
        const safetyMultiplier = milesSinceLastIncident / targetMiles;
        const formattedMultiplier = safetyMultiplier.toFixed(1);

        // Update to show safety comparison mode
        if (heroBarEl) {
            heroBarEl.style.width = '100%';
            heroBarEl.classList.add('exceeded');
        }
        if (heroTargetEl) {
            heroTargetEl.textContent = formattedMultiplier + 'x';
            heroTargetEl.classList.add('exceeded');
        }
        if (heroContextEl) {
            heroContextEl.innerHTML = '<span class="safety-highlight">' + formattedMultiplier + 'x safer</span> than human drivers (police-reported)';
        }
        if (heroCardEl) {
            heroCardEl.classList.add('exceeded-human-level');
        }
    } else {
        // Normal progress mode
        if (heroBarEl) {
            const widthPercent = (milesSinceLastIncident / targetMiles) * 100;
            heroBarEl.style.width = widthPercent.toFixed(1) + '%';
            heroBarEl.classList.remove('exceeded');
        }
        if (heroTargetEl) {
            heroTargetEl.textContent = '500K';
            heroTargetEl.classList.remove('exceeded');
        }
        if (heroContextEl) {
            heroContextEl.textContent = 'Human driver benchmark (police-reported)';
        }
        if (heroCardEl) {
            heroCardEl.classList.remove('exceeded-human-level');
        }
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

// ===== Update FAQ Dynamic Values =====
function updateFaqValues() {
    const currentIncidentData = getIncidentData();
    const latestMPI = currentIncidentData[currentIncidentData.length - 1].mpi;
    const previousMPI = currentIncidentData[currentIncidentData.length - 2].mpi;
    const totalIncidents = currentIncidentData.reduce((sum, d) => sum + (d.count || 1), 0);
    const changePercent = Math.round(((latestMPI - previousMPI) / previousMPI) * 100);
    const waymoRatio = Math.round(1000000 / latestMPI);
    const vsHumanRatio = (500000 / latestMPI).toFixed(1);
    const vsInsuranceRatio = (300000 / latestMPI).toFixed(1);
    const currentFleetSize = getCurrentFleetSize();

    // Calculate current streak
    const lastIncident = currentIncidentData[currentIncidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const milesSinceLastIncident = activeDays * currentFleetSize * 115;

    // Calculate months to match human drivers (insurance-adjusted: 300K)
    const monthsToHuman = Math.ceil((Math.log(300000 / latestMPI) / trendParams.dailyGrowth) / 30);

    // Calculate Waymo percentage
    const waymoPct = (latestMPI / 1000000 * 100).toFixed(1);

    // Format current date
    const dateOptions = { month: 'long', day: 'numeric', year: 'numeric' };
    const currentDateStr = today.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    const currentDateFull = today.toLocaleDateString('en-US', dateOptions);
    const lastIncidentDateStr = lastIncidentDate.toLocaleDateString('en-US', dateOptions);

    // Populate visible FAQ spans
    const setValue = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };

    // Original FAQ values
    setValue('faq-latest-mpi', latestMPI.toLocaleString());
    setValue('faq-latest-mpi-2', latestMPI.toLocaleString());
    setValue('faq-latest-mpi-3', latestMPI.toLocaleString());
    setValue('faq-doubling-time', trendParams.doublingTime);
    setValue('faq-doubling-time-2', trendParams.doublingTime);
    setValue('faq-doubling-time-3', trendParams.doublingTime);
    setValue('faq-total-incidents', totalIncidents);
    setValue('faq-change-percent', changePercent);
    setValue('faq-r-squared', trendParams.rSquared.toFixed(3));
    setValue('faq-waymo-ratio', waymoRatio);

    // New AEO FAQ values (Q9-Q12)
    setValue('faq-current-date', currentDateStr);
    setValue('faq-current-date-2', currentDateFull);
    setValue('faq-latest-mpi-4', latestMPI.toLocaleString());
    setValue('faq-latest-mpi-5', latestMPI.toLocaleString());
    setValue('faq-latest-mpi-6', latestMPI.toLocaleString());
    setValue('faq-latest-mpi-7', latestMPI.toLocaleString());
    setValue('faq-latest-mpi-8', latestMPI.toLocaleString());
    setValue('faq-doubling-time-4', trendParams.doublingTime);
    setValue('faq-doubling-time-5', trendParams.doublingTime);
    setValue('faq-doubling-time-6', trendParams.doublingTime);
    setValue('faq-forecast-mpi', trendParams.forecast30Day.toLocaleString());
    setValue('faq-total-incidents-2', totalIncidents);
    setValue('faq-total-incidents-3', totalIncidents);
    setValue('faq-current-streak', milesSinceLastIncident.toLocaleString());
    setValue('faq-current-streak-2', milesSinceLastIncident.toLocaleString());
    setValue('faq-fleet-size', currentFleetSize);
    setValue('faq-last-incident-date', lastIncidentDateStr);
    setValue('faq-vs-human-ratio', vsHumanRatio);
    setValue('faq-vs-insurance-ratio', vsInsuranceRatio);
    setValue('faq-vs-waymo-ratio', waymoRatio);

    // News debunking FAQ values (Q13-Q14)
    const simpleAvgMPI = Math.round(currentIncidentData.reduce((sum, d) => sum + d.mpi, 0) / totalIncidents);
    const latestVsAvg = (latestMPI / simpleAvgMPI).toFixed(1);
    setValue('faq-news-total-incidents', totalIncidents);
    setValue('faq-simple-avg-mpi', simpleAvgMPI.toLocaleString());
    setValue('faq-news-latest-mpi', latestMPI.toLocaleString());
    setValue('faq-latest-vs-avg', latestVsAvg);
    setValue('faq-news-doubling', trendParams.doublingTime);
    setValue('faq-news-r-squared', trendParams.rSquared.toFixed(3));
    setValue('faq-news-current-streak', milesSinceLastIncident.toLocaleString());
    setValue('faq-news-fleet-size', currentFleetSize);
    setValue('faq-redact-r-squared', trendParams.rSquared.toFixed(3));
    setValue('faq-redact-doubling', trendParams.doublingTime);

    // New Task 12 FAQ values
    setValue('faq-safe-mpi', latestMPI.toLocaleString());
    setValue('faq-safe-doubling', trendParams.doublingTime);

    // AEO Summary section values
    setValue('aeo-current-streak', milesSinceLastIncident.toLocaleString());
    setValue('aeo-fleet-size', currentFleetSize);
    setValue('aeo-latest-mpi', latestMPI.toLocaleString());
    setValue('aeo-doubling-time', trendParams.doublingTime);
    setValue('aeo-vs-human', vsHumanRatio);

    // Update AEO datestamp
    const aeoDatestamp = document.getElementById('aeo-datestamp');
    if (aeoDatestamp) {
        aeoDatestamp.textContent = currentDateFull;
        aeoDatestamp.setAttribute('datetime', today.toISOString().split('T')[0]);
    }

    // Key Insights table values
    setValue('insight-latest-mpi', latestMPI.toLocaleString());
    setValue('insight-latest-mpi-2', latestMPI.toLocaleString());
    setValue('insight-r-squared', trendParams.rSquared.toFixed(3));
    setValue('insight-doubling', trendParams.doublingTime);
    setValue('insight-months-to-human', monthsToHuman);
    setValue('insight-streak', milesSinceLastIncident.toLocaleString());
    setValue('insight-fleet', currentFleetSize);
    setValue('insight-waymo-pct', waymoPct);

    // Myths section values
    setValue('myth-total-incidents', totalIncidents);
    setValue('myth-fleet-size', currentFleetSize);
    setValue('myth-latest-mpi', latestMPI.toLocaleString());
    setValue('myth-current-streak', milesSinceLastIncident.toLocaleString());
    setValue('myth-doubling', trendParams.doublingTime);
    setValue('myth-r-squared', trendParams.rSquared.toFixed(3));

    // Share section values
    setValue('share-mpi', latestMPI.toLocaleString());
    setValue('share-doubling', trendParams.doublingTime);
    setValue('share-streak', milesSinceLastIncident.toLocaleString());

    // Parity projection: compute predicted date when MPI reaches 500K (police-reported benchmark)
    const lastIncidentDateForParity = new Date(currentIncidentData[currentIncidentData.length - 1].date);
    const daysToPolice500K = Math.ceil(Math.log(500000 / latestMPI) / trendParams.dailyGrowth);
    const parityDate = new Date(lastIncidentDateForParity);
    parityDate.setDate(parityDate.getDate() + daysToPolice500K);
    const parityDateStr = parityDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    setValue('parity-date', parityDateStr);
    setValue('parity-date-2', parityDateStr);
    setValue('parity-r-squared', trendParams.rSquared.toFixed(3));
    setValue('parity-doubling', trendParams.doublingTime);

    // Update share buttons for share-data section
    const pageUrl = 'https://robotaxi-safety-tracker.com/';
    const shareDataText = 'Tesla Robotaxi Safety Data:\n\n' +
        '- Latest MPI: ' + latestMPI.toLocaleString() + ' miles per incident\n' +
        '- Safety doubling every ' + trendParams.doublingTime + ' days\n' +
        '- Current streak: ' + milesSinceLastIncident.toLocaleString() + ' miles without an incident\n\n' +
        'Real-time data from NHTSA reports:';
    const shareDataXEl = document.getElementById('share-data-x');
    if (shareDataXEl) {
        shareDataXEl.href = 'https://x.com/intent/tweet?text=' + encodeURIComponent(shareDataText) + '&url=' + encodeURIComponent(pageUrl);
    }
    const shareDataRedditEl = document.getElementById('share-data-reddit-2');
    if (shareDataRedditEl) {
        shareDataRedditEl.href = 'https://www.reddit.com/submit?url=' + encodeURIComponent(pageUrl) + '&title=' + encodeURIComponent('Tesla Robotaxi Safety: ' + latestMPI.toLocaleString() + ' MPI, Doubling Every ' + trendParams.doublingTime + ' Days');
    }

    // Update JSON-LD FAQPage schema with computed values (including new AEO questions)
    const faqSchemaEl = document.getElementById('faq-schema');
    if (faqSchemaEl) {
        const faqSchema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "How is robotaxi safety measured and tracked?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Robotaxi safety is primarily measured using miles per incident (MPI) — the average distance a robotaxi drives between crashes or reportable incidents. Higher MPI means better safety. In the U.S., all autonomous driving system (ADS) incidents must be reported to NHTSA under Standing General Order 2021-01, providing a transparent public record of robotaxi safety performance. This tracker monitors robotaxi safety for Tesla's Cybercab fleet in Austin, TX — the only fully unsupervised (Level 4) Tesla robotaxi deployment. Key robotaxi safety metrics include MPI trend over time, comparison to human driver crash rates, and fleet-wide incident frequency. Waymo, the other major U.S. robotaxi operator, publishes its own safety data showing over 1,000,000 MPI."
                    }
                },
                {
                    "@type": "Question",
                    "name": "How safe are Tesla robotaxis compared to human drivers?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Tesla robotaxis in Austin average approximately " + latestMPI.toLocaleString() + " miles between incidents. For comparison, human drivers average about 500,000 miles between police-reported crashes, or approximately 300,000 miles between insurance claims. Tesla's safety is improving rapidly, with the interval between incidents doubling approximately every " + trendParams.doublingTime + " days."
                    }
                },
                {
                    "@type": "Question",
                    "name": "How many Tesla robotaxi incidents have occurred?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Tesla has reported " + totalIncidents + " incidents to NHTSA since launching in Austin in June 2025. All incidents occurred in Austin, Texas, where Tesla operates unsupervised autonomous driving (Level 4). Some Austin vehicles now run without safety monitors, though most still have monitors present. The Bay Area fleet operates with safety drivers as required by California law, and follows different reporting requirements."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Is Tesla robotaxi safety improving?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Yes, significantly. Our analysis shows Tesla robotaxi safety is doubling approximately every " + trendParams.doublingTime + " days. The most recent interval between incidents reached " + latestMPI.toLocaleString() + " miles — a " + changePercent + "% improvement from the previous interval. This exponential improvement trend (R\u00B2 = " + trendParams.rSquared.toFixed(3) + ") suggests the system is learning and becoming safer over time."
                    }
                },
                {
                    "@type": "Question",
                    "name": "How does Tesla robotaxi compare to Waymo?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Waymo reports approximately 1,000,000+ miles per incident based on their published safety data. Tesla's latest interval is " + latestMPI.toLocaleString() + " miles per incident — roughly " + waymoRatio + "x less than Waymo's reported figures. However, Tesla's rapid improvement rate (doubling every ~" + trendParams.doublingTime + " days) could narrow this gap significantly if the trend continues."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Where does Tesla operate robotaxis?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Tesla currently operates robotaxis in two markets: Austin, Texas (unsupervised, with some vehicles already running without safety monitors) and the San Francisco Bay Area (with safety drivers, required by California law). Tesla has announced plans to expand to Dallas, Houston, Phoenix, Miami, Orlando, Tampa, and Las Vegas in the first half of 2026."
                    }
                },
                {
                    "@type": "Question",
                    "name": "What is Tesla's robotaxi fleet size?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "As of the Q4 2025 earnings call, Tesla reported 'well over 500' vehicles across Austin and the Bay Area carrying paid customers. Elon Musk stated the fleet is expected to 'double every month.' This tracker monitors the Austin fleet specifically, as it's the only location with true unsupervised autonomous driving."
                    }
                },
                {
                    "@type": "Question",
                    "name": "How is Tesla robotaxi safety data calculated?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Miles per incident is calculated by: (1) Tracking fleet size daily from robotaxitracker.com and news sources; (2) Estimating daily miles using 115 miles/vehicle/day based on Tesla's Q3 2025 report; (3) Recording incidents from NHTSA Standing General Order crash reports. An exponential trend model is then fitted to identify the improvement rate."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Why does this tracker focus only on Austin data?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Austin is the only location where Tesla operates unsupervised Level 4 autonomous driving, which requires incident reporting to NHTSA under Standing General Order 2021-01. Some Austin vehicles already run without safety monitors, though most still have monitors. The Bay Area fleet operates with safety drivers (Level 2) as required by California law — Tesla must accumulate sufficient supervised miles before applying for driverless permits. Comparing only Austin data ensures consistency."
                    }
                },
                {
                    "@type": "Question",
                    "name": "What is the current Tesla Robotaxi MPI?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "As of " + currentDateStr + ", the current Tesla Robotaxi Miles Per Incident (MPI) is " + latestMPI.toLocaleString() + " miles. This means the Tesla Cybercab fleet in Austin, TX drives an average of " + latestMPI.toLocaleString() + " miles between each reported incident. The improvement rate shows safety doubling every " + trendParams.doublingTime + " days, with a 30-day forecast of " + trendParams.forecast30Day.toLocaleString() + " MPI. Total incidents tracked: " + totalIncidents + " since June 2025. Current streak: " + milesSinceLastIncident.toLocaleString() + " miles without an incident."
                    }
                },
                {
                    "@type": "Question",
                    "name": "How does Tesla Robotaxi safety compare to human drivers in 2026?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "As of January 2026, Tesla Robotaxi is " + vsHumanRatio + "x worse than human drivers based on police-reported crashes (500,000 MPI), " + vsInsuranceRatio + "x worse based on insurance claims (300,000 MPI), and " + waymoRatio + "x worse than Waymo (1,000,000+ MPI). However, Tesla's safety is doubling every ~" + trendParams.doublingTime + " days. At this rate, Tesla could match human driver safety levels (insurance-adjusted) within months if the exponential trend continues. Data sourced from NHTSA CRSS 2023 and the Swiss Re/Waymo safety study."
                    }
                },
                {
                    "@type": "Question",
                    "name": "How many miles has Tesla Robotaxi driven without a crash?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "As of " + currentDateFull + ", Tesla Robotaxi has driven " + milesSinceLastIncident.toLocaleString() + " miles without an incident in Austin, TX. The fleet of " + currentFleetSize + " unsupervised vehicles has been operating incident-free since " + lastIncidentDateStr + ". This ongoing streak already exceeds the latest completed interval of " + latestMPI.toLocaleString() + " miles, suggesting continued safety improvement."
                    }
                },
                {
                    "@type": "Question",
                    "name": "What is Tesla Robotaxi's crash frequency?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Tesla Robotaxi crash frequency as of January 2026: " + totalIncidents + " total incidents reported to NHTSA since June 2025. Latest crash rate: 1 incident per " + latestMPI.toLocaleString() + " miles driven. Crash frequency is decreasing, with MPI doubling every " + trendParams.doublingTime + " days. All incidents are reported under NHTSA SGO 2021-01, which requires reporting any crash within 30 seconds of ADS engagement. This captures all incidents regardless of severity, including minor ones that human drivers would typically never report to police."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Are reports that Tesla Robotaxi crashes 10x-12x more than humans accurate?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Headlines claiming Tesla Robotaxis crash '10x' or '12x more than human drivers' are based on simple averages of past performance that miss a critical trend. The current incident-free streak is " + milesSinceLastIncident.toLocaleString() + " miles — already approaching the human driver benchmark of 500,000 miles between police-reported crashes. Safety is doubling every " + trendParams.doublingTime + " days (R² = " + trendParams.rSquared.toFixed(3) + "), an exponential improvement that simple averages completely hide. The latest completed interval was " + latestMPI.toLocaleString() + " MPI, already " + latestVsAvg + "x better than the simple average of ~" + simpleAvgMPI.toLocaleString() + " MPI. These news articles treat crash data as a static snapshot; our trend analysis shows a system improving at an exponential rate toward human-level safety. Sources: Carscoops, Common Dreams, Electrek, Futurism, PHTM."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Is Tesla robotaxi safer than human drivers?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Not yet, on a simple average basis. Tesla Robotaxi's latest interval between incidents is " + latestMPI.toLocaleString() + " miles, compared to human drivers' 500,000 miles between police-reported crashes. However, safety is doubling every ~" + trendParams.doublingTime + " days, meaning Tesla is on an exponential trajectory toward parity. The comparison is complicated by reporting differences: NHTSA SGO 2021-01 captures all incidents including minor ones, while human crash statistics only count police-reported events."
                    }
                },
                {
                    "@type": "Question",
                    "name": "What is miles per incident and why does it matter?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Miles per incident (MPI) measures the average distance an autonomous vehicle drives between reportable incidents. It is the primary safety metric for comparing AV performance against human drivers and other AV operators like Waymo. Higher MPI equals a safer vehicle. Human drivers average ~500,000 miles between police-reported crashes (~300,000 between insurance claims). Waymo reports 1,000,000+ MPI."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Does NHTSA SGO 2021-01 include minor crashes?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Yes. NHTSA Standing General Order 2021-01 requires AV operators to report any crash where the automated driving system was engaged within 30 seconds of the incident, regardless of severity. This includes minor fender-benders and incidents where the AV was stationary. By contrast, human crash statistics only count police-reported crashes, which miss an estimated 60% of property-damage-only incidents."
                    }
                },
                {
                    "@type": "Question",
                    "name": "How does reporting lag affect the safety streak?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "NHTSA SGO 2021-01 requires initial crash reports within 1 day and updated reports within 10 days. However, Tesla has been cited for delayed reporting. This means the current streak number may be artificially high if an incident occurred recently but hasn't appeared in the public NHTSA database. We treat streak data as provisional until the reporting window catches up (typically 2-4 weeks)."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Does Tesla redact Robotaxi crash data from NHTSA reports?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Yes, Tesla redacts crash narrative details from NHTSA Standing General Order reports, as reported by Carscoops, Sherwood News, and WebProNews. However, this does not affect the core safety metrics tracked here. This tracker uses only structured, non-redacted NHTSA SGO data: incident dates, ADS engagement status, fleet size (from robotaxitracker.com), and daily miles (115 mi/vehicle/day from Tesla's Q3 2025 report). The MPI trend (R² = " + trendParams.rSquared.toFixed(3) + ") and safety doubling time (" + trendParams.doublingTime + " days) are fully calculable from non-redacted data."
                    }
                }
            ]
        };
        faqSchemaEl.textContent = JSON.stringify(faqSchema);
    }

    // Update Article schema dateModified dynamically
    const statsSchemaEl = document.getElementById('stats-schema');
    if (statsSchemaEl) {
        try {
            const statsSchema = JSON.parse(statsSchemaEl.textContent);
            statsSchema.dateModified = today.toISOString().split('T')[0];
            statsSchemaEl.textContent = JSON.stringify(statsSchema);
        } catch (e) {
            // Schema update failed silently
        }
    }

    // Dynamically update meta tags with computed values
    const setMeta = (selector, content) => {
        const el = document.querySelector(selector);
        if (el) el.setAttribute('content', content);
    };
    const latestMPIFormatted = latestMPI.toLocaleString();
    const dt = trendParams.doublingTime;

    setMeta('meta[name="description"]',
        'Live Tesla Robotaxi safety data: ' + latestMPIFormatted + ' miles per incident, ' + dt + '-day doubling time, Austin fleet status. Independent tracking of Cybercab crash rates vs human drivers and Waymo.');
    setMeta('meta[property="og:description"]',
        'Independent safety tracking: Tesla Cybercab achieving ' + latestMPIFormatted + ' miles between incidents in Austin. Safety doubling every ' + dt + ' days. Compare to human drivers & Waymo.');
    setMeta('meta[name="twitter:description"]',
        'Live safety data: ' + latestMPIFormatted + ' MPI, ' + dt + '-day doubling time. Track Tesla Cybercab incidents vs human drivers.');
}

// ===== Fleet Mode Toggle =====
function setFleetMode(mode) {
    if (mode === fleetMode) return;
    fleetMode = mode;

    // Recompute trend params for new data
    recomputeTrendParams();

    // Update toggle button states
    document.querySelectorAll('.fleet-toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Reinitialize chart and metrics with new data
    initMPIChart();
    populateIncidentTable();
    updateMetrics();
    updateHeroStreak();
    updateCurrentStreakComparison();

    // Update stat cards
    const statDoublingEl = document.getElementById('stat-doubling-time');
    if (statDoublingEl) statDoublingEl.textContent = trendParams.doublingTime + ' days';
    const statDoublingDetailEl = document.getElementById('stat-doubling-detail');
    if (statDoublingDetailEl) {
        const months = (trendParams.doublingTime / 30).toFixed(1);
        statDoublingDetailEl.textContent = 'Safety doubles every ~' + months + ' months';
    }
    const statRSquaredEl = document.getElementById('stat-r-squared');
    if (statRSquaredEl) statRSquaredEl.textContent = 'R\u00B2 = ' + trendParams.rSquared.toFixed(3);
    const statGrowthEl = document.getElementById('stat-daily-growth');
    if (statGrowthEl) statGrowthEl.textContent = '+' + (trendParams.dailyGrowth * 100).toFixed(1) + '%';
    const statForecastEl = document.getElementById('stat-forecast');
    if (statForecastEl) statForecastEl.textContent = trendParams.forecast30Day.toLocaleString();
    const statEquationEl = document.getElementById('stat-equation');
    if (statEquationEl) {
        const aVal = Math.round(trendParams.exponential.a).toLocaleString();
        const bVal = trendParams.exponential.b.toFixed(4);
        statEquationEl.innerHTML = 'MPI = ' + aVal + '·e<sup>' + bVal + 't</sup>';
    }
}

// ===== Incident Filter Toggle =====
function updateIncidentFilters() {
    // Get current checkbox states
    const backingCheckbox = document.getElementById('filter-backing');
    const stationaryCheckbox = document.getElementById('filter-stationary');

    if (backingCheckbox) includeBackingIncidents = backingCheckbox.checked;
    if (stationaryCheckbox) includeStationaryIncidents = stationaryCheckbox.checked;

    // Recompute trend params for new data
    recomputeTrendParams();

    // Reinitialize chart and metrics with new data
    initMPIChart();
    populateIncidentTable();
    updateMetrics();
    updateHeroStreak();
    updateCurrentStreakComparison();
    updateFaqValues();

    // Update stat cards
    const statDoublingEl = document.getElementById('stat-doubling-time');
    if (statDoublingEl) statDoublingEl.textContent = trendParams.doublingTime + ' days';
    const statDoublingDetailEl = document.getElementById('stat-doubling-detail');
    if (statDoublingDetailEl) {
        const months = (trendParams.doublingTime / 30).toFixed(1);
        statDoublingDetailEl.textContent = 'Safety doubles every ~' + months + ' months';
    }
    const statRSquaredEl = document.getElementById('stat-r-squared');
    if (statRSquaredEl) statRSquaredEl.textContent = 'R\u00B2 = ' + trendParams.rSquared.toFixed(3);
    const statGrowthEl = document.getElementById('stat-daily-growth');
    if (statGrowthEl) statGrowthEl.textContent = '+' + (trendParams.dailyGrowth * 100).toFixed(1) + '%';
    const statForecastEl = document.getElementById('stat-forecast');
    if (statForecastEl) statForecastEl.textContent = trendParams.forecast30Day.toLocaleString();
    const statEquationEl = document.getElementById('stat-equation');
    if (statEquationEl) {
        const aVal = Math.round(trendParams.exponential.a).toLocaleString();
        const bVal = trendParams.exponential.b.toFixed(4);
        statEquationEl.innerHTML = 'MPI = ' + aVal + '·e<sup>' + bVal + 't</sup>';
    }
}

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    initMPIChart();
    initFleetChart();
    populateIncidentTable();
    updateMetrics();
    updateHeroStreak();
    updateCurrentStreakComparison();
    updateFaqValues();
    animateComparisonBars();

    // Set up fleet mode toggle buttons
    document.querySelectorAll('.fleet-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => setFleetMode(btn.dataset.mode));
    });

    // Set up incident filter checkboxes
    const backingCheckbox = document.getElementById('filter-backing');
    const stationaryCheckbox = document.getElementById('filter-stationary');
    if (backingCheckbox) {
        backingCheckbox.addEventListener('change', updateIncidentFilters);
    }
    if (stationaryCheckbox) {
        stationaryCheckbox.addEventListener('change', updateIncidentFilters);
    }

    // Set up scale toggle buttons
    document.querySelectorAll('.scale-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => setChartScale(btn.dataset.scale));
    });

    // Update Best Fit Model card with equation and R² details
    const statEquationEl = document.getElementById('stat-equation');
    if (statEquationEl) {
        const aVal = Math.round(trendParams.exponential.a).toLocaleString();
        const bVal = trendParams.exponential.b.toFixed(4);
        statEquationEl.innerHTML = 'MPI = ' + aVal + '·e<sup>' + bVal + 't</sup>';
    }

    // Update stat cards from computed trendParams
    const heroEl = document.getElementById('hero-doubling-time');
    if (heroEl) heroEl.textContent = trendParams.doublingTime;
    const statDoublingEl = document.getElementById('stat-doubling-time');
    if (statDoublingEl) statDoublingEl.textContent = trendParams.doublingTime + ' days';
    const statDoublingDetailEl = document.getElementById('stat-doubling-detail');
    if (statDoublingDetailEl) {
        const months = (trendParams.doublingTime / 30).toFixed(1);
        statDoublingDetailEl.textContent = 'Safety doubles every ~' + months + ' months';
    }
    const statRSquaredEl = document.getElementById('stat-r-squared');
    if (statRSquaredEl) statRSquaredEl.textContent = 'R\u00B2 = ' + trendParams.rSquared.toFixed(3);
    const statGrowthEl = document.getElementById('stat-daily-growth');
    if (statGrowthEl) statGrowthEl.textContent = '+' + (trendParams.dailyGrowth * 100).toFixed(1) + '%';
    const statForecastEl = document.getElementById('stat-forecast');
    if (statForecastEl) statForecastEl.textContent = trendParams.forecast30Day.toLocaleString();

    // Update date
    document.getElementById('last-updated').textContent = new Date().toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    // Set up share button URLs
    const pageUrl = 'https://robotaxi-safety-tracker.com/';
    const shareTitle = 'Tesla Robotaxi Safety is Doubling Every ' + trendParams.doublingTime + ' Days';
    const shareText = shareTitle + '\n\nTracking Tesla\'s autonomous vehicle safety improvements with real NHTSA data.';

    const shareXEl = document.getElementById('share-x');
    if (shareXEl) {
        shareXEl.href = 'https://x.com/intent/tweet?text=' + encodeURIComponent(shareText) + '&url=' + encodeURIComponent(pageUrl);
    }

    const shareRedditEl = document.getElementById('share-reddit');
    if (shareRedditEl) {
        shareRedditEl.href = 'https://www.reddit.com/submit?url=' + encodeURIComponent(pageUrl) + '&title=' + encodeURIComponent(shareTitle);
    }

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

// ===== Chart Scale Toggle (Task 5) =====
let chartScaleMode = 'log'; // 'log' or 'linear'

function setChartScale(scale) {
    if (scale === chartScaleMode) return;
    chartScaleMode = scale;

    // Update toggle button states
    document.querySelectorAll('.scale-toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.scale === scale);
    });

    // Reinitialize chart with new scale
    if (mpiChartInstance) {
        mpiChartInstance.destroy();
        mpiChartInstance = null;
    }
    initMPIChart();
}

// ===== Fleet Size Calculator (Task 10) =====
function initCalculator() {
    const milesSlider = document.getElementById('calc-miles-per-day');
    const hoursSlider = document.getElementById('calc-active-hours');
    const utilSlider = document.getElementById('calc-utilization');
    const fleetSlider = document.getElementById('calc-fleet-size');

    if (!milesSlider) return;

    function updateCalculator() {
        const milesPerDay = parseInt(milesSlider.value);
        const activeHours = parseInt(hoursSlider.value);
        const utilization = parseInt(utilSlider.value);
        const fleetSize = parseInt(fleetSlider.value);

        // Update display values
        document.getElementById('calc-miles-display').textContent = milesPerDay + ' mi/day';
        document.getElementById('calc-hours-display').textContent = activeHours + ' hrs';
        document.getElementById('calc-util-display').textContent = utilization + '%';
        document.getElementById('calc-fleet-display').textContent = fleetSize + ' vehicles';

        // Calculate results
        const dailyMiles = fleetSize * milesPerDay;
        const monthlyMiles = dailyMiles * 30;
        const avgSpeed = milesPerDay / activeHours;

        // Calculate streak at these assumptions
        const currentData = getIncidentData();
        const lastIncident = currentData[currentData.length - 1];
        const lastIncidentDate = new Date(lastIncident.date);
        const today = new Date();
        const daysSince = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
        const stoppageDays = countStoppageDays(lastIncidentDate, today);
        const activeDays = daysSince - stoppageDays;
        const streakMiles = activeDays * fleetSize * milesPerDay;

        // Update DOM
        document.getElementById('calc-daily-miles').textContent = dailyMiles.toLocaleString();
        document.getElementById('calc-monthly-miles').textContent = monthlyMiles.toLocaleString();
        document.getElementById('calc-avg-speed').textContent = avgSpeed.toFixed(1) + ' mph';
        document.getElementById('calc-streak-miles').textContent = streakMiles.toLocaleString();
    }

    [milesSlider, hoursSlider, utilSlider, fleetSlider].forEach(slider => {
        slider.addEventListener('input', updateCalculator);
    });

    updateCalculator();
}

initCalculator();

// ===== Dataset Download (Task 16) =====
function generateCSV() {
    const currentData = getIncidentData();
    // Monthly aggregate format (NHTSA data has month-level resolution only)
    let csv = 'month,incident_count,avg_fleet_size,total_miles,mpi\n';
    currentData.forEach((d) => {
        const monthStr = new Date(d.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        csv += monthStr + ',' + (d.count || 1) + ',' + d.fleet + ',' + d.miles + ',' + d.mpi + '\n';
    });
    return csv;
}

function generateJSON() {
    const currentData = getIncidentData();
    // Monthly aggregate format (NHTSA data has month-level resolution only)
    const dataset = {
        metadata: {
            title: 'Tesla Robotaxi Safety Data - Monthly Aggregates',
            description: 'Monthly MPI estimates. NHTSA SGO data has month-level date resolution only, so incidents are aggregated by month.',
            source: 'NHTSA SGO 2021-01 / robotaxitracker.com',
            license: 'MIT',
            updated: new Date().toISOString().split('T')[0],
            url: 'https://robotaxi-safety-tracker.com/',
            methodology: 'https://robotaxi-safety-tracker.com/methodology.html',
            miles_per_day_assumption: 115,
            fleet_source: 'robotaxitracker.com (Austin total fleet)'
        },
        monthly_data: currentData.map((d) => ({
            month: new Date(d.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
            incident_count: d.count || 1,
            avg_fleet_size: d.fleet,
            total_miles: d.miles,
            mpi: d.mpi
        })),
        trend: {
            model: 'exponential',
            r_squared: trendParams.rSquared,
            doubling_time_days: trendParams.doublingTime,
            daily_growth_rate: trendParams.dailyGrowth,
            forecast_30day_mpi: trendParams.forecast30Day
        },
        totals: {
            total_incidents: currentData.reduce((sum, d) => sum + (d.count || 1), 0),
            total_miles: currentData.reduce((sum, d) => sum + d.miles, 0)
        }
    };
    return JSON.stringify(dataset, null, 2);
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

const csvBtn = document.getElementById('download-csv');
if (csvBtn) csvBtn.addEventListener('click', () => downloadFile(generateCSV(), 'tesla-robotaxi-incidents.csv', 'text/csv'));

const jsonBtn = document.getElementById('download-json');
if (jsonBtn) jsonBtn.addEventListener('click', () => downloadFile(generateJSON(), 'tesla-robotaxi-incidents.json', 'application/json'));

// ===== Fetch Latest Data =====
// Note: Trend parameters for the chart are computed in-browser from incidentData
// via computeExponentialFit(). The data.json (from Python analysis of raw NHTSA
// incidents) uses a different dataset and is NOT used for chart trend lines.
async function fetchLatestData() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) return;
        const data = await response.json();

        // Update stat cards with NHTSA raw-analysis metadata (not chart trend)
        const trend = data.trend_analysis || {};
        const bestFit = trend.best_fit || {};
        const bestModel = trend.best_model || null;

        const statModelEl = document.getElementById('stat-best-model');
        if (bestModel && statModelEl) {
            statModelEl.textContent = bestModel.charAt(0).toUpperCase() + bestModel.slice(1);
        }
    } catch (error) {
        console.log('Using embedded data (JSON fetch not available)');
    }
}

// Try to fetch latest data
fetchLatestData();

// ===== FAQ Accordion =====
(function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all other items
            faqItems.forEach(otherItem => {
                otherItem.classList.remove('active');
                otherItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
            });

            // Toggle current item
            if (!isActive) {
                item.classList.add('active');
                question.setAttribute('aria-expanded', 'true');
            }
        });
    });
})();

// ===== Subscribe Modal =====
(function initSubscribeModal() {
    const overlay = document.getElementById('subscribe-overlay');
    const openBtn = document.getElementById('open-subscribe');
    const closeBtn = document.getElementById('subscribe-close');
    const form = document.getElementById('subscribe-form');
    const emailInput = document.getElementById('subscribe-email');
    const submitBtn = document.getElementById('subscribe-submit');
    const successEl = document.getElementById('subscribe-success');
    const errorEl = document.getElementById('subscribe-error');
    const errorText = document.getElementById('error-text');

    if (!overlay || !openBtn) return;

    function openModal() {
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
        setTimeout(() => emailInput && emailInput.focus(), 200);
    }

    function closeModal() {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }

    function resetForm() {
        form.style.display = '';
        successEl.style.display = 'none';
        errorEl.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.querySelector('.submit-text').style.display = '';
        submitBtn.querySelector('.submit-loading').style.display = 'none';
    }

    openBtn.addEventListener('click', () => {
        resetForm();
        openModal();
    });

    closeBtn.addEventListener('click', closeModal);

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = emailInput.value.trim();
        if (!email) return;

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.querySelector('.submit-text').style.display = 'none';
        submitBtn.querySelector('.submit-loading').style.display = '';

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    _subject: 'New Subscriber - Tesla Robotaxi Safety Tracker'
                })
            });

            if (response.ok) {
                form.style.display = 'none';
                successEl.style.display = '';
                errorEl.style.display = 'none';
            } else {
                throw new Error('Submission failed');
            }
        } catch (err) {
            // Fallback: open mailto link so the subscription still works
            const mailtoUrl = 'mailto:weekly-update@robotaxi-safety-tracker.com'
                + '?subject=' + encodeURIComponent('Subscribe to Weekly Updates')
                + '&body=' + encodeURIComponent(
                    'Hi, please add me to the weekly update list.\n\nMy email: ' + email
                );
            window.location.href = mailtoUrl;

            form.style.display = 'none';
            successEl.style.display = '';
            errorEl.style.display = 'none';
        }
    });
})();

// ===== Data =====
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
// Active fleet data is preserved in fleet_growth_active.json for future use
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
    { date: '2025-12-21', size: 29 },
    { date: '2025-12-22', size: 30 },
    { date: '2025-12-23', size: 30 },
    { date: '2025-12-24', size: 30 },
    { date: '2025-12-25', size: 31 },
    { date: '2025-12-26', size: 31 },
    { date: '2025-12-27', size: 31 },
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
    { date: '2026-01-14', size: 38 },
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
    { date: '2026-01-25', size: 72 },
    { date: '2026-01-26', size: 72 },
    { date: '2026-01-27', size: 72 },
    { date: '2026-01-28', size: 72 },
    { date: '2026-01-29', size: 72 },
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

const fit = computeExponentialFit(incidentData);
const trendParams = {
    exponential: { a: fit.a, b: fit.b },
    rSquared: fit.rSquared,
    doublingTime: fit.doublingTime,
    dailyGrowth: fit.dailyGrowth,
    forecast30Day: fit.forecast30Day
};

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

            // Calculate cumulative miles since last incident (excluding stoppage days)
            const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
            const stoppageDays = countStoppageDays(lastIncidentDate, today);
            const activeDays = daysSinceLastIncident - stoppageDays;
            const currentFleetSize = fleetData[fleetData.length - 1].size; // Latest fleet size
            const cumulativeMiles = activeDays * currentFleetSize * 115; // 115 mi/day/vehicle
            ongoingProgress.push(cumulativeMiles);
        } else {
            // Today already in labels, find its index and set ongoing progress
            const todayIndex = labels.indexOf(todayStr);
            const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
            const stoppageDays = countStoppageDays(lastIncidentDate, today);
            const activeDays = daysSinceLastIncident - stoppageDays;
            const currentFleetSize = fleetData[fleetData.length - 1].size;
            const cumulativeMiles = activeDays * currentFleetSize * 115;
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
                    label: 'Exponential Trend',
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

    // Calculate miles since last incident (excluding stoppage days)
    const lastIncident = incidentData[incidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const currentFleetSize = fleetData[fleetData.length - 1].size;
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
document.querySelectorAll('a[href^="#"]:not(.share-icon)').forEach(anchor => {
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
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const currentFleetSize = fleetData[fleetData.length - 1].size;
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
    const lastIncident = incidentData[incidentData.length - 1];
    const lastIncidentDate = new Date(lastIncident.date);
    const today = new Date();
    const daysSinceLastIncident = Math.floor((today - lastIncidentDate) / (1000 * 60 * 60 * 24));
    const stoppageDays = countStoppageDays(lastIncidentDate, today);
    const activeDays = daysSinceLastIncident - stoppageDays;
    const currentFleetSize = fleetData[fleetData.length - 1].size;
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

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    initMPIChart();
    initFleetChart();
    populateIncidentTable();
    updateMetrics();
    updateHeroStreak();
    updateCurrentStreakComparison();
    animateComparisonBars();

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
    const pageUrl = 'https://kangning-huang.github.io/tesla_robotaxi_mile_per_incident_tracker/';
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

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

const fleetData = [
    { date: '2025-06-25', size: 10 },
    { date: '2025-07-15', size: 15 },
    { date: '2025-08-15', size: 20 },
    { date: '2025-09-15', size: 25 },
    { date: '2025-10-15', size: 30 },
    { date: '2025-11-15', size: 32 },
    { date: '2025-12-15', size: 33 },
    { date: '2026-01-15', size: 42 },
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
        intersect: false,
        mode: 'index'
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
            padding: 12,
            displayColors: true,
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += context.parsed.y.toLocaleString();
                    }
                    return label;
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

    // Prepare data
    const labels = incidentData.map(d => d.date);
    const mpiValues = incidentData.map(d => d.mpi);

    // Calculate exponential trend line
    const startDate = new Date(incidentData[0].date);
    const trendData = incidentData.map(d => {
        const currentDate = new Date(d.date);
        const daysSinceStart = Math.floor((currentDate - startDate) / (1000 * 60 * 60 * 24));
        return Math.round(trendParams.exponential.a * Math.exp(trendParams.exponential.b * daysSinceStart));
    });

    // Human driver benchmark
    const humanBenchmark = new Array(incidentData.length).fill(500000);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'MPI per Interval',
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
                    order: 1
                },
                {
                    label: 'Exponential Trend',
                    data: trendData,
                    borderColor: chartColors.primary,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [],
                    pointRadius: 0,
                    tension: 0.4,
                    order: 2
                },
                {
                    label: 'Human Driver Avg (500K)',
                    data: humanBenchmark,
                    borderColor: chartColors.success,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [8, 4],
                    pointRadius: 0,
                    order: 3
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                x: commonOptions.scales.x,
                y: {
                    grid: {
                        color: chartColors.grid,
                        drawBorder: false
                    },
                    min: 0,
                    max: 600000,
                    ticks: {
                        color: chartColors.muted,
                        font: { family: "'JetBrains Mono', monospace", size: 11 },
                        stepSize: 100000,
                        callback: function(value) {
                            return Math.round(value / 1000) + 'K';
                        }
                    }
                }
            },
            plugins: {
                ...commonOptions.plugins,
                annotation: {
                    annotations: {
                        humanLine: {
                            type: 'line',
                            yMin: 500000,
                            yMax: 500000,
                            borderColor: chartColors.success,
                            borderWidth: 2,
                            borderDash: [8, 4]
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
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    beginAtZero: true,
                    max: 50
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

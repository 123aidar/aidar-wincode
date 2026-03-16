/**
 * AutoService Pro — Dashboard Charts
 * Chart.js integration for analytics dashboard.
 */

const CHART_COLORS = {
    primary:    'rgba(99, 102, 241, 1)',
    primaryBg:  'rgba(99, 102, 241, 0.15)',
    green:      'rgba(16, 185, 129, 1)',
    greenBg:    'rgba(16, 185, 129, 0.15)',
    orange:     'rgba(245, 158, 11, 1)',
    orangeBg:   'rgba(245, 158, 11, 0.15)',
    red:        'rgba(239, 68, 68, 1)',
    redBg:      'rgba(239, 68, 68, 0.15)',
    cyan:       'rgba(6, 182, 212, 1)',
    cyanBg:     'rgba(6, 182, 212, 0.15)',
    purple:     'rgba(168, 85, 247, 1)',
    purpleBg:   'rgba(168, 85, 247, 0.15)',
};

const DEFAULT_OPTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } },
        title:  { display: false },
    },
    scales: {
        x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.08)' } },
        y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.08)' } },
    },
};

async function fetchJSON(url) {
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) throw new Error(`API ${url} returned ${res.status}`);
    return res.json();
}

/* ---- Revenue Line Chart ---- */
async function renderRevenueChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    try {
        const data = await fetchJSON('/api/analytics/revenue/monthly/');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Выручка',
                    data: data.values,
                    borderColor: CHART_COLORS.primary,
                    backgroundColor: CHART_COLORS.primaryBg,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }],
            },
            options: DEFAULT_OPTS,
        });
    } catch (e) {
        console.warn('Revenue chart:', e.message);
    }
}

/* ---- Services Popularity Bar Chart ---- */
async function renderServicesChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    try {
        const data = await fetchJSON('/api/analytics/services/popular/');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Заказы',
                    data: data.values,
                    backgroundColor: [
                        CHART_COLORS.primaryBg, CHART_COLORS.greenBg,
                        CHART_COLORS.orangeBg, CHART_COLORS.cyanBg,
                        CHART_COLORS.purpleBg, CHART_COLORS.redBg
                    ],
                    borderColor: [
                        CHART_COLORS.primary, CHART_COLORS.green,
                        CHART_COLORS.orange, CHART_COLORS.cyan,
                        CHART_COLORS.purple, CHART_COLORS.red
                    ],
                    borderWidth: 1.5,
                    borderRadius: 6,
                }],
            },
            options: { ...DEFAULT_OPTS, plugins: { ...DEFAULT_OPTS.plugins, legend: { display: false } } },
        });
    } catch (e) {
        console.warn('Services chart:', e.message);
    }
}

/* ---- Mechanic Workload Bar Chart ---- */
async function renderWorkloadChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    try {
        const data = await fetchJSON('/api/analytics/mechanics/workload/');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Активные заказы',
                    data: data.values,
                    backgroundColor: CHART_COLORS.cyanBg,
                    borderColor: CHART_COLORS.cyan,
                    borderWidth: 1.5,
                    borderRadius: 6,
                }],
            },
            options: {
                ...DEFAULT_OPTS,
                indexAxis: 'y',
                plugins: { ...DEFAULT_OPTS.plugins, legend: { display: false } },
            },
        });
    } catch (e) {
        console.warn('Workload chart:', e.message);
    }
}

/* ---- Order Status Doughnut Chart ---- */
async function renderStatusChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    try {
        const data = await fetchJSON('/api/analytics/orders/status/');
        const palette = [
            CHART_COLORS.orange, CHART_COLORS.cyan, CHART_COLORS.primary,
            CHART_COLORS.red, CHART_COLORS.green, CHART_COLORS.purple,
        ];
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: palette.slice(0, data.labels.length),
                    borderColor: 'rgba(15, 23, 42, 0.8)',
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', padding: 16, font: { family: 'Inter' } },
                    },
                },
            },
        });
    } catch (e) {
        console.warn('Status chart:', e.message);
    }
}

/* ---- Dashboard Initialization ---- */
function initDashboardCharts() {
    renderRevenueChart('revenueChart');
    renderServicesChart('servicesChart');
    renderWorkloadChart('workloadChart');
    renderStatusChart('statusChart');
}

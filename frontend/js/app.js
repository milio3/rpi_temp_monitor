const API_URL = '/api';

// Configuración Global
Chart.defaults.font.family = "'Outfit', sans-serif";
Chart.defaults.color = '#94a3b8';

let dailyChart, historyChart;
let fullMonthlyData = [];
let isFirstLoad = true;

const tempFormatter = new Intl.NumberFormat('es-ES', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
});

const timeFormatter = new Intl.DateTimeFormat('es-ES', {
    hour: '2-digit', minute: '2-digit', hour12: false
});

// --- Llamadas a la API ---

async function fetchLatest() {
    try {
        const res = await fetch(`${API_URL}/readings/latest`);
        if (!res.ok) throw new Error('Error de API');
        const data = await res.json();

        const now = new Date();
        const readingTime = new Date(data.timestamp);
        const diffMinutes = (now - readingTime) / 1000 / 60;

        let status = 'online';
        if (diffMinutes > 20) status = 'stale';

        renderCurrentTemp(data);
        updateStatus(status);
    } catch (e) {
        console.error(e);
        updateStatus('offline');
    }
}

async function fetchHistory() {
    try {
        const res = await fetch(`${API_URL}/readings/history?days=1`);
        const data = await res.json();
        updateDailyChart(data);
    } catch (e) { console.error(e); }
}

async function fetchLongHistory() {
    try {
        const resMonthly = await fetch(`${API_URL}/readings/stats/monthly`);
        fullMonthlyData = await resMonthly.json();
        renderMonthlyStatsPreview(fullMonthlyData);
        renderModalContent(fullMonthlyData);

        const resDaily = await fetch(`${API_URL}/readings/history?days=30`);
        const dailyRaw = await resDaily.json();
        processAndRenderHistoryChart(dailyRaw);
    } catch (e) { console.error(e); }
}

// --- Lógica de UI ---

function updateStatus(state) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');

    // Resetear clases
    dot.className = "w-2 h-2 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.3)]";
    dot.classList.remove('animate-pulse', 'bg-emerald-400', 'bg-rose-500', 'bg-amber-400', 'bg-slate-500', 'shadow-[0_0_10px_rgba(52,211,153,0.8)]', 'shadow-[0_0_10px_rgba(244,63,94,0.8)]', 'shadow-[0_0_10px_rgba(251,191,36,0.8)]');

    text.classList.remove('text-rose-400', 'text-amber-400', 'text-emerald-400', 'text-slate-400');

    if (state === 'online') {
        dot.classList.add('bg-emerald-400', 'animate-pulse', 'shadow-[0_0_10px_rgba(52,211,153,0.8)]');
        text.innerText = 'EN LÍNEA';
        text.classList.add('text-emerald-400');
    } else if (state === 'offline') {
        dot.classList.add('bg-rose-500', 'shadow-[0_0_10px_rgba(244,63,94,0.8)]');
        text.innerText = 'SIN CONEXIÓN';
        text.classList.add('text-rose-400');
    } else if (state === 'stale') {
        dot.classList.add('bg-amber-400', 'shadow-[0_0_10px_rgba(251,191,36,0.8)]');
        text.innerText = 'DATOS ANTIGUOS';
        text.classList.add('text-amber-400');
    }
}

function renderCurrentTemp(data) {
    const temp = data.temperature;

    // Arrays para escritorio y móvil si existen
    const els = [document.getElementById('currentTemp'), document.getElementById('currentTempMobile')];

    els.forEach(el => {
        if (!el) return;
        el.innerText = `${tempFormatter.format(temp)} ºC`;

        // Color dinámico según temperatura
        el.className = el.className.replace(/text-\[.*?\]/g, ''); // Limpiar colores custom previos si los hubiera
        el.style.color = ''; // Reset inline

        if (temp > 75) {
            el.style.textShadow = "0 0 30px rgba(244, 63, 94, 0.6)";
            el.classList.add('text-rose-400');
            el.classList.remove('text-white', 'text-amber-400');
        } else if (temp > 60) {
            el.style.textShadow = "0 0 30px rgba(251, 191, 36, 0.6)";
            el.classList.add('text-amber-400');
            el.classList.remove('text-white', 'text-rose-400');
        } else {
            el.style.textShadow = "0 0 30px rgba(34, 211, 238, 0.4)";
            el.classList.add('text-white');
            el.classList.remove('text-rose-400', 'text-amber-400');
        }
    });

    const date = new Date(data.timestamp);
    const timeStr = timeFormatter.format(date);

    const footerEls = [document.getElementById('lastUpdateText'), document.getElementById('lastUpdateTextMobile')];
    footerEls.forEach(el => {
        if (el) el.innerText = `Actualizado: ${timeStr}`;
    });
}

function renderMonthlyStatsPreview(data) {
    const container = document.getElementById('monthlyStatsPreview');


    if (!data.length) return;

    const recent = [...data].reverse().slice(0, 8);
    let html = '';
    let currentYear = null;

    recent.forEach((m, index) => {
        const [year, month] = m.month.split('-');

        // Separador de año
        if (currentYear !== year) {
            html += `
            <div class="flex items-center gap-2 mt-4 mb-2 opacity-60">
                <span class="text-[10px] font-bold text-indigo-200 uppercase tracking-widest">${year}</span>
                <div class="h-px bg-indigo-500/30 flex-grow"></div>
            </div>`;
            currentYear = year;
        }

        const dateObj = new Date(year, month - 1);
        let monthName = dateObj.toLocaleString('es-ES', { month: 'long' });
        monthName = monthName.charAt(0).toUpperCase() + monthName.slice(1);

        // Datos para tooltip (JSON stringified en data-attr)
        const minDate = new Date(m.min_time);
        const maxDate = new Date(m.max_time);

        const tooltipData = JSON.stringify({
            month: monthName + ' ' + year,
            min: tempFormatter.format(m.min),
            minDate: minDate.toLocaleString('es-ES'),
            max: tempFormatter.format(m.max),
            maxDate: maxDate.toLocaleString('es-ES')
        });

        html += `
        <div class="stats-row glass-card grid grid-cols-3 gap-3 px-3 py-3 items-center text-sm cursor-default group hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
             
            <div class="text-center font-bold text-indigo-100 group-hover:text-white transition-colors capitalize text-xs tracking-wide leading-none flex items-center justify-center h-full">
                ${monthName}
            </div>
            
            <div class="flex items-center justify-center font-mono font-bold text-cyan-300 bg-cyan-900/50 border border-cyan-500/30 rounded-md py-1.5 shadow-sm">
                ${tempFormatter.format(m.min)}
            </div>
            
            <div class="flex items-center justify-center font-mono font-bold text-pink-300 bg-pink-900/50 border border-pink-500/30 rounded-md py-1.5 shadow-sm">
                ${tempFormatter.format(m.max)}
            </div>
        </div>`;
    });

    container.innerHTML = html;
}




function renderModalContent(data) {
    const container = document.getElementById('modalBody');
    if (!container) return;

    const byYear = {};
    data.forEach(m => {
        const y = m.month.split('-')[0];
        if (!byYear[y]) byYear[y] = [];
        byYear[y].push(m);
    });

    const years = Object.keys(byYear).sort((a, b) => b - a);
    let html = '';
    years.forEach(year => {
        const months = byYear[year].reverse();
        html += `
        <details class="group mb-4 glass-card overflow-hidden" ${year === years[0] ? 'open' : ''}>
            <summary class="flex justify-between items-center font-bold text-lg p-4 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer text-indigo-100">
                <span>Año ${year}</span>
                <span class="transition-transform duration-300 group-open:rotate-180 text-cyan-400">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </span>
            </summary>
            <div class="p-2 space-y-1 bg-black/20">
                 ${months.map(m => createModalMonthRow(m)).join('')}
            </div>
        </details>
        `;
    });
    container.innerHTML = html;
}

function createModalMonthRow(m) {
    const [year, month] = m.month.split('-');
    const dateObj = new Date(year, month - 1);
    let monthName = dateObj.toLocaleString('es-ES', { month: 'long' });
    monthName = monthName.charAt(0).toUpperCase() + monthName.slice(1);

    const minDate = new Date(m.min_time);
    const maxDate = new Date(m.max_time);

    // Formato solicitado: Diciembre, MIN 42,01 ºC (29/12 - 06:33), MAX 57,98 ºC (03/12 - 12:33)
    const minFmt = `${tempFormatter.format(m.min)} ºC (${minDate.getDate().toString().padStart(2, '0')}/${(minDate.getMonth() + 1).toString().padStart(2, '0')} - ${timeFormatter.format(minDate)})`;
    const maxFmt = `${tempFormatter.format(m.max)} ºC (${maxDate.getDate().toString().padStart(2, '0')}/${(maxDate.getMonth() + 1).toString().padStart(2, '0')} - ${timeFormatter.format(maxDate)})`;

    return `
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center text-sm p-4 hover:bg-white/5 rounded-lg border-b border-white/5 last:border-0 transition-colors">
        <!-- Mes -->
        <div class="md:col-span-2 font-bold text-indigo-100 capitalize text-lg md:text-base">${monthName}</div>
        
        <!-- Min -->
        <div class="md:col-span-5 flex items-center gap-3 bg-cyan-950/30 px-3 py-2 rounded-lg border border-cyan-500/10">
            <span class="text-[10px] font-bold text-cyan-500 uppercase tracking-wider">Min</span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-2">
                <span class="font-mono text-cyan-100 font-bold text-base bg-transparent">${tempFormatter.format(m.min)}°</span>
                <span class="text-xs text-cyan-200/60 font-mono whitespace-nowrap">(${minDate.getDate().toString().padStart(2, '0')}/${(minDate.getMonth() + 1).toString().padStart(2, '0')} - ${timeFormatter.format(minDate)})</span>
            </div>
        </div>
        
        <!-- Max -->
        <div class="md:col-span-5 flex items-center gap-3 bg-pink-950/30 px-3 py-2 rounded-lg border border-pink-500/10">
             <span class="text-[10px] font-bold text-pink-500 uppercase tracking-wider">Max</span>
             <div class="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-2">
                 <span class="font-mono text-pink-100 font-bold text-base bg-transparent">${tempFormatter.format(m.max)}°</span>
                 <span class="text-xs text-pink-200/60 font-mono whitespace-nowrap">(${maxDate.getDate().toString().padStart(2, '0')}/${(maxDate.getMonth() + 1).toString().padStart(2, '0')} - ${timeFormatter.format(maxDate)})</span>
            </div>
        </div>
    </div>`;
}

window.openModal = () => document.getElementById('historyModal')?.classList.add('active');
window.closeModal = () => document.getElementById('historyModal')?.classList.remove('active');

// --- Gráficos ---

function initDailyChart() {
    const ctx = document.getElementById('dailyChart').getContext('2d');

    // Gradiente para el gráfico diario
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(249, 115, 22, 0.2)'); // Naranja 500 apagado
    gradient.addColorStop(1, 'rgba(249, 115, 22, 0.0)');

    dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Temperatura',
                data: [],
                borderColor: '#f97316', // Naranja 500
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 5,
                pointBackgroundColor: '#f97316',
                pointHitRadius: 20
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#020617',
                    padding: 10,
                    cornerRadius: 8,
                    borderColor: 'rgba(148, 163, 184, 0.1)',
                    borderWidth: 1,
                    titleFont: { family: "'Outfit', sans-serif", size: 13 },
                    bodyFont: { family: 'monospace', size: 13, weight: 'bold' },
                    titleColor: '#cbd5e1',
                    bodyColor: '#e2e8f0',
                    displayColors: false,
                    callbacks: {
                        title: (c) => {
                            const date = new Date(c[0].parsed.x);
                            return new Intl.DateTimeFormat('es-ES', {
                                day: '2-digit', month: '2-digit', year: 'numeric'
                            }).format(date);
                        },
                        label: (c) => {
                            const date = new Date(c.parsed.x);
                            const timeStr = new Intl.DateTimeFormat('es-ES', {
                                hour: '2-digit', minute: '2-digit', hour12: false
                            }).format(date);
                            return `Temp. ${tempFormatter.format(c.parsed.y)} ºC (${timeStr})`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: { unit: 'hour', displayFormats: { hour: 'HH:mm' }, tooltipFormat: 'dd/MM HH:mm' },
                    grid: { display: false },
                    offset: true,
                    ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 6, font: { size: 13 }, color: '#cbd5e1' }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    border: { display: false },
                    ticks: { font: { size: 12 }, color: '#cbd5e1' }
                }
            }
        }
    });
}

function updateDailyChart(data) {
    if (!dailyChart) return;

    data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const points = data.map(d => ({ x: d.timestamp, y: d.temperature }));
    dailyChart.data.datasets[0].data = points;

    if (isFirstLoad) {
        dailyChart.update();
        isFirstLoad = false;
    } else {
        dailyChart.update('none');
    }
}

function initHistoryChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Máx', data: [],
                    borderColor: '#fb7185', // Rosa 400
                    backgroundColor: 'rgba(251, 113, 133, 0.1)',
                    fill: false, tension: 0.4, pointRadius: 2, pointHoverRadius: 5, borderWidth: 2, pointBackgroundColor: '#fb7185'
                },
                {
                    label: 'Mín', data: [],
                    borderColor: '#38bdf8', // Cielo 400
                    backgroundColor: 'rgba(56, 189, 248, 0.05)',
                    fill: '-1', tension: 0.4, pointRadius: 2, pointHoverRadius: 5, borderWidth: 2, pointBackgroundColor: '#38bdf8'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#020617',
                    padding: 10,
                    cornerRadius: 8,
                    borderColor: 'rgba(148, 163, 184, 0.1)',
                    borderWidth: 1,
                    titleFont: { family: "'Outfit', sans-serif", size: 13 },
                    bodyFont: { family: 'monospace', size: 13, weight: 'bold' },
                    titleColor: '#cbd5e1',
                    bodyColor: '#e2e8f0',
                    displayColors: false,
                    callbacks: {
                        title: (c) => {
                            const dateStr = c[0].raw.fullDate;
                            if (dateStr) {
                                const [y, m, d] = dateStr.split('-');
                                return `${d}/${m}/${y}`;
                            }
                            return c[0].label;
                        },
                        label: function (context) {
                            const raw = context.raw;
                            return `${context.dataset.label}: ${tempFormatter.format(raw.y)} °C (${raw.t})`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    grid: { display: false },
                    offset: true,
                    ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 7, font: { size: 13 }, color: '#cbd5e1' }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    border: { display: false },
                    ticks: { font: { size: 12 }, color: '#cbd5e1' }
                }
            }
        }
    });
}

function processAndRenderHistoryChart(dailyRaw) {
    if (!historyChart) return;

    const grouped = {};
    dailyRaw.forEach(r => {
        const day = r.timestamp.split('T')[0];
        const val = r.temperature;
        const timeStr = r.timestamp.split('T')[1].substring(0, 5);

        if (!grouped[day]) {
            grouped[day] = { min: val, minTime: timeStr, max: val, maxTime: timeStr, date: day };
        } else {
            if (val < grouped[day].min) { grouped[day].min = val; grouped[day].minTime = timeStr; }
            if (val > grouped[day].max) { grouped[day].max = val; grouped[day].maxTime = timeStr; }
        }
    });

    const sortedDays = Object.values(grouped).sort((a, b) => a.date.localeCompare(b.date));
    const recentDays = sortedDays.slice(-15);

    // Etiquetas visuales (DD Mes)
    const visualLabels = recentDays.map(d => {
        const parts = d.date.split('-'); // YYYY-MM-DD
        const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
        const monthShort = dateObj.toLocaleString('es-ES', { month: 'short' });
        return `${parts[2]} ${monthShort}`;
    });

    historyChart.data.labels = visualLabels;

    historyChart.data.datasets[0].data = recentDays.map((d, i) => ({
        x: visualLabels[i], y: d.max, t: d.maxTime, fullDate: d.date
    }));
    historyChart.data.datasets[1].data = recentDays.map((d, i) => ({
        x: visualLabels[i], y: d.min, t: d.minTime, fullDate: d.date
    }));

    historyChart.update();
}

document.addEventListener('DOMContentLoaded', () => {
    initDailyChart();
    initHistoryChart();

    fetchLatest();
    fetchHistory();
    fetchLongHistory();

    setInterval(() => {
        fetchLatest();
        fetchHistory();
    }, 60000);
});

/**
 * Gestor de Gráficas para Dashboard Térmico RPi
 * Cumple directrices de contraste y escala ergonómica para monitores QHD.
 */

let dailyChart = null;
let historyChart = null;

const numberFormat = new Intl.NumberFormat('es-ES', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 2,
});

const timeFormat = new Intl.DateTimeFormat('es-ES', {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
});

const dateFormat = new Intl.DateTimeFormat('es-ES', {
  day: '2-digit',
  month: '2-digit',
});

async function loadDailyChart() {
  const canvas = document.getElementById('dailyChart');
  if (!canvas) return;

  try {
    const response = await fetch('/api/v1/readings/history?days=1');
    if (!response.ok) return;
    const data = await response.json();

    const labels = data.map(d => {
      const dt = new Date(d.timestamp);
      return timeFormat.format(dt);
    });
    const values = data.map(d => d.temperature);

    const ctx = canvas.getContext('2d');

    // Gradiente suave para el fondo del gráfico
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(138, 180, 248, 0.25)');
    gradient.addColorStop(1, 'rgba(138, 180, 248, 0.0)');

    if (dailyChart) {
      dailyChart.data.labels = labels;
      dailyChart.data.datasets[0].data = values;
      dailyChart.update('none');
      return;
    }

    dailyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Temperatura (°C)',
          data: values,
          borderColor: '#8AB4F8',
          backgroundColor: gradient,
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: values.length > 50 ? 0 : 3,
          pointHoverRadius: 6,
          pointBackgroundColor: '#8AB4F8',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: '#20252C',
            titleColor: '#F0F2F5',
            bodyColor: '#C4CBD4',
            borderColor: '#414B58',
            borderWidth: 1,
            padding: 12,
            bodyFont: { size: 15, family: 'Inter, sans-serif' },
            titleFont: { size: 15, weight: '600', family: 'Inter, sans-serif' },
            callbacks: {
              label: function(context) {
                return ` ${numberFormat.format(context.parsed.y)} °C`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(65, 75, 88, 0.3)',
              drawBorder: false,
            },
            ticks: {
              color: '#ADB6C2',
              font: { size: 13, family: 'Inter, sans-serif' },
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 12,
            }
          },
          y: {
            grid: {
              color: 'rgba(65, 75, 88, 0.3)',
              drawBorder: false,
            },
            ticks: {
              color: '#ADB6C2',
              font: { size: 13, family: 'Inter, sans-serif' },
              callback: function(val) {
                return `${val} °C`;
              }
            }
          }
        }
      }
    });
  } catch (error) {
    console.error('Error cargando gráfico de 24h:', error);
  }
}

async function loadHistoryChart() {
  const canvas = document.getElementById('historyChart');
  if (!canvas) return;

  try {
    const response = await fetch('/api/v1/readings/history?days=30');
    if (!response.ok) return;
    const data = await response.json();

    // Reducir la muestra a medias por intervalos para 30 días si hay muchos puntos
    const labels = [];
    const values = [];

    // Muestreo simplificado
    const step = Math.max(1, Math.floor(data.length / 100));
    for (let i = 0; i < data.length; i += step) {
      const item = data[i];
      const dt = new Date(item.timestamp);
      labels.push(`${dateFormat.format(dt)} ${timeFormat.format(dt).substring(0, 5)}`);
      values.push(item.temperature);
    }

    const ctx = canvas.getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(125, 217, 165, 0.25)');
    gradient.addColorStop(1, 'rgba(125, 217, 165, 0.0)');

    if (historyChart) {
      historyChart.data.labels = labels;
      historyChart.data.datasets[0].data = values;
      historyChart.update('none');
      return;
    }

    historyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Tendencia 30 Días (°C)',
          data: values,
          borderColor: '#7DD9A5',
          backgroundColor: gradient,
          fill: true,
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointBackgroundColor: '#7DD9A5',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: '#20252C',
            titleColor: '#F0F2F5',
            bodyColor: '#C4CBD4',
            borderColor: '#414B58',
            borderWidth: 1,
            padding: 12,
            bodyFont: { size: 15, family: 'Inter, sans-serif' },
            titleFont: { size: 15, weight: '600', family: 'Inter, sans-serif' },
            callbacks: {
              label: function(context) {
                return ` ${numberFormat.format(context.parsed.y)} °C`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(65, 75, 88, 0.3)',
              drawBorder: false,
            },
            ticks: {
              color: '#ADB6C2',
              font: { size: 13, family: 'Inter, sans-serif' },
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 8,
            }
          },
          y: {
            grid: {
              color: 'rgba(65, 75, 88, 0.3)',
              drawBorder: false,
            },
            ticks: {
              color: '#ADB6C2',
              font: { size: 13, family: 'Inter, sans-serif' },
              callback: function(val) {
                return `${val} °C`;
              }
            }
          }
        }
      }
    });
  } catch (error) {
    console.error('Error cargando gráfico histórico:', error);
  }
}

function refreshAllCharts() {
  loadDailyChart();
  loadHistoryChart();
}

// Inicialización automática
document.addEventListener('DOMContentLoaded', () => {
  refreshAllCharts();
  // Refresco periódico de gráficos cada 60 segundos
  setInterval(refreshAllCharts, 60000);
});

// Refrescar al recibir evento HTMX de actualización
document.body.addEventListener('chartsRefresh', refreshAllCharts);

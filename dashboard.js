async function loadDashboard() {
  const resp = await fetch('/data');
  if (!resp.ok) {
    document.body.innerHTML = '<p class="error">Unable to load analytics data.</p>';
    return;
  }

  const data = await resp.json();
  document.getElementById('total-crashes').textContent = data.totalCrashes.toLocaleString();
  document.getElementById('total-injured').textContent = data.totalInjured.toLocaleString();
  document.getElementById('total-killed').textContent = data.totalKilled.toLocaleString();
  document.getElementById('top-borough').textContent = data.topBorough || 'N/A';
  document.getElementById('top-factor').textContent = data.topFactor || 'N/A';

  createChart('monthlyChart', {
    labels: data.monthlySummary.map((row) => row.month),
    datasets: [
      {
        label: 'Crashes',
        data: data.monthlySummary.map((row) => row.crashes),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.16)',
        fill: true,
        tension: 0.28,
        pointRadius: 2,
      },
      {
        label: 'Injured',
        data: data.monthlySummary.map((row) => row.injured),
        borderColor: '#16a34a',
        backgroundColor: 'rgba(22, 163, 74, 0.16)',
        fill: true,
        tension: 0.28,
        pointRadius: 2,
      },
    ],
  });

  createChart('boroughChart', {
    labels: data.boroughSummary.map((row) => row.borough),
    datasets: [
      {
        label: 'Crashes',
        data: data.boroughSummary.map((row) => row.crashes),
        backgroundColor: ['#2563eb', '#ea580c', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899'],
      },
    ],
  }, 'bar');

  createChart('factorChart', {
    labels: data.topFactors.map((row) => row.factor),
    datasets: [
      {
        label: 'Occurrences',
        data: data.topFactors.map((row) => row.count),
        backgroundColor: '#0ea5e9',
      },
    ],
  }, 'bar');

  createChart('vehicleChart', {
    labels: data.topVehicles.map((row) => row.vehicle),
    datasets: [
      {
        label: 'Count',
        data: data.topVehicles.map((row) => row.count),
        backgroundColor: '#ec4899',
      },
    ],
  }, 'bar');

  renderBoroughTable(data.boroughSummary);
}

function createChart(canvasId, chartData, type = 'line') {
  const ctx = document.getElementById(canvasId).getContext('2d');
  new Chart(ctx, {
    type,
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: { mode: 'index', intersect: false },
      },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true },
      },
    },
  });
}

function renderBoroughTable(rows) {
  const container = document.getElementById('borough-table');
  const table = document.createElement('table');
  table.innerHTML = `
    <thead>
      <tr>
        <th>Borough</th>
        <th>Crashes</th>
        <th>Injured</th>
        <th>Killed</th>
      </tr>
    </thead>
    <tbody>
      ${rows
        .map(
          (row) => `
        <tr>
          <td>${row.borough}</td>
          <td>${row.crashes.toLocaleString()}</td>
          <td>${row.injured.toLocaleString()}</td>
          <td>${row.killed.toLocaleString()}</td>
        </tr>`
        )
        .join('')}
    </tbody>
  `;
  container.appendChild(table);
}

window.addEventListener('DOMContentLoaded', loadDashboard);

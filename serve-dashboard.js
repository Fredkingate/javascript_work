const http = require('http');
const fs = require('fs');
const path = require('path');

const PUBLIC_DIR = __dirname;
const CSV_PATH = process.env.CSV_PATH || '/Users/melvinlouisbowersiii/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv.download/Motor_Vehicle_Collisions_-_Crashes.csv';
const CONTENT_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
};

function parseCsv(text) {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const headers = splitLine(lines.shift() || '');
  return lines
    .filter((line) => line.trim().length > 0)
    .map((line) => {
      const values = splitLine(line);
      return headers.reduce((row, header, index) => {
        row[header] = values[index] || '';
        return row;
      }, {});
    });
}

function splitLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (inQuotes) {
      if (char === '"') {
        if (line[i + 1] === '"') {
          current += '"';
          i += 1;
        } else {
          inQuotes = false;
        }
      } else {
        current += char;
      }
    } else if (char === '"') {
      inQuotes = true;
    } else if (char === ',') {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }

  result.push(current);
  return result;
}

function parseNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function monthKey(dateText) {
  const [month, day, year] = dateText.split('/').map((part) => part.padStart(2, '0'));
  if (!year || !month) return 'Unknown';
  return `${year}-${month}`;
}

function getDayOfWeek(dateText) {
  const [month, day, year] = dateText.split('/').map(Number);
  if (!month || !day || !year) return 'Unknown';
  return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][new Date(year, month - 1, day).getDay()];
}

function aggregate(records) {
  const metrics = {
    totalCrashes: 0,
    totalInjured: 0,
    totalKilled: 0,
    borough: new Map(),
    months: new Map(),
    factors: new Map(),
    vehicles: new Map(),
  };

  records.forEach((record) => {
    metrics.totalCrashes += 1;
    metrics.totalInjured += parseNumber(record['NUMBER OF PERSONS INJURED']);
    metrics.totalKilled += parseNumber(record['NUMBER OF PERSONS KILLED']);

    const borough = record['BOROUGH'] || 'Unknown';
    const boroughEntry = metrics.borough.get(borough) || { crashes: 0, injured: 0, killed: 0 };
    boroughEntry.crashes += 1;
    boroughEntry.injured += parseNumber(record['NUMBER OF PERSONS INJURED']);
    boroughEntry.killed += parseNumber(record['NUMBER OF PERSONS KILLED']);
    metrics.borough.set(borough, boroughEntry);

    const month = monthKey(record['CRASH DATE']);
    const monthEntry = metrics.months.get(month) || { crashes: 0, injured: 0, killed: 0 };
    monthEntry.crashes += 1;
    monthEntry.injured += parseNumber(record['NUMBER OF PERSONS INJURED']);
    monthEntry.killed += parseNumber(record['NUMBER OF PERSONS KILLED']);
    metrics.months.set(month, monthEntry);

    ['CONTRIBUTING FACTOR VEHICLE 1', 'CONTRIBUTING FACTOR VEHICLE 2', 'CONTRIBUTING FACTOR VEHICLE 3', 'CONTRIBUTING FACTOR VEHICLE 4', 'CONTRIBUTING FACTOR VEHICLE 5'].forEach((key) => {
      const factor = record[key] && record[key].trim();
      if (factor && factor !== 'Unspecified' && factor !== 'Unreported') {
        metrics.factors.set(factor, (metrics.factors.get(factor) || 0) + 1);
      }
    });

    ['VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3', 'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5'].forEach((key) => {
      const vehicle = record[key] && record[key].trim();
      if (vehicle) {
        metrics.vehicles.set(vehicle, (metrics.vehicles.get(vehicle) || 0) + 1);
      }
    });
  });

  const boroughSummary = Array.from(metrics.borough.entries())
    .map(([borough, item]) => ({ borough, ...item }))
    .sort((a, b) => b.crashes - a.crashes);

  const monthlySummary = Array.from(metrics.months.entries())
    .map(([month, item]) => ({ month, ...item }))
    .sort((a, b) => (a.month > b.month ? 1 : -1));

  const topFactors = Array.from(metrics.factors.entries())
    .map(([factor, count]) => ({ factor, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const topVehicles = Array.from(metrics.vehicles.entries())
    .map(([vehicle, count]) => ({ vehicle, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  return {
    totalCrashes: metrics.totalCrashes,
    totalInjured: metrics.totalInjured,
    totalKilled: metrics.totalKilled,
    topBorough: boroughSummary[0]?.borough || 'Unknown',
    topFactor: topFactors[0]?.factor || 'Unknown',
    boroughSummary,
    monthlySummary,
    topFactors,
    topVehicles,
  };
}

function serveStatic(req, res) {
  const filePath = req.url === '/' ? path.join(PUBLIC_DIR, 'dashboard.html') : path.join(PUBLIC_DIR, decodeURIComponent(req.url));
  const ext = path.extname(filePath);
  const type = CONTENT_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': type });
    res.end(content);
  });
}

const server = http.createServer((req, res) => {
  if (req.url === '/data') {
    fs.readFile(CSV_PATH, 'utf8', (err, raw) => {
      if (err) {
        res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ error: 'Unable to read CSV file', message: err.message }));
        return;
      }
      const records = parseCsv(raw);
      const analytics = aggregate(records);
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(analytics));
    });
  } else {
    serveStatic(req, res);
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Dashboard server running: http://localhost:${PORT}`);
  console.log(`Loading CSV from: ${CSV_PATH}`);
});

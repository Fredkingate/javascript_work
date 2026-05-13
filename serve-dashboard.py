#!/usr/bin/env python3
import csv
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PUBLIC_DIR = Path(__file__).resolve().parent
CSV_PATH = Path(os.environ.get(
    'CSV_PATH',
    '/Users/melvinlouisbowersiii/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv.download/Motor_Vehicle_Collisions_-_Crashes.csv',
))

CONTRIBUTING_FACTORS = [
    'CONTRIBUTING FACTOR VEHICLE 1',
    'CONTRIBUTING FACTOR VEHICLE 2',
    'CONTRIBUTING FACTOR VEHICLE 3',
    'CONTRIBUTING FACTOR VEHICLE 4',
    'CONTRIBUTING FACTOR VEHICLE 5',
]
VEHICLE_TYPES = [
    'VEHICLE TYPE CODE 1',
    'VEHICLE TYPE CODE 2',
    'VEHICLE TYPE CODE 3',
    'VEHICLE TYPE CODE 4',
    'VEHICLE TYPE CODE 5',
]


def parse_csv(path):
    with path.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader if any(value.strip() for value in row.values())]


def month_key(date_text):
    parts = date_text.split('/')
    if len(parts) != 3:
        return 'Unknown'
    month, day, year = [part.zfill(2) for part in parts]
    return f'{year}-{month}'


def parse_number(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def aggregate(records):
    metrics = {
        'totalCrashes': 0,
        'totalInjured': 0,
        'totalKilled': 0,
        'borough': {},
        'months': {},
        'factors': {},
        'vehicles': {},
    }

    for record in records:
        metrics['totalCrashes'] += 1
        injured = parse_number(record.get('NUMBER OF PERSONS INJURED', '0'))
        killed = parse_number(record.get('NUMBER OF PERSONS KILLED', '0'))
        metrics['totalInjured'] += injured
        metrics['totalKilled'] += killed

        borough = (record.get('BOROUGH') or 'Unknown').strip() or 'Unknown'
        borough_item = metrics['borough'].setdefault(borough, {'crashes': 0, 'injured': 0, 'killed': 0})
        borough_item['crashes'] += 1
        borough_item['injured'] += injured
        borough_item['killed'] += killed

        month = month_key(record.get('CRASH DATE', ''))
        month_item = metrics['months'].setdefault(month, {'crashes': 0, 'injured': 0, 'killed': 0})
        month_item['crashes'] += 1
        month_item['injured'] += injured
        month_item['killed'] += killed

        for key in CONTRIBUTING_FACTORS:
            factor = (record.get(key) or '').strip()
            if factor and factor not in ('Unspecified', 'Unreported'):
                metrics['factors'][factor] = metrics['factors'].get(factor, 0) + 1

        for key in VEHICLE_TYPES:
            vehicle = (record.get(key) or '').strip()
            if vehicle:
                metrics['vehicles'][vehicle] = metrics['vehicles'].get(vehicle, 0) + 1

    borough_summary = sorted(
        [{'borough': borough, **values} for borough, values in metrics['borough'].items()],
        key=lambda item: item['crashes'],
        reverse=True,
    )
    monthly_summary = sorted(
        [{'month': month, **values} for month, values in metrics['months'].items()],
        key=lambda item: item['month'],
    )
    top_factors = sorted(
        [{'factor': factor, 'count': count} for factor, count in metrics['factors'].items()],
        key=lambda item: item['count'],
        reverse=True,
    )[:10]
    top_vehicles = sorted(
        [{'vehicle': vehicle, 'count': count} for vehicle, count in metrics['vehicles'].items()],
        key=lambda item: item['count'],
        reverse=True,
    )[:10]

    return {
        'totalCrashes': metrics['totalCrashes'],
        'totalInjured': metrics['totalInjured'],
        'totalKilled': metrics['totalKilled'],
        'topBorough': borough_summary[0]['borough'] if borough_summary else 'Unknown',
        'topFactor': top_factors[0]['factor'] if top_factors else 'Unknown',
        'boroughSummary': borough_summary,
        'monthlySummary': monthly_summary,
        'topFactors': top_factors,
        'topVehicles': top_vehicles,
    }


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_GET(self):
        if self.path == '/data':
            try:
                records = parse_csv(CSV_PATH)
                analytics = aggregate(records)
                payload = json.dumps(analytics).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except Exception as exc:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(exc)}).encode('utf-8'))
        else:
            super().do_GET()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '3000'))
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f'Dashboard server running at http://localhost:{port}')
    print(f'Loading CSV from: {CSV_PATH}')
    server.serve_forever()

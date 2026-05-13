#!/usr/bin/env python3
import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

DEFAULT_CSV = Path(
    '/Users/melvinlouisbowersiii/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv'
)

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


def parse_args():
    parser = argparse.ArgumentParser(description='Graph Motor Vehicle Collisions CSV data.')
    parser.add_argument(
        '--csv',
        type=Path,
        default=DEFAULT_CSV,
        help='Path to Motor_Vehicle_Collisions_-_Crashes.csv',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('collision_graphs.png'),
        help='Output image file for the generated graphs',
    )
    return parser.parse_args()


def load_rows(csv_path):
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader if any(value.strip() for value in row.values())]


def month_label(csv_date):
    try:
        return datetime.strptime(csv_date, '%m/%d/%Y').strftime('%Y-%m')
    except ValueError:
        return 'Unknown'


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def aggregate(rows):
    monthly_crashes = Counter()
    monthly_injured = Counter()
    borough_counts = Counter()
    factor_counts = Counter()
    vehicle_counts = Counter()

    for row in rows:
        month = month_label(row.get('CRASH DATE', ''))
        if month != 'Unknown':
            monthly_crashes[month] += 1
            monthly_injured[month] += parse_int(row.get('NUMBER OF PERSONS INJURED', '0'))

        borough = (row.get('BOROUGH') or 'Unknown').strip() or 'Unknown'
        borough_counts[borough] += 1

        for factor_col in CONTRIBUTING_FACTORS:
            factor = (row.get(factor_col) or '').strip()
            if factor and factor not in ('Unspecified', 'Unreported'):
                factor_counts[factor] += 1

        for vehicle_col in VEHICLE_TYPES:
            vehicle = (row.get(vehicle_col) or '').strip()
            if vehicle:
                vehicle_counts[vehicle] += 1

    return {
        'months': sorted(monthly_crashes),
        'monthly_crashes': [monthly_crashes[m] for m in sorted(monthly_crashes)],
        'monthly_injured': [monthly_injured[m] for m in sorted(monthly_injured)],
        'borough_counts': borough_counts.most_common(8),
        'top_factors': factor_counts.most_common(10),
        'top_vehicles': vehicle_counts.most_common(10),
    }


def render_graphs(data, output_path):
    plt.rcParams.update({'font.size': 10, 'figure.facecolor': '#ffffff'})
    fig, axes = plt.subplots(2, 2, figsize=(18, 12), constrained_layout=True)

    # Monthly crashes
    axes[0, 0].plot(data['months'], data['monthly_crashes'], marker='o', color='#1f77b4')
    axes[0, 0].set_title('Monthly Crashes')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Crash Count')
    axes[0, 0].tick_params(axis='x', rotation=45)

    # Monthly injured
    axes[0, 1].plot(data['months'], data['monthly_injured'], marker='o', color='#ff7f0e')
    axes[0, 1].set_title('Monthly Injuries')
    axes[0, 1].set_xlabel('Month')
    axes[0, 1].set_ylabel('Number Injured')
    axes[0, 1].tick_params(axis='x', rotation=45)

    # Borough counts
    boroughs, borough_values = zip(*data['borough_counts']) if data['borough_counts'] else ([], [])
    axes[1, 0].barh(boroughs[::-1], borough_values[::-1], color='#2ca02c')
    axes[1, 0].set_title('Top Boroughs by Crash Count')
    axes[1, 0].set_xlabel('Crash Count')

    # Top factors
    factors, factor_values = zip(*data['top_factors']) if data['top_factors'] else ([], [])
    axes[1, 1].barh(factors[::-1], factor_values[::-1], color='#d62728')
    axes[1, 1].set_title('Top Contributing Factors')
    axes[1, 1].set_xlabel('Occurrences')

    fig.suptitle('Motor Vehicle Collision Analytics', fontsize=18, y=1.02)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    args = parse_args()
    rows = load_rows(args.csv)
    data = aggregate(rows)
    render_graphs(data, args.output)
    print(f'Generated graph image: {args.output.resolve()}')

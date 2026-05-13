# NYC Motor Vehicle Collisions Dashboard

This dashboard reads `Motor_Vehicle_Collisions_-_Crashes.csv` and exposes analytics in a web UI.

## Files
- `dashboard.html` — dashboard front end
- `dashboard.js` — front-end chart and table logic
- `styles.css` — dashboard styling
- `serve-dashboard.js` — simple Node server that reads the CSV and serves data
- `serve-dashboard.py` — Python fallback server using built-in modules

## Run locally
1. Open a terminal in `javascript_work`.
2. Run one of the server options:

### Node
```bash
node serve-dashboard.js
```

### Python
```bash
python3 serve-dashboard.py
```

If the CSV path differs, set `CSV_PATH` first.

### Node with custom CSV path
```bash
CSV_PATH="/Users/yourname/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv.download/Motor_Vehicle_Collisions_-_Crashes.csv" node serve-dashboard.js
```

### Python with custom CSV path
```bash
CSV_PATH="/Users/yourname/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv" python3 serve-dashboard.py
```

### Generate graphs directly
```bash
python3 graph_collisions.py
```

Or with a custom CSV path:
```bash
python3 graph_collisions.py --csv "/Users/yourname/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv"
```

3. Open `http://localhost:3000`.

You can also access the generated graph image directly at:

```bash
http://localhost:3000/collision_graphs.png
```

## Notes
- No external packages are required for Python.
- The server uses the CSV file path from `CSV_PATH` or the default path hard-coded in the server script.

#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo " Giovanna Rupture Monitor — Container Start"
echo "============================================"

# Stage 1: Run the ETL pipeline (generates data/rupture_report.csv)
echo ""
echo "[entrypoint] Running pipeline (python main.py --local)..."
python main.py --local

# Stage 2: Verify CSV exists
CSV_PATH="data/rupture_report.csv"
if [ ! -f "$CSV_PATH" ]; then
    echo "[entrypoint] ERROR: $CSV_PATH not found after pipeline run."
    exit 1
fi
ROWS=$(wc -l < "$CSV_PATH")
echo "[entrypoint] CSV ready: $CSV_PATH ($ROWS lines)"

# Stage 3: Serve dashboard + data on port 8000
echo ""
echo "[entrypoint] Starting HTTP server on port 8000..."
echo "[entrypoint] Dashboard: http://localhost:8000/dashboard.html"
echo ""
cd /app
exec python -m http.server 8000

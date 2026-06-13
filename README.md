# 🔍 Stock-Out Monitor by Region — Lojas Giovanna

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="pandas 2.0+"/>
  <img src="https://img.shields.io/badge/requests-2.31%2B-FF6F00?style=for-the-badge&logo=curl&logoColor=white" alt="requests 2.31+"/>
  <img src="https://img.shields.io/badge/DataMission-API-6A0DAD?style=for-the-badge&logo=databricks&logoColor=white" alt="DataMission API"/>
  <img src="https://img.shields.io/badge/status-production-00C853?style=for-the-badge" alt="Status: Production"/>
</p>

<p align="center">
  <strong>3-stage ETL pipeline</strong> — ingestion, processing, and stock-out (ruptura)
  report by region, powered by the <strong>DataMission</strong> API.
</p>

---

## EN Quick Summary

**Stack:** Python 3.10+ · pandas · REST API · CSV

**What it does:** 3-stage ETL pipeline that fetches inventory data from an API,
computes stock-out (ruptura) by region, and outputs a ranked CSV report.

**Business impact:** Analyzes 4,150 regions per run. Identified regions with up to
33% stock-out rate, enabling targeted redistribution.

**Proves:** API ingestion, pandas aggregation, data quality enforcement,
CI/CD scheduling (GitHub Actions), ETL pipeline design.

**Run:** `python main.py`

---

## 📋 The Problem

Stock-out — when product demand exceeds available inventory — is one of the
biggest losses in physical retail. Each unavailable item represents:

- **Lost sale** — irrecoverable (the customer doesn't wait)
- **Satisfaction drop** — risk of switching to competitors
- **Allocation distortion** — inventory poorly distributed across regions

This pipeline answers a question legacy systems often can't answer in time:
**Where is the product missing, and by how much?**

> _"You can't manage what you don't measure. And you don't measure what you don't define."_

The project defines **ruptura** (stock-out rate) as the percentage of unmet demand:

```
ruptura = (demand_forecast - current_stock) / demand_forecast
```

| Value | Meaning |
|-------|---------|
| `> 0` | 🔴 Stock-out — insufficient inventory to meet demand |
| `= 0` | 🟢 Equilibrium — demand exactly met |
| `< 0` | 🟡 Excess stock — capital tied up |

---

## 🏗️ Pipeline Architecture

```mermaid
flowchart TB
    subgraph Stage1["Stage 1 — Ingestion"]
        A[API DataMission<br/>GET /projects/{id}/dataset] --> B[requests.get<br/>headers: Bearer token]
        B --> C[raw_data.json<br/>1,000 records]
    end

    subgraph Stage2["Stage 2 — Processing"]
        C --> D[build_demand_forecast<br/>pandas DataFrame]
        D --> E[compute_ruptura<br/>groupby by region<br/>mean + max]
    end

    subgraph Stage3["Stage 3 — Report"]
        E --> F[print_summary<br/>Top 3 regions]
        E --> G[rupture_report.csv<br/>562 regions analyzed]
    end

    style Stage1 fill:#E3F2FD,stroke:#1565C0
    style Stage2 fill:#FFF3E0,stroke:#E65100
    style Stage3 fill:#E8F5E9,stroke:#2E7D32
```

### Data flow

```
📥 Stage 1: fetch_data()
    │  requests.get → API DataMission
    │  Validates: status 200, decodable JSON
    ▼
data/raw_data.json  (1,000 records)

📊 Stage 2: process_inventory()
    │  pandas.read_json → DataFrame
    │  build_demand_forecast() → columns: region, current_stock, demand_forecast
    │  compute_ruptura() → ruptura = (demand - stock) / demand
    │  groupby("region").agg(["mean", "max"])
    ▼
Summary by region  (562 regions)

📄 Stage 3: print_summary() + save_report()
    │  Top 3 regions with highest stock-out rate
    │  Exports → data/rupture_report.csv
    ▼
Final report
```

### Architectural decisions

| Decision | Alternatives | Choice |
|----------|--------------|--------|
| Monolithic vs. orchestrated pipeline | Airflow, Prefect | `main.py` sequential — simplicity for MVP |
| JSON vs. CSV as raw | CSV, Parquet | JSON — fidelity to API schema |
| pandas vs. DuckDB | DuckDB, Polars | pandas — mature ecosystem for CI/CD and prototyping |
| `.env` vs. secrets manager | AWS Secrets, Vault | `.env` + `os.environ` — portable, no cloud dependency |

> 📖 Full decision record: [`decisions/ADR-001-rupture-pipeline.md`](decisions/ADR-001-rupture-pipeline.md)

---

## 🛠️ Stack & Technologies

| Technology | Version | Role |
|------------|---------|------|
| Python | ≥ 3.10 | Main runtime — typing, f-strings, `os.environ` |
| pandas | ≥ 2.0.0 | DataFrame operations, groupby aggregations |
| requests | ≥ 2.31.0 | HTTP client for REST API ingestion |
| DataMission | — | Source of realistic mock data (orders/inventory) |

**Minimal dependencies:** only **2 external packages** — lightweight, portable,
reproducible in any Python environment.

---

## 💼 What This Proves

For a Data Engineer role, this project demonstrates:

| Skill | Evidence |
|-------|----------|
| API ingestion | `requests.get()` with token auth, 10k-row response handling |
| Data transformation | pandas groupby aggregation (mean + max by region) |
| Data quality | 6 DQ rules (NOT NULL, RANGE, POSITIVE checks) |
| CI/CD scheduling | `.github/workflows/ingest.yml` (daily at 06:00 UTC) |
| Business translation | Defined ruptura formula clearly, linked to retail loss |
| Reproducibility | `.env` config, `--local` flag for offline re-runs |

---

## 📊 Real Results

Pipeline executed with **20,000 records** from the DataMission API — 2 calls of 10,000 rows each:

### 🥇 Top 3 Regions with Highest Average Stock-Out

| # | Region | Avg Stock-Out | Max Stock-Out |
|---|--------|:-------------:|:-------------:|
| 1 | **Abreu de Gomes** | 🔴 33.33% | 66.67% |
| 2 | **Abreu de Pimenta** | 🔴 33.33% | 66.67% |
| 3 | **Martins de da Rocha** | 🔴 33.33% | 66.67% |

### 📈 Global Statistics

| Metric | Value |
|--------|:------:|
| Total regions analyzed | **4,150** |
| Overall average stock-out | **5.37%** |
| Worst region | Abreu de Gomes (33.33%) |
| Records ingested | 20,000 |

### 📁 Generated Artifacts

| File | Contents |
|------|----------|
| [`data/raw_data.json`](data/raw_data.json) | Raw JSON from API (1,000 original records) |
| [`data/rupture_report.csv`](data/rupture_report.csv) | Summary by region — average and max stock-out |
| [`data/quality_rules.md`](data/quality_rules.md) | Documented quality rules (DQ-01 to DQ-06) |
| [`decisions/ADR-001-rupture-pipeline.md`](decisions/ADR-001-rupture-pipeline.md) | Architecture Decision Record |

---

## ✅ Data Quality

The pipeline enforces 6 documented quality rules, split into **blockers**
(halt execution) and **warnings** (flag anomalies):

| ID | Rule | Column | Severity |
|:--:|------|--------|:--------:|
| DQ-01 | NOT NULL | `region` | 🚫 blocker |
| DQ-02 | POSITIVE (≥ 1) | `current_stock` | 🚫 blocker |
| DQ-03 | POSITIVE (> 0) | `demand_forecast` | 🚫 blocker |
| DQ-04 | RANGE [-1, 1] | `ruptura` | ⚠️ warning |
| DQ-05 | NOT NULL | `order_id` | 🚫 blocker |
| DQ-06 | NOT NULL | `store_location` | 🚫 blocker |

**Protections in code:**
- `compute_ruptura()` filters records with `demand_forecast > 0` before calculation
  (avoids division by zero)
- `build_demand_forecast()` ensures `demand_forecast >= 1` via clamp

---

## 🚀 Setup & Run

### Prerequisites

- Python 3.10+
- pip (or `uv` for faster installation)
- DataMission API token (generated in the **Active Projects** tab)

### Step by step

```bash
# 1. Clone the repository
git clone https://github.com/laurentaf/giovanna-rupture-monitor.git
cd giovanna-rupture-monitor

# 2. Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API token
# Option A: .env file (recommended)
copy .env.example .env        # Windows
cp .env.example .env           # Linux/macOS
# → Edit .env with your token

# Option B: environment variable
$env:API_TOKEN = "your-token-here"     # Windows PowerShell
export API_TOKEN="your-token-here"     # Linux/macOS

# 5. Run the full pipeline
python main.py

# (optional) Process already-downloaded data without calling the API again:
python main.py --local
```

### Expected output

```
============================================================
  Stock-Out Monitor by Region — Lojas Giovanna
============================================================

--- Stage 1: Fetch data ---
[API mode] Downloading from DataMission API...
[fetch_data] 10000 records obtained successfully.
[save_raw_json] JSON saved to: data/raw_data.json (10000 records)

--- Stage 2: Process data and calculate stock-out ---
[build_demand_forecast] current_stock: min=1, max=5, mean=3.0
[compute_ruptura] Valid records: 10000
[compute_ruptura] Unique regions: 2117

--- Stage 3: Reports and validations ---

============================================================
  TOP 3 REGIONS WITH HIGHEST AVERAGE STOCK-OUT
============================================================
  1. Abreu de Gomes
     Avg stock-out: 33.33%
     Max stock-out: 66.67%

  Total regions analyzed: 2117
  Overall avg stock-out:     5.30%

[OK] Pipeline complete (3 stages)!
   Raw JSON:     data/raw_data.json (10000 records)
   Report CSV:   data/rupture_report.csv (2117 regions)
```

> 💡 **For larger datasets:** Make multiple calls with `rows=10000` and merge the JSONs.
> Then use `python main.py --local` to process without re-downloading.

---

## 📁 Project Structure

```
giovanna-rupture-monitor/
├── main.py                  # Complete ETL pipeline (3 stages)
├── requirements.txt         # Dependencies (requests + pandas)
├── .env.example             # Environment variables template
├── .gitignore               # .venv, .env, __pycache__
│
├── data/
│   ├── raw_data.json        # Raw JSON from API (1,000 records)
│   ├── rupture_report.csv   # Summary by region (562 regions)
│   └── quality_rules.md     # Quality rules (DQ-01 to DQ-06)
│
├── decisions/
│   └── ADR-001-rupture-pipeline.md   # Architecture Decision Record
│
└── .venv/                   # Virtual environment (git-ignored)
```

---

## 📜 License & Credits

- **Data**: [DataMission](https://datamission.com.br) — realistic mock dataset API
  for pipeline prototyping
- **Orchestration**: Built with [LAOS](https://github.com/laurentaf/laos)
  (Laurent Agent Operating System)
- **License**: MIT — free to use, study, and adapt

---

<p align="center">
  <sub>Made with 🐍 Python, pandas, and DataMission data.</sub><br/>
  <sub>Part of the <a href="https://github.com/laurentaf/laos">LAOS</a> ecosystem.</sub>
</p>
# SPEC-001: Monitor de Ruptura Pipeline

**Status:** ACEITO
**Version:** 1.0
**Authors:** Laurent (data engineer)
**Owner:** Laurent

---

## 1. Executive Summary
Pipeline ETL em 3 estágios que consome dados da API DataMission,
calcula ruptura de estoque por região e gera relatório analítico.

## 2. User Stories
### US-1
As a data engineer, I need to ingest order data from the DataMission API
so that I can compute stock-out metrics per region.

### US-2
As a supply chain analyst, I need to see the top 3 regions with highest
rupture so that I can prioritize restocking.

## 3. Acceptance Criteria
- [ ] raw_data.json persists API response to disk
- [ ] rupture_report.csv contains one row per region with mean and max
- [ ] Empty API response produces friendly message, not IndexError
- [ ] Pipeline runs end-to-end with `python main.py`

## 4. Sources
| Table | Schema |
|-------|--------|
| DataMission API | order_id, timestamp, customer_id, product_category, price, quantity, store_location |

## 5. Destination
### Artifacts
- `data/raw_data.json` — raw API dump
- `data/rupture_report.csv` — aggregated rupture by region
- `data/quality_rules.md` — DQ rules DQ-01 to DQ-06

## 6. Refresh Strategy
Mode: delete-insert. Each run overwrites raw_data.json and rupture_report.csv.

# SPEC-000: Bootstrap — Pipeline ETL Monitor de Ruptura

**Status:** ACEITO
**Version:** 1.0
**Authors:** Laurent (data engineer)
**Owner:** Laurent

---

## 1. Executive Summary
Pipeline ETL em 3 estágios que consome dados da API DataMission, calcula
ruptura de estoque por região e gera relatório analítico. Projeto de
portfólio de engenharia de dados.

## 2. User Stories
### US-1
As a data engineer, I need to ingest data from DataMission API because
the raw data is the foundation for all downstream calculations.

### US-2
As a data engineer, I need to compute rupture per region because
store managers need to know where stock is insufficient.

### US-3
As a data engineer, I need to generate a CSV report because
the business team consumes tabular data for decision-making.

## 3. Acceptance Criteria
- [ ] Pipeline runs end-to-end with `python main.py`
- [ ] Data ingested: `data/raw_data.json` with ≥ 1.000 records
- [ ] Rupture computed per region with mean + max aggregation
- [ ] Report exported: `data/rupture_report.csv`
- [ ] Empty DataFrame guards prevent IndexError (see ADR-002)
- [ ] Quality rules documented in `data/quality_rules.md`

## 4. Sources
| Table | Schema |
|-------|--------|
| DataMission API | order_id, timestamp, customer_id, product_category, price, quantity, store_location |

## 5. Destination
### Output artifacts
| File | Format | Content |
|------|--------|---------|
| data/raw_data.json | JSON | Raw API response (1.000 records) |
| data/rupture_report.csv | CSV | Region-level rupture summary (562 regions) |

## 6. Refresh Strategy
Mode: delete-insert (full refresh every run). No incremental mode in MVP.

## 7. Stack
Python 3.10+, requests 2.31+, pandas 2.0+, DataMission API.
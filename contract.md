# Contract – Giovanna Rupture Monitor

Este documento formaliza o escopo, necessidades, entregáveis e capacidades utilizadas pelo projeto **Giovanna Ruptura Monitor**.

## Brief
Monitorar a ruptura de estoque por região nas lojas Giovanna, com dados sintéticos ShadowTraffic, pipeline ETL em 3 estágios, relatório CSV e dashboard HTML. Dockerizado: único `docker run` produz dashboard funcional.

## Needs
- data
- etl
- data-quality
- dashboard
- presentation

## Deliverables
- `main.py` — pipeline ETL com ShadowTraffic (modo --local)
- `generate_shadowtraffic_data.py` — gerador de dados sintéticos
- `dashboard.html` — dashboard interativo com mapa de ruptura
- `data/rupture_report.csv` — relatório de ruptura por região
- `data/raw_data.json` — dataset sintético usado pelo pipeline
- `Dockerfile` + `entrypoint.sh` + `docker-compose.yml` — containerização
- `README.md` — documentação com instruções Docker e local

## Capabilities Used
- **latade** (primary) — SQL, data engineering, data quality
- **ladesign** (optional) — dashboard, presentation

## Repo
https://github.com/laurentaf/giovanna-rupture-monitor

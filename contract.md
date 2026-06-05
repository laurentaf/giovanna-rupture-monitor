# Contract — Monitor de Ruptura por Região Lojas Giovanna

## Brief
Pipeline ETL em 3 estágios que consome dados da API DataMission
(datamission.com.br/projects/93fa0f19-ae51-4ed9-986b-47457ac2f26a),
calcula ruptura de estoque por região e gera relatório analítico.
Projeto de portfólio de engenharia de dados.

## Needs
- etl
- data
- data-quality

## Capabilities Used
- **latade** (primary) — SQL, data engineering, data quality
- **ladesign** (optional) — presentation

## Deliverables
- `data/raw_data.json` — Dados brutos da API
- `data/rupture_report.csv` — Relatório de ruptura por região
- `main.py` — Pipeline ETL com 3 estágios
- `README.md` — Documentação de portfólio
- `data/quality_rules.md` — Regras DQ-01 a DQ-06
- `decisions/ADR-001-rupture-pipeline.md` — Decisão de arquitetura
- `decisions/ADR-002-empty-dataframe-guards.md` — Guards de DataFrame vazio

## Repo
https://github.com/laurentaf/giovanna-rupture-monitor

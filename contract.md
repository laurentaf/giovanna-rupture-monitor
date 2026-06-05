# Contrato do Projeto — Monitor de Ruptura por Região (Lojas Giovanna)

## Brief
Pipeline ETL em 3 estágios que consome dados da API DataMission,
calcula ruptura de estoque por região e gera relatório analítico para
as Lojas Giovanna. Projeto de portfólio de engenharia de dados com foco
em reprodutibilidade, qualidade de dados e documentação.

## Needs
- **etl** — pipeline de ingestão, transformação e carga
- **data** — modelagem e processamento de dados
- **data-quality** — regras de qualidade (DQ-01 a DQ-06)

## Capabilities Utilizadas
- **latade** (primary) — SQL, modelagem, DQ, pipeline de dados
- **ladesign** (optional) — suporte a apresentação visual

## Deliverables
| Artefato | Descrição |
|----------|-----------|
| `data/raw_data.json` | Dados brutos obtidos da API DataMission |
| `data/rupture_report.csv` | Relatório de ruptura por região (562 regiões) |
| `main.py` | Pipeline ETL com 3 estágios (fetch, process, report) |
| `README.md` | Documentação completa do projeto (10K+ chars) |
| `data/quality_rules.md` | 6 regras de qualidade documentadas |
| `spec/adr/001-rupture-pipeline.md` | Decisão arquitetural sobre stack e pipeline |
| `spec/adr/002-empty-dataframe-guards.md` | Decisão sobre guards de DataFrame vazio |

## Repositório
https://github.com/laurentaf/giovanna-rupture-monitor
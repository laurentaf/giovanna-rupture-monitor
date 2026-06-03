# Monitor de Ruptura por Região — Lojas Giovanna

Pipeline ETL em 3 estágios que monitora **ruptura de estoque por região**
usando dados da API DataMission.

## Arquitetura

```
API DataMission
      │
      ▼
┌─────────────────┐
│ Estágio 1       │  fetch_data()
│ Ingestão via API│  → data/raw_data.json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Estágio 2       │  build_demand_forecast() + compute_rupture()
│ Processamento   │  Cria colunas: regiao, estoque_atual, demanda_prevista
│                 │  Calcula ruptura = (demanda - estoque) / demanda
│                 │  Agrega por região (mean, max)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Estágio 3       │  print_summary() + save_report()
│ Relatórios      │  Top 3 regiões com maior ruptura
│                 │  → data/rupture_report.csv
└─────────────────┘
```

## Cálculo de ruptura

```
ruptura = (demanda_prevista - estoque_atual) / demanda_prevista
```

- **Positivo** → estoque insuficiente para atender a demanda (RUPTURA)
- **Negativo** → excesso de estoque
- **Zero** → demanda exatamente atendida

## Pré-requisitos

- Python 3.10+
- pip

## Setup

```bash
# 1. Clonar
git clone https://github.com/laurentaf/giovanna-rupture-monitor.git
cd giovanna-rupture-monitor

# 2. Venv
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Dependências
pip install -r requirements.txt
```

## Configuração da API

Gere seu token na aba **Projetos Ativos** do DataMission.

```bash
# Opção 1: .env (recomendado)
copy .env.example .env   # Windows
# Edite .env com seu token

# Opção 2: variável de ambiente
$env:API_TOKEN = "seu-token"  # Windows PowerShell
export API_TOKEN="seu-token"   # Linux/Mac
```

## Execução

```bash
python main.py
```

## Saídas

| Estágio | Arquivo | Descrição |
|---------|---------|-----------|
| 1 | `data/raw_data.json` | JSON bruto da API (1000 registros) |
| 3 | `data/rupture_report.csv` | Resumo por região (média e máximo da ruptura) |

## Regras de qualidade

Ver [data/quality_rules.md](data/quality_rules.md).

## Decisões técnicas

Ver [decisions/](decisions/).

## Projeto

Gerado pela [LAOS](https://github.com/laurentaf/laos).

# 🔍 Monitor de Ruptura por Região — Lojas Giovanna

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="pandas 2.0+"/>
  <img src="https://img.shields.io/badge/requests-2.31%2B-FF6F00?style=for-the-badge&logo=curl&logoColor=white" alt="requests 2.31+"/>
  <img src="https://img.shields.io/badge/DataMission-API-6A0DAD?style=for-the-badge&logo=databricks&logoColor=white" alt="DataMission API"/>
  <img src="https://img.shields.io/badge/status-produção-00C853?style=for-the-badge" alt="Status: Produção"/>
</p>

<p align="center">
  <strong>Pipeline ETL em 3 estágios</strong> — ingestão, processamento e relatório de<br/>
  ruptura de estoque por região, alimentado pela API <strong>DataMission</strong>.
</p>

---

## 📋 O Problema

Ruptura de estoque — quando a demanda de um produto supera o estoque disponível —
é um dos maiores vilões do varejo físico. Cada item em falta representa:

- **Venda perdida** irremediável (o cliente não espera)
- **Queda na satisfação** e risco de migração para concorrentes
- **Distorção na alocação** — estoque mal distribuído entre regiões

Este pipeline resolve uma pergunta simples que muitos sistemas legacy não respondem
em tempo hábil: **onde está faltando produto, e quanto?**

> _"Não se gerencia o que não se mede. E não se mede o que não se define."_

O projeto define **ruptura** como o percentual da demanda não atendida:

```
ruptura = (demanda_prevista - estoque_atual) / demanda_prevista
```

| Valor | Significado |
|-------|-------------|
| `> 0` | 🔴 Ruptura — estoque insuficiente para atender a demanda |
| `= 0` | 🟢 Equilíbrio — demanda exatamente atendida |
| `< 0` | 🟡 Excesso de estoque — capital empatado |

---

## 🏗️ Arquitetura do Pipeline

```mermaid
flowchart TB
    subgraph Estágio1["Estágio 1 — Ingestão"]
        A[API DataMission<br/>GET /projects/{id}/dataset] --> B[requests.get<br/>headers: Bearer token]
        B --> C[raw_data.json<br/>1.000 registros]
    end

    subgraph Estágio2["Estágio 2 — Processamento"]
        C --> D[build_demand_forecast<br/>pandas DataFrame]
        D --> E[compute_rupture<br/>groupby por região<br/>média + máximo]
    end

    subgraph Estágio3["Estágio 3 — Relatório"]
        E --> F[print_summary<br/>Top 3 regiões]
        E --> G[rupture_report.csv<br/>562 regiões analisadas]
    end

    style Estágio1 fill:#E3F2FD,stroke:#1565C0
    style Estágio2 fill:#FFF3E0,stroke:#E65100
    style Estágio3 fill:#E8F5E9,stroke:#2E7D32
```

### Fluxo de dados

```
📥 Estágio 1: fetch_data()
    │  requests.get → API DataMission
    │  Valida: status 200, JSON decodificável
    ▼
data/raw_data.json  (1.000 registros)

📊 Estágio 2: process_inventory()
    │  pandas.read_json → DataFrame
    │  build_demand_forecast() → colunas: regiao, estoque_atual, demanda_prevista
    │  compute_rupture() → ruptura = (demanda - estoque) / demanda
    │  groupby("regiao").agg(["mean", "max"])
    ▼
Resumo por região  (562 regiões)

📄 Estágio 3: print_summary() + save_report()
    │  Top 3 regiões com maior ruptura
    │  Exporta → data/rupture_report.csv
    ▼
Relatório final
```

### Decisões arquiteturais

| Decisão | Alternativa | Escolha |
|---------|-------------|---------|
| Pipeline monolítico vs. orquestrado | Airflow, Prefect | `main.py` sequencial — simplicidade para MVP |
| JSON vs. CSV como raw | CSV, Parquet | JSON — fidelidade ao schema da API |
| pandas vs. DuckDB | DuckDB, Polars | pandas — ecossistema maduro para CI/CD e prototipação |
| `.env` vs. secrets manager | AWS Secrets, Vault | `.env` + `os.environ` — portátil e sem dependência cloud |

> 📖 Detalhamento completo da decisão: [`decisions/ADR-001-rupture-pipeline.md`](decisions/ADR-001-rupture-pipeline.md)

---

## 🛠️ Stack & Tecnologias

| Tecnologia | Versão | Papel no Pipeline |
|------------|--------|-------------------|
| [![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org) | ≥ 3.10 | Runtime principal — tipagem, f-strings, `os.environ` |
| [![pandas](https://img.shields.io/badge/pandas-2.0%2B-150458?logo=pandas)](https://pandas.pydata.org) | ≥ 2.0.0 | DataFrame operations, groupby aggregations |
| [![requests](https://img.shields.io/badge/requests-2.31%2B-FF6F00?logo=curl)](https://requests.readthedocs.io) | ≥ 2.31.0 | HTTP Client para ingestão via API REST |
| [![DataMission](https://img.shields.io/badge/DataMission-API-6A0DAD)](https://datamission.com.br) | — | Fonte de dados fictícios realistas (pedidos/inventário) |

### Dependências mínimas

```txt
requests>=2.31.0
pandas>=2.0.0
```

Apenas **2 dependências externas** — pipeline leve, portátil e reproduzível
em qualquer ambiente com Python.

---

## 📊 Resultados Reais

Pipeline executado com dados reais da API DataMission (1.000 registros, 562 regiões):

### 🥇 Top 3 Regiões com Maior Ruptura Média

| # | Região | Ruptura Média | Ruptura Máxima |
|---|--------|:--------------:|:--------------:|
| 1 | **Siqueira de Brito** | 🔴 33,33% | 66,67% |
| 2 | **Teixeira de Cunha** | 🔴 33,33% | 66,67% |
| 3 | **Vieira** | 🔴 33,33% | 66,67% |

### 📈 Estatísticas Globais

| Métrica | Valor |
|---------|:-----:|
| Total de regiões analisadas | **562** |
| Média geral de ruptura | **4,57%** |
| Pior região | Siqueira de Brito (33,33%) |
| Registros ingeridos | 1.000 |

### 📁 Artefatos Gerados

| Arquivo | Conteúdo |
|---------|----------|
| [`data/raw_data.json`](data/raw_data.json) | JSON bruto da API (1.000 registros originais) |
| [`data/rupture_report.csv`](data/rupture_report.csv) | Resumo por região — média e máximo da ruptura |
| [`data/quality_rules.md`](data/quality_rules.md) | Regras de qualidade documentadas (DQ-01 a DQ-06) |
| [`decisions/ADR-001-rupture-pipeline.md`](decisions/ADR-001-rupture-pipeline.md) | Architecture Decision Record |

---

## ✅ Qualidade de Dados

O pipeline valida 6 regras de qualidade documentadas, divididas em **blockers**
(impedem a execução) e **warnings** (sinalizam anomalias):

| ID | Regra | Coluna | Severidade |
|:--:|-------|--------|:----------:|
| DQ-01 | NOT NULL | `regiao` | 🚫 blocker |
| DQ-02 | POSITIVE (≥ 1) | `estoque_atual` | 🚫 blocker |
| DQ-03 | POSITIVE (> 0) | `demanda_prevista` | 🚫 blocker |
| DQ-04 | RANGE [-1, 1] | `ruptura` | ⚠️ warning |
| DQ-05 | NOT NULL | `order_id` | 🚫 blocker |
| DQ-06 | NOT NULL | `store_location` | 🚫 blocker |

**Proteções implementadas no código:**
- `compute_rupture()` filtra registros com `demanda_prevista > 0` antes do cálculo
  (evita divisão por zero)
- `build_demand_forecast()` garante `demanda_prevista >= 1` via clamp

---

## 🚀 Setup & Execução

### Pré-requisitos

- Python 3.10+
- pip (ou `uv` para instalação mais rápida)
- Token de API DataMission (gerado na aba **Projetos Ativos**)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/laurentaf/giovanna-rupture-monitor.git
cd giovanna-rupture-monitor

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o token da API
# Opção A: arquivo .env (recomendado)
copy .env.example .env        # Windows
cp .env.example .env           # Linux/macOS
# → Edite .env com seu token

# Opção B: variável de ambiente
$env:API_TOKEN = "seu-token-aqui"     # Windows PowerShell
export API_TOKEN="seu-token-aqui"     # Linux/macOS

# 5. Execute o pipeline completo
python main.py
```

### Saída esperada

```bash
============================================================
  Monitor de Ruptura por Regiao — Lojas Giovanna
============================================================

--- Estagio 1: Obter dados da API ---
[fetch_data] 1000 registros obtidos com sucesso.
[save_raw_json] JSON salvo em: data/raw_data.json (1000 registros)

--- Estagio 2: Processar dados e calcular ruptura ---
[build_demand_forecast] estoque_atual: min=1, max=825, media=277.0
[compute_rupture] Registros com demanda valida: 1000
[compute_rupture] Regioes unicas: 562

--- Estagio 3: Relatorios e validacoes ---

============================================================
  TOP 3 REGIOES COM MAIOR RUPTURA MEDIA
============================================================
  1. Siqueira de Brito
     Ruptura media: 33,33%
     Ruptura max:   66,67%

  Total de regioes analisadas: 562
  Media geral de ruptura:     4,57%

[OK] Pipeline completo (3 estagios)!
   JSON bruto:     data/raw_data.json
   Relatorio CSV:  data/rupture_report.csv
```

---

## 📁 Estrutura do Projeto

```
giovanna-rupture-monitor/
├── main.py                  # Pipeline ETL completo (3 estágios)
├── requirements.txt         # Dependências (requests + pandas)
├── .env.example             # Template para variáveis de ambiente
├── .gitignore               # .venv, .env, __pycache__
│
├── data/
│   ├── raw_data.json        # JSON bruto da API (1.000 registros)
│   ├── rupture_report.csv   # Resumo por região (562 regiões)
│   └── quality_rules.md     # Regras de qualidade (DQ-01 a DQ-06)
│
├── decisions/
│   └── ADR-001-rupture-pipeline.md   # Architecture Decision Record
│
└── .venv/                   # Ambiente virtual (gitignorado)
```

---

## 📜 Licença & Créditos

- **Dados**: [DataMission](https://datamission.com.br) — API de datasets fictícios
  realistas para prototipação de pipelines
- **Orquestração**: Projeto gerado e gerenciado pela [LAOS](https://github.com/laurentaf/laos)
  (Laurent Agent Operating System) — arcabouço de orquestração de agentes
- **Licença**: MIT — sinta-se livre para usar, estudar e adaptar

---

<p align="center">
  <sub>Feito com 🐍 Python, pandas e dados da DataMission.</sub><br/>
  <sub>Parte do ecossistema <a href="https://github.com/laurentaf/laos">LAOS</a>.</sub>
</p>

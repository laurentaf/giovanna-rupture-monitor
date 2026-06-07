# 🔍 Giovanna Rupture Monitor

Projeto de monitoramento de ruptura de estoque por região nas lojas **Giovanna**. O pipeline ETL ingest​a dados (agora usando ShadowTraffic), calcula a métrica de ruptura e gera um dashboard HTML e um relatório CSV.

## Principais Artefatos
- `dashboard.html` – visualização interativa do mapa de ruptura.
- `data/rupture_report.csv` – resumo por região (ruptura média e máxima).
- `data/raw_data.json` – dataset sintético usado na execução local (`--local`).

## Como rodar

### Opção 1: Docker (recomendado)
```bash
# 1. Construa a imagem
docker build -t giovanna-monitor .

# 2. Execute o container (mapeie porta 8000)
docker run -p 8000:8000 --name giovanna-run giovanna-monitor

# 3. Acesse o dashboard
navegador → http://localhost:8000/dashboard.html
```
> O container já executa o pipeline (`python main.py --local`) antes de servir o dashboard.

### Opção 2: Local (sem Docker)
```bash
# 1. Instale dependências
pip install -r requirements.txt

# 2. Rode pipeline (usa dados locais)
python main.py --local

# 3. Sirva o dashboard
python -m http.server 8000
# Acesse: http://localhost:8000/dashboard.html
```

## Tecnologias
- **Python 3.10+**, **pandas**
- **LADESIGN** – dashboard HTML
- **LATADE** – pipeline medallion (bronze → silver → gold)

## Onde está o quê

| Caminho | Descrição |
|---------|-----------|
| `main.py` | Pipeline ETL principal (ingestão → transformação → CSV) |
| `data/raw_data.json` | Dataset sintético ShadowTraffic (determinístico) |
| `data/rupture_report.csv` | Relatório agregado por região (saída do pipeline) |
| `dashboard.html` | Dashboard HTML interativo de ruptura |
| `Dockerfile` | Build do container Docker com pipeline + dashboard |
| `spec/constitution.md` | Constituição SDD do projeto |
| `spec/todo.md` | Roadmap e tracker de tarefas |

## Documentação de Arquitetura
Veja a *SDD* em `spec/constitution.md` e o *roadmap* em `spec/todo.md`.

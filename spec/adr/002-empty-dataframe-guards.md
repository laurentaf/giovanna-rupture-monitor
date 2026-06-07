# ADR-002: Guards para DataFrame vazio em todas as etapas do pipeline

## Status

Accepted

## Contexto

O pipeline pode receber dados vazios (JSON vazio, arquivo corrompido, ou zero registros após filtro). Sem guards, operações como `.mean()`, `.min()`, `.max()`, `groupby()`, `to_csv()`, e `.iloc[0]` geram `IndexError` ou `ValueError`, travando a execução.

Isso é particularmente importante no contexto Docker, onde o pipeline roda automaticamente no entrypoint e uma falha não-tratada derruba o container sem mensagem útil.

## Decisão

Adicionar guards de DataFrame vazio em todas as etapas do pipeline:

| Função | Proteção |
|--------|----------|
| ingest() | Valida colunas obrigatórias; early exit com mensagem se 0 registros |
| main() | Early exit com mensagem clara se ingest() retornar DF vazio |
| transform() | Retorna DF vazio com colunas corretas se input vazio; zero-division guard em pct_critico |
| print_summary() | Mensagem amigável + return cedo se summary vazia |
| save_report() | Avisa se DataFrame vazio antes de salvar; escreve CSV com header apenas |

### Regra geral

Antes de qualquer operação de indexação ou agregação em DataFrame:
```python
if df.empty:
    print("...")
    return pd.DataFrame(columns=[...])
```

Antes de acessar índices fixos (iloc[0]):
```python
if top3.empty:
    print("Nenhum dado para exibir")
    return
```

## Alternativas

### A) Try/except genérico
Rejeitado porque mascara erros reais.

### B) Schema validation library (pandera, great_expectations)
Rejeitado por adicionar dependência pesada para um pipeline de 1 dependência (pandas).

## Consequências

+ Pipeline nunca trava por IndexError ou ValueError com dados vazios
+ Mensagens de erro claras indicam o problema exato
+ Comportamento consistente em todas as etapas
+ Docker container não derruba silenciosamente — sempre loga o problema
- Boilerplate adicional em cada função (~10 linhas extras)

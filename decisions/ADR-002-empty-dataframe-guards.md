# ADR-002: Guards para DataFrame vazio em todas as etapas do pipeline

## Status

Aceito

## Contexto

O Data Mission rejeitou a entrega (REJECTED) porque `print_summary()` assume que
existe pelo menos uma regiao e acessa `top3.iloc[0]` sem verificar se `summary`
esta vazio. Quando a API nao retorna registros (ou o arquivo JSON local esta
vazio), isso gera `IndexError` e toda a execucao trava.

O mesmo risco existe em todas as operacoes de agregacao do pipeline:
`.mean()`, `.min()`, `.max()`, `groupby()`, `to_csv()`.

## Decisao

Adicionar guards de DataFrame vazio em todas as etapas do pipeline:

| Funcao | Protecao |
|--------|----------|
| `fetch_data()` | Avisa se API retornar lista vazia |
| `load_local_json()` | sys.exit se arquivo vazio ou inexistente |
| `main()` | early exit com mensagem clara se raw_data vazio |
| `build_demand_forecast()` | Retorna DF vazio com colunas corretas se input vazio |
| `compute_rupture()` | Retorna DF vazio com colunas se sem registros validos |
| `print_summary()` | Mensagem amigavel + return cedo se summary vazia; so acessa `top3.iloc[0]` apos verificar |
| `save_report()` | Avisa se DataFrame vazio antes de salvar |

### Regra geral

**Antes de qualquer operacao de indexacao ou agregacao em DataFrame:**

```python
if df.empty:
    print("AVISO: DataFrame vazio — pulando operacao.")
    return  # ou DF vazio com colunas corretas
```

**Antes de acessar indices fixos (`iloc[0]`, `iloc[-1]`):**

```python
if top3.empty:
    print("Nenhuma regiao para exibir.")
    return
# agora seguro: top3.iloc[0]
```

## Consequencias

**Positivas:**
- Pipeline nunca trava por IndexError ou ValueError com dados vazios
- Mensagens de erro claras indicam o problema exato
- Comportamento consistente em todas as etapas

**Negativas:**
- Boilerplate adicional em cada funcao (~10 linhas extras)
- Pode mascarar problemas de dados se os guards forem muito permissivos

## Referencia

- P0 em `knowledge/padroes-entrega.md` (LAOS): "todo pipeline de dados deve
  validar DataFrame vazio antes de operacoes de indexacao ou agregacao"
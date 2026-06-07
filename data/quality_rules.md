# Regras de Qualidade — Monitor de Ruptura

## Regras documentadas

| ID | Regra | Coluna | Descrição | Severidade |
|----|-------|--------|-----------|------------|
| DQ-01 | NOT NULL | `regiao` | Região não pode ser nula | blocker |
| DQ-02 | NOT NULL | `produto` | Produto não pode ser nulo | blocker |
| DQ-03 | POSITIVE | `estoque_atual` | Estoque atual deve ser ≥ 0 | blocker |
| DQ-04 | POSITIVE | `giro_diario` | Giro diário deve ser ≥ 0 | warning |
| DQ-05 | POSITIVE | `cobertura_dias` | Cobertura em dias deve ser ≥ 0 | warning |
| DQ-06 | RANGE [0, 1] | `irc` | IRC deve estar entre 0 e 1 | warning |
| DQ-07 | NOT NULL | `risco` | Nível de risco não pode ser nulo | blocker |
| DQ-08 | IN {0, 1} | `critico` | Flag crítico deve ser 0 ou 1 | blocker |

## Validações no pipeline

- `ingest()` valida presença das 9 colunas obrigatórias antes de prosseguir.
- `transform()` verifica `df.empty` antes de qualquer agregação — retorna DataFrame vazio com colunas corretas.
- `save_report()` verifica `summary.empty` antes de `to_csv()` — escreve CSV com header apenas se vazio.
- `print_summary()` exibe mensagem amigável se não houver dados.

# Regras de Qualidade — Monitor de Ruptura

## Regras documentadas

| ID | Regra | Coluna | Descrição | Severidade |
|----|-------|--------|-----------|------------|
| DQ-01 | NOT NULL | `regiao` | Região não pode ser nula | blocker |
| DQ-02 | POSITIVE | `estoque_atual` | Estoque atual deve ser ≥ 1 | blocker |
| DQ-03 | POSITIVE | `demanda_prevista` | Demanda prevista deve ser > 0 | blocker |
| DQ-04 | RANGE | `ruptura` | Ruptura deve estar entre -1 e 1 | warning |
| DQ-05 | NOT NULL | `order_id` | ID do pedido não pode ser nulo | blocker |
| DQ-06 | NOT NULL | `store_location` | Loja não pode ser nula | blocker |

## Validações no pipeline

- `compute_rupture()` filtra registros com `demanda_prevista > 0` antes
  de calcular a ruptura (evita divisão por zero).
- `build_demand_forecast()` garante `demanda_prevista >= 1` via clamp.

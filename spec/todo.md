# TODO — Monitor de Ruptura Lojas Giovanna

---

## Missão 0 — SDD Scaffold (obrigatória)

- [x] spec/constitution.md
- [x] spec/todo.md
- [x] spec/adr/_template.md
- [x] spec/adr/README.md
- [x] spec/harness/_template.md
- [x] spec/specs/000-bootstrap/spec.md
- [x] contract.md
- [x] ADRs movidos de decisions/ para spec/adr/

---

## Estágio 1 — Ingestão (fetch_data)

- [x] Implementar fetch_data() com requests
- [x] Salvar raw_data.json em disco
- [x] Guard: API retornar lista vazia
- [x] Suporte a modo --local

## Estágio 2 — Processamento (build_demand_forecast + compute_rupture)

- [x] build_demand_forecast(): derivar regiao, estoque_atual, demanda_prevista
- [x] compute_rupture(): calcular ruptura por registro
- [x] Agregar por regiao (mean + max)
- [x] Guard: DataFrame vazio em cada etapa
- [x] Guard: demanda_prevista > 0 antes de divisao

## Estágio 3 — Relatório (print_summary + save_report)

- [x] print_summary(): top 3 regioes
- [x] Guard: summary vazio antes de acessar iloc[0]
- [x] save_report(): exportar rupture_report.csv
- [x] Guard: DataFrame vazio antes de salvar

## Qualidade de Dados

- [x] DQ-01: NOT NULL regiao
- [x] DQ-02: POSITIVE estoque_atual
- [x] DQ-03: POSITIVE demanda_prevista
- [x] DQ-04: RANGE ruptura
- [x] DQ-05: NOT NULL order_id
- [x] DQ-06: NOT NULL store_location

---

## Phase 10: Remaining

- [ ] GitHub Actions CI/CD
- [ ] Testes unitarios com pytest
- [ ] Pre-commit hooks

---

## Completed

- [x] Pipeline 3 estagios funcional
- [x] README com documentacao completa
- [x] ADR-001: arquitetura do pipeline
- [x] ADR-002: empty dataframe guards
- [x] Regras de qualidade documentadas (DQ-01 a DQ-06)
- [x] Missao 0 — SDD scaffold

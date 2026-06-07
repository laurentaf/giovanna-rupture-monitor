# Constitution – Project Skeleton

This file defines the mandatory SDD scaffold for the project. All sections are required by the Missão 0.

## Article I – Project Purpose
Define the business problem and success criteria.

## Article II – Architecture Overview
High‑level diagram of data sources, processing layers and dashboard.

## Article III – Governance
Roles, review process and delivery checklist.

## Scope

- Monitoramento de ruptura de estoque por região nas lojas Giovanna.
- Pipeline ETL: ingestão de dados ShadowTraffic → transformação (cálculo IRC v2) → relatório CSV agregado por região.
- Dashboard HTML servido via Docker container, consumindo o CSV gerado.
- Dados determinísticos e reprodutíveis (sem dependência de API externa em modo `--local`).

## Non-goals

- Previsão de demanda ou reposição automática (somente diagnóstico de ruptura atual).
- Integração com ERP ou sistemas de gestão da Giovanna (escopo futuro, não neste ciclo).
- Dashboard real-time ou streaming (o pipeline é batch, rodado sob demanda).
- Análise por loja individual (granularidade é por região).

## Article IV – Risks & Mitigations
List of known risks and mitigation strategies.

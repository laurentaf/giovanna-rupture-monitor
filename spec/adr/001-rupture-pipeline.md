# ADR-001: Pipeline de Monitor de Ruptura em 3 Estágios

## Status

Accepted

## Contexto

Precisamos de um pipeline que consuma dados de pedidos de uma API e produza
um relatório de ruptura de estoque por região.

**Evolução do projeto:**
- **v1 (DataMission)**: Pipeline inicial consumia API DataMission (pedidos com order_id, customer_id, product_category, price, quantity, store_location). Não continha estoque_atual nem demanda_prevista — derivamos estoque de quantity e simulamos demanda via SHA256 determinístico.
- **v2 (ShadowTraffic)**: Migramos para geração sintética local com ShadowTraffic (via script Python equivalente). Motivação: controle total sobre aleatoriedade, volume, distribuição de risco (critico/alerta/normal/confortavel/excesso), e modelo de dados rico (estoque, giro_diario, cobertura_dias, IRC). Elimina dependência de API externa e token.

## Decisão

Pipeline em 3 estágios (mantido, fonte alterada):

1. **Ingestão**: `generate_shadowtraffic_data.py` → JSON sintético em disco (`data/raw_data_shadowtraffic.json`)
   - 27 cidades, ~14-20k produtos, seed determinístico (42)
   - Gera: regiao, produto, categoria, estoque_atual, giro_diario, cobertura_dias, irc, risco, critico
2. **Processamento**: Agrega por cidade calculando:
   - `irc_medio`, `cobertura_media_dias`, `giro_medio`
   - `qtd_critico`, `pct_critico`
   - `risco_predominante` baseado no IRC médio (critico > 0.80, alerta 0.55-0.80, normal 0.30-0.55, confortavel 0.10-0.30, excesso < 0.10)
3. **Relatório**: `rupture_report.csv` com 27 cidades + dashboard HTML (`dashboard.html`)

## Alternativas

### A) DuckDB + SQL
Alternativa com DuckDB em vez de pandas. Rejeitada porque o pandas oferece
prototipação mais rápida e ecossistema maduro para CI/CD.

### B) Polars
Alternativa performática com Polars. Rejeitada por ser menos conhecida no
portfolio de engenharia de dados.

### C) Manter DataMission API
Rejeitado: dependência externa, token necessário, volume limitado (10k/chamada), sem controle sobre distribuição de risco/estoque, schema de pedidos não de estoque.

## Consequências

+ Pipeline 100% local, reprodutível, sem segredos
+ Modelo de dados rico: estoque, giro, cobertura, IRC, risco — compatível com dashboard
+ Distribuição de risco balanceada (critico, alerta, normal, confortavel, excesso)
+ Volume configurável (seed determinístico para reprodutibilidade)
- Dados sintéticos, não reais — adequado para portfolio/demo, não para produção
- Requer manutenção do script de geração se schema mudar

## Métricas v2 (ShadowTraffic)

| Métrica | Valor |
|---------|-------|
| Cidades | 27 |
| Produtos totais | ~14.000 |
| IRC médio geral | ~35% |
| Cobertura média | ~9.3 dias |
| Risco predominante | 2 critico, 4 alerta, 7 normal, 9 confortavel, 5 excesso |
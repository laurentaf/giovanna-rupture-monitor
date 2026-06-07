#!/usr/bin/env python3
"""
ShadowTraffic Data Generator — Monitor de Ruptura Lojas Giovanna

Gera dados sintéticos de estoque por cidade/região com:
- estoque_atual, giro_diario, cobertura_dias
- IRC = max(0, 1 - cobertura_dias / 14)
- risco: critico/alerta/normal/confortavel/excesso
- qtd_critico, pct_critico

Reproduz o modelo que o dashboard espera (source.md + dashboard.html).
"""

import json
import random
import hashlib
from pathlib import Path
import pandas as pd

# Seed determinístico para reprodutibilidade
SEED = 42
random.seed(SEED)

# ─── Cidades/Regiões (27 cidades como no source.md) ──────────────────────────
CIDADES = [
    "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador",
    "Fortaleza", "Curitiba", "Manaus", "Recife", "Porto Alegre",
    "Belém", "Goiânia", "Guarulhos", "Campinas", "São Luís",
    "São Gonçalo", "Maceió", "Duque de Caxias", "Natal", "Teresina",
    "São Bernardo do Campo", "João Pessoa", "Jaboatão dos Guararapes",
    "Santo André", "Osasco", "Ribeirão Preto", "Uberlândia"
]

# ─── Target IRC por cidade (para garantir cobertura dos 5 riscos) ────────────
# IRC ranges: critico > 0.80, alerta 0.55-0.80, normal 0.30-0.55, confortavel 0.10-0.30, excesso < 0.10
CIDADE_IRC_TARGET = {
    "Curitiba": 0.85,      # critico
    "Ribeirão Preto": 0.82, # critico
    "São Bernardo do Campo": 0.79, # critico
    "Manaus": 0.65,        # alerta
    "Fortaleza": 0.60,     # alerta
    "João Pessoa": 0.58,   # alerta
    "Duque de Caxias": 0.55, # alerta
    "Belo Horizonte": 0.50, # normal
    "Goiânia": 0.45,       # normal
    "Campinas": 0.42,      # normal
    "Salvador": 0.38,      # normal
    "Natal": 0.35,         # normal
    "Porto Alegre": 0.28,  # confortavel
    "Maceió": 0.25,        # confortavel
    "São Paulo": 0.22,     # confortavel
    "Santo André": 0.20,   # confortavel
    "Recife": 0.18,        # confortavel
    "Guarulhos": 0.15,     # confortavel
    "São Gonçalo": 0.12,   # confortavel
    "Belém": 0.08,         # excesso
    "Teresina": 0.06,      # excesso
    "Brasília": 0.05,      # excesso
    "Osasco": 0.04,        # excesso
    "Jaboatão dos Guararapes": 0.03, # excesso
    "São Luís": 0.02,      # excesso
    "Uberlândia": 0.01,    # excesso
    "Rio de Janeiro": 0.40  # normal (extra)
}

# ─── Produtos por cidade ──────────────────────────────────────────────────────
PRODUTOS_POR_CIDADE = {
    "Moda": ["Camiseta", "Calça", "Vestido", "Tênis", "Jaqueta"],
    "Eletrônicos": ["Smartphone", "Notebook", "Fone", "Carregador", "Mouse"],
    "Casa": ["Sofá", "Mesa", "Cadeira", "Luminária", "Tapete"],
    "Beleza": ["Perfume", "Creme", "Shampoo", "Maquiagem", "Protetor"],
    "Esporte": ["Bicicleta", "Halteres", "Tapete Yoga", "Bola", "Raquete"]
}

# ─── Risco baseado em IRC ────────────────────────────────────────────────────
def classificar_risco(irc: float) -> str:
    """Classifica risco baseado no IRC (0 a 1)."""
    if irc > 0.80:
        return "critico"
    elif irc > 0.55:
        return "alerta"
    elif irc > 0.30:
        return "normal"
    elif irc > 0.10:
        return "confortavel"
    else:
        return "excesso"

def gerar_dados_cidade(cidade: str) -> list[dict]:
    """
    Gera registros de produtos para uma cidade.
    Cada produto tem estoque, giro, cobertura, IRC e risco.
    """
    registros = []
    n_produtos = random.randint(200, 800)  # 200-800 produtos por cidade (total ~20k)

    # IRC alvo para esta cidade (determina risco predominante)
    target_irc = CIDADE_IRC_TARGET.get(cidade, 0.50)
    
    # Cobertura alvo: IRC = max(0, 1 - cobertura/14) -> cobertura = 14 * (1 - IRC)
    target_cobertura = max(0.0, 14.0 * (1.0 - target_irc))
    
    # Variação ao redor do alvo (±30%)
    cobertura_min = target_cobertura * 0.7
    cobertura_max = target_cobertura * 1.3

    for _ in range(n_produtos):
        categoria = random.choice(list(PRODUTOS_POR_CIDADE.keys()))
        produto = random.choice(PRODUTOS_POR_CIDADE[categoria])

        # Gerar cobertura aleatória ao redor do alvo da cidade
        cobertura = random.uniform(cobertura_min, cobertura_max)
        
        # Giro diário: 0.2 a 25
        if random.random() < 0.3:
            giro = random.uniform(0.1, 1.0)
        else:
            giro = random.lognormvariate(1.8, 0.9)
        giro = max(0.05, min(giro, 30.0))
        
        # Estoque = cobertura * giro
        estoque = int(round(cobertura * giro))
        estoque = max(0, min(estoque, 200))

        # IRC real calculado
        irc_real = max(0.0, 1.0 - cobertura / 14.0)

        # Risco
        risco = classificar_risco(irc_real)

        # Crítico: estoque baixo relativo ao giro (IRC > 0.40)
        critico = 1 if irc_real > 0.40 else 0

        registros.append({
            "regiao": cidade,
            "produto": produto,
            "categoria": categoria,
            "estoque_atual": estoque,
            "giro_diario": round(giro, 2),
            "cobertura_dias": round(cobertura, 2),
            "irc": round(irc_real, 4),
            "risco": risco,
            "critico": critico
        })

    return registros


def main():
    print("=" * 60)
    print("  ShadowTraffic Generator — Lojas Giovanna")
    print("=" * 60)

    all_registros = []

    print("\n[1/4] Gerando dados por cidade...")
    for cidade in CIDADES:
        regs = gerar_dados_cidade(cidade)
        all_registros.extend(regs)
        print(f"  {cidade}: {len(regs)} produtos")

    print(f"\nTotal de registros: {len(all_registros)}")

    # ─── Agregar por cidade para rupture_report.csv ──────────────────────────
    print("\n[2/4] Agregando por cidade...")
    df = pd.DataFrame(all_registros)

    agg = df.groupby("regiao").agg(
        qtd_produtos=("produto", "count"),
        estoque_total=("estoque_atual", "sum"),
        giro_medio=("giro_diario", "mean"),
        cobertura_media_dias=("cobertura_dias", "mean"),
        irc_medio=("irc", "mean"),
        qtd_critico=("critico", "sum"),
        pct_critico=("critico", "mean")
    ).reset_index()

    # Risco predominante baseado no IRC médio da cidade (não mode)
    agg["risco_predominante"] = agg["irc_medio"].apply(classificar_risco)

    agg["pct_critico"] = (agg["pct_critico"] * 100).round(2)
    agg["cobertura_media_dias"] = agg["cobertura_media_dias"].round(2)
    agg["giro_medio"] = agg["giro_medio"].round(2)
    agg["irc_medio"] = agg["irc_medio"].round(4)

    print(f"  {len(agg)} cidades agregadas")

    # ─── Salvar raw_data_shadowtraffic.json (registros detalhados) ───────────
    print("\n[3/4] Salvando raw_data_shadowtraffic.json...")
    raw_path = Path("data/raw_data_shadowtraffic.json")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_registros, f, indent=2, ensure_ascii=False)
    print(f"  {raw_path} ({len(all_registros)} registros)")

    # ─── Salvar rupture_report.csv (agregado por cidade) ─────────────────────
    print("\n[4/4] Salvando rupture_report.csv...")
    report_path = Path("data/rupture_report.csv")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(report_path, index=False, encoding="utf-8")
    print(f"  {report_path} ({len(agg)} cidades)")

    # ─── Estatísticas ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ESTATÍSTICAS GERAIS")
    print("=" * 60)
    print(f"  Cidades: {len(agg)}")
    print(f"  Produtos totais: {len(all_registros)}")
    print(f"  IRC médio geral: {agg['irc_medio'].mean():.2%}")
    print(f"  Cobertura média: {agg['cobertura_media_dias'].mean():.1f} dias")

    # Distribuição de risco
    risco_dist = agg["risco_predominante"].value_counts()
    print("\n  Distribuição de risco predominante:")
    for risco, count in risco_dist.items():
        print(f"    {risco}: {count}")

    # Top 10 IRC
    top10 = agg.nlargest(10, "irc_medio")
    print("\n  Top 10 cidades por IRC médio:")
    for i, row in top10.iterrows():
        print(f"    {row['regiao']}: {row['irc_medio']:.2%} ({row['risco_predominante']})")

    print("\n[OK] ShadowTraffic generation completo!")


if __name__ == "__main__":
    main()
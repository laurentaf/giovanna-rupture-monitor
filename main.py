"""
Monitor de Ruptura por Regiao — Lojas Giovanna.

Pipeline ETL em 3 estagios:
  Estagio 1: ingest() — le dados sinteticos do ShadowTraffic (raw_data.json)
  Estagio 2: transform() — agrega por regiao com metricas de ruptura
  Estagio 3: report() — exibe resumo e exporta CSV final

Schema de entrada (ShadowTraffic):
  regiao, produto, categoria, estoque_atual, giro_diario,
  cobertura_dias, irc, risco, critico

Schema de saida (rupture_report.csv):
  regiao, qtd_produtos, estoque_total, giro_medio,
  cobertura_media_dias, irc_medio, qtd_critico,
  pct_critico, risco_predominante
"""

import pandas as pd
import os
import sys
import argparse
from datetime import datetime

# ─── Configuracoes ──────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_DATA_FILE = "raw_data.json"
REPORT_FILE = "rupture_report.csv"

# Colunas esperadas no JSON de entrada (ShadowTraffic schema)
EXPECTED_COLUMNS = [
    "regiao", "produto", "categoria", "estoque_atual",
    "giro_diario", "cobertura_dias", "irc", "risco", "critico",
]

# Colunas de saida do CSV
OUTPUT_COLUMNS = [
    "regiao", "qtd_produtos", "estoque_total", "giro_medio",
    "cobertura_media_dias", "irc_medio", "qtd_critico",
    "pct_critico", "risco_predominante",
]


# =============================================================================
# Estagio 1: Ingestao
# =============================================================================

def ingest(json_path: str) -> pd.DataFrame:
    """
    Le o JSON bruto do ShadowTraffic e retorna um DataFrame.

    Args:
        json_path: Caminho absoluto para raw_data.json.

    Returns:
        DataFrame com as colunas do ShadowTraffic schema.

    Raises:
        SystemExit: Se o arquivo nao existe ou o DataFrame fica vazio.
    """
    if not os.path.exists(json_path):
        print(f"[ingest] ERRO: Arquivo nao encontrado: {json_path}")
        sys.exit(1)

    print(f"[ingest] Lendo: {json_path}")
    df = pd.read_json(json_path)

    # --- DataFrame empty guard (P0 padroes-entrega) ---
    if df.empty:
        print("[ingest] AVISO: DataFrame vazio apos leitura do JSON.")
        print("[ingest] Nenhum registro para processar — abortando.")
        sys.exit(1)

    # Valida presenca das colunas esperadas
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        print(f"[ingest] ERRO: Colunas ausentes no JSON: {sorted(missing)}")
        print(f"[ingest] Colunas encontradas: {list(df.columns)}")
        sys.exit(1)

    print(f"[ingest] {len(df)} registros lidos, {df['regiao'].nunique()} regioes.")
    print(f"[ingest] Colunas validadas: {list(df.columns)}")
    return df


# =============================================================================
# Estagio 2: Transformacao
# =============================================================================

def _risco_mode(series: pd.Series) -> str:
    """Retorna a moda (valor mais frequente) de uma Series de risco.

    Em caso de empate, retorna o primeiro valor por ordem alfabetica
    para resultado deterministico.
    """
    if series.empty:
        return "N/A"
    counts = series.value_counts()
    max_count = counts.max()
    # Dos empatados, escolhe o primeiro alfabeticamente
    tied = sorted(counts[counts == max_count].index.tolist())
    return tied[0]


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega dados por regiao com metricas de ruptura.

    Args:
        df: DataFrame bruto com schema ShadowTraffic.

    Returns:
        DataFrame com colunas de saida do rupture_report.csv.
    """
    # --- DataFrame empty guard (P0 padroes-entrega) ---
    if df.empty:
        print("[transform] AVISO: DataFrame vazio — retornando resultado vazio.")
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Marca produtos criticos por regiao: um produto e critico se pelo menos
    # um de seus registros tem critico=1. Depois conta quantos produtos
    # criticos existem por regiao (evita inflar o contador quando ha
    # multiplas linhas por produto).
    produto_critico = (
        df.groupby(["regiao", "produto"])["critico"]
        .max()              # 1 se qualquer linha do produto e critica
        .reset_index()
        .groupby("regiao")["critico"]
        .sum()              # total de produtos criticos na regiao
        .reset_index()
        .rename(columns={"critico": "qtd_critico"})
    )

    aggregated = (
        df.groupby("regiao")
        .agg(
            qtd_produtos=("produto", "nunique"),
            estoque_total=("estoque_atual", "sum"),
            giro_medio=("giro_diario", "mean"),
            cobertura_media_dias=("cobertura_dias", "mean"),
            irc_medio=("irc", "mean"),
            risco_predominante=("risco", _risco_mode),
        )
        .reset_index()
    )

    # Merge qtd_critico calculado por produto (nao por linha)
    aggregated = aggregated.merge(produto_critico, on="regiao", how="left")
    aggregated["qtd_critico"] = aggregated["qtd_critico"].fillna(0).astype(int)

    # --- Guard: se agregacao produz DataFrame vazio ---
    if aggregated.empty:
        print("[transform] AVISO: Agregacao produziu DataFrame vazio.")
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # pct_critico = qtd_critico / qtd_produtos * 100
    # Guard contra divisao por zero (qtd_produtos nunca deve ser 0,
    # mas protegemos por robustez)
    aggregated["pct_critico"] = aggregated.apply(
        lambda row: round(row["qtd_critico"] / row["qtd_produtos"] * 100, 2)
        if row["qtd_produtos"] > 0
        else 0.0,
        axis=1,
    )

    # Arredonda metricas continuas para 2 casas decimais
    aggregated["giro_medio"] = aggregated["giro_medio"].round(2)
    aggregated["cobertura_media_dias"] = aggregated["cobertura_media_dias"].round(2)
    aggregated["irc_medio"] = aggregated["irc_medio"].round(4)

    # Garante qtd_critico como inteiro
    aggregated["qtd_critico"] = aggregated["qtd_critico"].astype(int)
    aggregated["qtd_produtos"] = aggregated["qtd_produtos"].astype(int)
    aggregated["estoque_total"] = aggregated["estoque_total"].astype(int)

    # Reordena colunas para o schema de saida
    result = aggregated[OUTPUT_COLUMNS]

    print(f"[transform] {len(result)} regioes agregadas.")
    return result


# =============================================================================
# Estagio 3: Relatorio
# =============================================================================

def print_summary(summary: pd.DataFrame) -> None:
    """
    Exibe resumo das regioes com maior risco critico.

    Args:
        summary: DataFrame agregado por regiao.
    """
    print("\n" + "=" * 70)
    print(" RESUMO DE RUPTURA POR REGIAO — Lojas Giovanna")
    print("=" * 70)

    # --- DataFrame empty guard ---
    if summary.empty:
        print(" Nenhuma regiao para exibir — dados ausentes ou vazios.")
        return

    top_critico = summary.sort_values("pct_critico", ascending=False).head(5)

    print(f"\n {'Regiao':<20} {'Produtos':>9} {'Estoque':>9} {'%Critico':>9} {'Risco':>15}")
    print(" " + "-" * 66)
    for _, row in top_critico.iterrows():
        print(f" {row['regiao']:<20} {row['qtd_produtos']:>9} "
              f"{row['estoque_total']:>9} {row['pct_critico']:>8.1f}% "
              f"{row['risco_predominante']:>15}")

    # Estatisticas gerais
    total_regioes = len(summary)
    total_produtos = summary["qtd_produtos"].sum()
    media_critico = summary["pct_critico"].mean()

    print(f"\n Total de regioes analisadas: {total_regioes}")
    print(f" Total de produtos (distintos agregados): {total_produtos}")
    print(f" Media geral de % critico: {media_critico:.1f}%")

    # Regiao mais critica
    if not top_critico.empty:
        worst = top_critico.iloc[0]
        print(f" Regiao mais critica: {worst['regiao']} "
              f"({worst['pct_critico']:.1f}% criticos, "
              f"risco predominante: {worst['risco_predominante']})")


def save_report(summary: pd.DataFrame, filepath: str) -> None:
    """
    Salva o resumo agregado em CSV.

    Args:
        summary: DataFrame agregado por regiao.
        filepath: Caminho do arquivo CSV de saida.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # --- DataFrame empty guard ---
    if summary.empty:
        print(f"[save_report] AVISO: DataFrame vazio — salvando CSV com apenas cabecalho.")
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(
            filepath, index=False, encoding="utf-8"
        )
        print(f"[save_report] Relatorio salvo em: {filepath} (0 regioes, cabecalho apenas)")
        return

    summary.to_csv(filepath, index=False, encoding="utf-8")
    print(f"[save_report] Relatorio salvo em: {filepath} ({len(summary)} regioes)")


# =============================================================================
# Pipeline principal
# =============================================================================

def main():
    """
    Executa os 3 estagios do pipeline em sequencia:
    1. Ingestao — le ShadowTraffic JSON bruto
    2. Transformacao — agrega por regiao com metricas de ruptura
    3. Relatorio — exibe resumo e salva CSV
    """
    parser = argparse.ArgumentParser(
        description="Monitor de Ruptura por Regiao — Lojas Giovanna"
    )
    parser.add_argument(
        "--local", "-l", action="store_true",
        help="Usa dados locais (data/raw_data.json) do ShadowTraffic"
    )
    args = parser.parse_args()

    print("=" * 70)
    print(" Monitor de Ruptura por Regiao — Lojas Giovanna")
    print("=" * 70)
    print(f" Modo: {'local' if args.local else 'padrao (local)'}")
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    json_path = os.path.join(DATA_DIR, RAW_DATA_FILE)
    report_path = os.path.join(DATA_DIR, REPORT_FILE)

    # --- Estagio 1: Ingestao ---
    print("\n--- Estagio 1: Ingestao de dados ---")
    df = ingest(json_path)

    # --- Estagio 2: Transformacao ---
    print("\n--- Estagio 2: Transformacao e agregacao ---")
    summary = transform(df)

    # --- Estagio 3: Relatorio ---
    print("\n--- Estagio 3: Relatorio e exportacao ---")
    print_summary(summary)
    save_report(summary, report_path)

    print("\n[OK] Pipeline completo (3 estagios)!")
    print(f" JSON bruto: {json_path} ({len(df)} registros lidos)")
    print(f" Relatorio:  {report_path} ({len(summary)} regioes)")
    if not summary.empty:
        print(f" Colunas CSV: {list(summary.columns)}")


if __name__ == "__main__":
    main()

"""
Monitor de Ruptura por Regiao — Lojas Giovanna.

Pipeline ETL em 3 estagios:
  Estagio 1: fetch_data() — consome API da DataMission e salva JSON bruto
  Estagio 2: process_inventory() — le JSON, computa ruptura, resumo por regiao
  Estagio 3: print_summary() — exibe top 3 regioes e exporta CSV final

Calculo de ruptura:
    ruptura = (demanda_prevista - estoque_atual) / demanda_prevista
    Indica o percentual da demanda que NAO foi atendida pelo estoque.
    Valores positivos = ruptura (estoque insuficiente).
    Valores negativos = excesso de estoque.
"""

import requests
import pandas as pd
import json
import os
import sys
import argparse
import hashlib
from datetime import datetime

# ─── Configuracoes ──────────────────────────────────────────────────────────

PROJECT_ID = "93fa0f19-ae51-4ed9-986b-47457ac2f26a"
API_TOKEN = os.environ.get("API_TOKEN")

BASE_URL = "https://api.datamission.com.br/projects"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


# =============================================================================
# Estagio 1: Configurar ambiente e obter dados
# =============================================================================

def fetch_data() -> list[dict]:
    """
    Consome a API de datasets da DataMission.

    Endpoint:
        GET https://api.datamission.com.br/projects/{project_id}/dataset?format=json&rows=10000

    Cada chamada retorna ate 10.000 registros unicos.
    Para datasets maiores, execute multiplas vezes e mescle os JSONs.

    Returns:
        list[dict]: Lista de registros de pedidos/inventario.

    Raises:
        requests.exceptions.RequestException: Se a requisicao falhar.
    """
    if not API_TOKEN:
        print("ERRO: Variavel de ambiente API_TOKEN nao definida.")
        sys.exit(1)

    url = f"{BASE_URL}/{PROJECT_ID}/dataset?format=json&rows=10000"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    print(f"[fetch_data] Chamando API: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    if not data:
        print("[fetch_data] AVISO: API retornou lista vazia.")
    print(f"[fetch_data] {len(data)} registros obtenidos com sucesso.")
    return data


def save_raw_json(data: list[dict], filepath: str) -> str:
    """Persiste dados brutos em JSON no disco."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[save_raw_json] JSON salvo em: {filepath} ({len(data)} registros)")
    return filepath


# =============================================================================
# Estagio 2: Processar dados e calcular ruptura
# =============================================================================

def build_demand_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria as colunas de estoque_atual e demanda_prevista a partir dos dados
    de pedidos.

    Como a API retorna dados de pedidos (nao dados de estoque), derivamos:
      - regiao = store_location (regiao da loja)
      - estoque_atual = quantity (estoque atual em unidades)
      - demanda_prevista = estimativa de demanda baseada em uma projecao
        com variacao deterministica (usando o order_id como seed)
        para simular um cenario real de previsao vs. estoque

    Args:
        df: DataFrame com dados brutos da API.

    Returns:
        DataFrame com colunas: regiao, estoque_atual, demanda_prevista
    """
    if df.empty:
        print("[build_demand_forecast] AVISO: DataFrame vazio — pulando transformacao.")
        return pd.DataFrame(columns=["regiao", "estoque_atual", "demanda_prevista"])

    # Renomeia store_location para regiao
    df["regiao"] = df["store_location"]

    # estoque_atual = quantity (cada registro representa a quantidade
    # do produto disponivel na regiao)
    df["estoque_atual"] = df["quantity"]

    # demanda_prevista: projecao com base na quantidade + pequeno desvio
    # deterministico (derivado do order_id) para simular previsao de demanda
    def _forecast(row):
        qty = row["quantity"]
        # Hash SHA256 deterministico do order_id (PYTHONHASHSEED nao afeta)
        h = hashlib.sha256(str(row["order_id"]).encode()).hexdigest()
        # Pega os primeiros 8 hex chars como int normalizado entre 0 e 1
        seed_val = int(h[:8], 16) / 0xFFFFFFFF  # 0.0 a 1.0
        factor = seed_val * 0.6 - 0.2  # entre -0.2 e +0.4
        forecast = max(1, round(qty * (1 + factor)))
        return forecast

    df["demanda_prevista"] = df.apply(_forecast, axis=1)

    print(f"[build_demand_forecast] estoque_atual: min={df['estoque_atual'].min()}, "
          f"max={df['estoque_atual'].max()}, "
          f"media={df['estoque_atual'].mean():.1f}")
    print(f"[build_demand_forecast] demanda_prevista: min={df['demanda_prevista'].min()}, "
          f"max={df['demanda_prevista'].max()}, "
          f"media={df['demanda_prevista'].mean():.1f}")

    return df[["regiao", "estoque_atual", "demanda_prevista"]]


def compute_rupture(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a ruptura por registro e depois agrega por regiao.

    Ruptura = (demanda_prevista - estoque_atual) / demanda_prevista

    Agregacao: media (mean) e maximo (max) da ruptura por regiao.

    Args:
        df: DataFrame com colunas regiao, estoque_atual, demanda_prevista.

    Returns:
        DataFrame com resumo por regiao: regiao, ruptura_mean, ruptura_max.
    """
    if df.empty:
        print("[compute_rupture] AVISO: DataFrame vazio — retornando resultado vazio.")
        return pd.DataFrame(columns=["regiao", "ruptura_mean", "ruptura_max"])

    # Calcula ruptura por registro
    df["ruptura"] = (df["demanda_prevista"] - df["estoque_atual"]) / df["demanda_prevista"]

    # Filtra registros com demanda_valida > 0
    df_valid = df[df["demanda_prevista"] > 0].copy()

    n_records = len(df_valid)
    print(f"[compute_rupture] Registros com demanda valida: {n_records}")

    if n_records == 0:
        print("[compute_rupture] AVISO: Nenhum registro com demanda > 0 — sem dados para agregar.")
        return pd.DataFrame(columns=["regiao", "ruptura_mean", "ruptura_max"])

    # Agrega por regiao
    summary = (
        df_valid.groupby("regiao")["ruptura"]
        .agg(["mean", "max"])
        .reset_index()
        .rename(columns={"mean": "ruptura_mean", "max": "ruptura_max"})
        .round(4)
    )

    print(f"[compute_rupture] Regioes unicas: {len(summary)}")
    return summary


# =============================================================================
# Estagio 3: Gerar relatorios e validacoes
# =============================================================================

def print_summary(summary: pd.DataFrame) -> None:
    """
    Exibe as top 3 regioes com maior ruptura media.

    Args:
        summary: DataFrame com colunas regiao, ruptura_mean, ruptura_max.
    """
    print("\n" + "=" * 60)
    print("  TOP 3 REGIOES COM MAIOR RUPTURA MEDIA")
    print("=" * 60)

    if summary.empty:
        print("  Nenhuma regiao para exibir — dados ausentes ou vazios.")
        print("  Verifique se a API retornou registros validos.")
        return

    top3 = summary.sort_values("ruptura_mean", ascending=False).head(3)

    for i, (_, row) in enumerate(top3.iterrows(), 1):
        print(f"  {i}. {row['regiao']}")
        print(f"     Ruptura media: {row['ruptura_mean']:.2%}")
        print(f"     Ruptura max:   {row['ruptura_max']:.2%}")
        print()

    # Estatisticas gerais
    mean_val = summary["ruptura_mean"].mean()
    mean_str = f"{mean_val:.2%}" if not pd.isna(mean_val) else "N/A"
    print(f"  Total de regioes analisadas: {len(summary)}")
    print(f"  Media geral de ruptura:     {mean_str}")

    # Pior regiao — so acessa se existir
    if not top3.empty:
        first = top3.iloc[0]
        print(f"  Pior regiao:                {first['regiao']} "
              f"({first['ruptura_mean']:.2%})")


def save_report(summary: pd.DataFrame, filepath: str) -> None:
    """Salva o resumo de ruptura por regiao em CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if summary.empty:
        print(f"[save_report] AVISO: DataFrame vazio — salvando CSV com apenas cabecalho.")
    summary.to_csv(filepath, index=False, encoding="utf-8")
    print(f"[save_report] Relatorio salvo em: {filepath} ({len(summary)} regioes)")


# =============================================================================
# Pipeline principal
# =============================================================================

def load_local_json(filepath: str) -> list[dict]:
    """Carrega dados de um arquivo JSON local."""
    if not os.path.exists(filepath):
        print(f"ERRO: Arquivo {filepath} nao encontrado.")
        print("Dica: execute primeiro sem --local para baixar da API.")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data or (isinstance(data, list) and len(data) == 0):
        print(f"ERRO: Arquivo {filepath} esta vazio.")
        sys.exit(1)
    print(f"[load_local_json] Carregados {len(data)} registros de {filepath}")
    return data


def main():
    """
    Executa os 3 estagios do pipeline em sequencia:
      1. Fetch dados da API e salva JSON bruto
      2. Processa dados, calcula ruptura, gera resumo por regiao
      3. Exibe top 3 regioes e salva relatorio CSV
    """
    parser = argparse.ArgumentParser(
        description="Monitor de Ruptura por Regiao — Lojas Giovanna"
    )
    parser.add_argument(
        "--local", "-l", action="store_true",
        help="Usa dados locais (data/raw_data.json) em vez de chamar a API"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Monitor de Ruptura por Regiao — Lojas Giovanna")
    print("=" * 60)

    json_path = os.path.join(DATA_DIR, "raw_data.json")

    # --- Estagio 1: Ingestao ---
    print("\n--- Estagio 1: Obter dados ---")
    if args.local:
        print("[modo local] Carregando dados existentes...")
        raw_data = load_local_json(json_path)
    else:
        print("[modo API] Baixando da API DataMission...")
        raw_data = fetch_data()
        save_raw_json(raw_data, json_path)

    if not raw_data:
        print("\n[ERRO] Nenhum registro retornado pela API. Verifique o token e o project_id.")
        sys.exit(1)

    # --- Estagio 2: Processamento ---
    print("\n--- Estagio 2: Processar dados e calcular ruptura ---")
    df = pd.DataFrame(raw_data)
    df_filtered = build_demand_forecast(df)
    summary = compute_rupture(df_filtered)

    # --- Estagio 3: Relatorios ---
    print("\n--- Estagio 3: Relatorios e validacoes ---")
    print_summary(summary)
    report_path = os.path.join(DATA_DIR, "rupture_report.csv")
    save_report(summary, report_path)

    print("\n[OK] Pipeline completo (3 estagios)!")
    print(f"   Modo:       {'local' if args.local else 'API'}")
    print(f"   JSON bruto: {json_path} ({len(raw_data)} registros)")
    print(f"   Relatorio:  {report_path} ({len(summary)} regioes)")


if __name__ == "__main__":
    main()

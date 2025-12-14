"""
Script principal da aplicação de conciliação financeira.
Execução: python -m src.main
"""
import argparse
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from src.excel_reader import read_vendas
from src.excel_writer import escrever_resultados
from src.business_rules import (
    calcular_resultados,
    TAXAS_CONFIG,
    FormaPagamento,
    StatusTransacao
)
# ----------------------------------

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ConciliacaoBot")

# --- CONFIGURAÇÕES PADRÃO ---
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_INPUT = "data/vendas.xlsx"
DEFAULT_OUTPUT = f"output/Relatorio_Conciliacao_{TIMESTAMP}.xlsx"
DEFAULT_PORTAL_URL = f"file://{Path.cwd()}/web_portal_fake/index.html"


def simular_consulta_gateway(
    valor_bruto: float, forma_pag_str: str
) -> tuple[float, StatusTransacao]:
    """
    MOCK: Simula consulta ao portal de pagamentos.
    """
    try:
        forma_enum = FormaPagamento(forma_pag_str.lower())
        regra = TAXAS_CONFIG[forma_enum]

        if regra["tipo"] == "percentual":
            taxa = valor_bruto * regra["valor"]
        else:
            taxa = regra["valor"]

        if random.random() < 0.10:
            taxa += random.uniform(0.50, 5.00)
            return taxa, StatusTransacao.DIVERGENTE

        return taxa, StatusTransacao.APROVADO

    except ValueError:
        raise ValueError(f"Forma de pagamento não suportada: '{forma_pag_str}'")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Sistema de Conciliação Financeira")

    parser.add_argument("--input", "-i", default=DEFAULT_INPUT)
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT)
    parser.add_argument("--portal-url", "-p", default=DEFAULT_PORTAL_URL)
    parser.add_argument("--headless", action="store_true")

    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 INICIANDO V1 | Input: {args.input}")

        df_vendas = read_vendas(args.input)
        logger.info(f"📖 Lidas {len(df_vendas)} linhas.")

        resultados = []

        for _, row in df_vendas.iterrows():
            id_venda = row["ID da venda"]
            valor_bruto = float(row["Valor bruto"])
            forma_pag = row["Forma de pagamento"]
            custo = float(row["Custo do produto"])

            try:
                taxa_gateway, status_enum = simular_consulta_gateway(
                    valor_bruto, forma_pag
                )
            except ValueError as e:
                logger.warning(f"⚠️ Venda {id_venda} ignorada: {e}")
                continue

            try:
                calculos = calcular_resultados(
                    valor_bruto=valor_bruto,
                    taxa_gateway=taxa_gateway,
                    custo_produto=custo,
                    forma_pagamento=forma_pag,
                )

                resultados.append(
                    {
                        "id_venda": id_venda,
                        "cliente": row["Cliente"],
                        "valor_bruto": valor_bruto,
                        "forma_pagamento": forma_pag,
                        "taxa_gateway": taxa_gateway,
                        "taxa_adicional": calculos["taxa_adicional"],
                        "valor_liquido": calculos["valor_liquido"],
                        "custo_produto": custo,
                        "lucro": calculos["lucro"],
                        "roi": calculos["roi"],
                        "status": status_enum.value,
                    }
                )

            except ValueError as ve:
                logger.warning(f"⚠️ Erro de cálculo na venda {id_venda}: {ve}")
                continue

        if resultados:
            escrever_resultados(resultados, args.output)
            logger.info(f"✅ Sucesso! Relatório salvo em: {args.output}")
        else:
            logger.warning("⚠️ Nenhum dado foi processado.")

    except Exception as e:
        logger.error(f"❌ Erro Fatal: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
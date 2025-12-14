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

# Imports absolutos (funcionam nativamente com python -m src.main)
from src.excel_reader import read_vendas
from src.business_rules import calcular_resultados, escrever_resultados, TAXAS_CONFIG, FormaPagamento

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ConciliacaoBot")

# --- CONFIGURAÇÕES PADRÃO ---
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
# Caminhos relativos ao diretório de execução (raiz do projeto)
DEFAULT_INPUT = "data/vendas.xlsx"
DEFAULT_OUTPUT = f"output/Relatorio_Conciliacao_{TIMESTAMP}.xlsx"
# Ajuste para URL funcionar em qualquer OS
DEFAULT_PORTAL_URL = f"file://{Path.cwd()}/web_portal_fake/index.html"


def simular_consulta_gateway(valor_bruto: float, forma_pag_str: str) -> tuple[float, str]:
    """
    MOCK: Simula a consulta ao portal de pagamentos.
    Retorna (taxa_gateway_simulada, status_simulado).
    Usa a Single Source of Truth (TAXAS_CONFIG) como base.
    """
    try:
        # 1. Normalizar e buscar regra oficial
        forma_enum = FormaPagamento(forma_pag_str.lower())
        regra = TAXAS_CONFIG[forma_enum]
        
        # 2. Calcular Baseline (O valor 'correto')
        if regra["tipo"] == "percentual":
            taxa_simulada = valor_bruto * regra["valor"]
        else: # fixo
            taxa_simulada = regra["valor"]

        # 3. Introduzir Ruído/Erro (Simulação de Realidade)
        # 10% de chance de erro no gateway
        if random.random() < 0.10: 
            erro = random.uniform(0.50, 5.00)
            taxa_simulada += erro
            return taxa_simulada, "PENDENTE (Divergência)"
        
        return taxa_simulada, "APROVADO"

    except ValueError:
        # Fallback para tipos desconhecidos no Enum
        return 0.0, "ERRO: TIPO DESCONHECIDO"


def parse_arguments():
    """Processa argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Sistema de Conciliação Financeira")
    
    parser.add_argument('--input', '-i', default=DEFAULT_INPUT, help='Arquivo de entrada')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT, help='Arquivo de saída')
    parser.add_argument('--portal-url', '-p', default=DEFAULT_PORTAL_URL, help='URL do portal')
    parser.add_argument('--headless', action='store_true', help='Modo headless')
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    try:
        # Garantir diretório de saída
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 INICIANDO V1 | Input: {args.input}")

        # 1. LEITURA
        df_vendas = read_vendas(args.input)
        logger.info(f"📖 Lidas {len(df_vendas)} linhas.")
        
        # 2. PROCESSAMENTO
        resultados = []
        
        # Futuro: with PortalPagamentosClient(...) as portal:
        
        for idx, row in df_vendas.iterrows():
            # Extrair dados da linha
            id_venda = row['ID da venda']
            val_bruto = float(row['Valor bruto'])
            forma_pag = row['Forma de pagamento']
            custo = float(row['Custo do produto'])

            # --- CHAMADA DO MOCK (Isolada) ---
            # No futuro, aqui entra: portal.consultar_transacao(id_venda)
            taxa_gateway, status = simular_consulta_gateway(val_bruto, forma_pag)
            
            if status == "ERRO: TIPO DESCONHECIDO":
                logger.warning(f"⚠️ Pula venda {id_venda}: Tipo {forma_pag} inválido.")
                continue

            try:
                # Regras de Negócio (Cálculo Real)
                calculos = calcular_resultados(
                    valor_bruto=val_bruto,
                    taxa_gateway=taxa_gateway,
                    custo_produto=custo,
                    forma_pagamento=forma_pag
                )

                resultados.append({
                    'id_venda': id_venda,
                    'cliente': row['Cliente'],
                    'valor_bruto': val_bruto,
                    'forma_pagamento': forma_pag,
                    'taxa_gateway': taxa_gateway,
                    'taxa_adicional': calculos['taxa_adicional'],
                    'valor_liquido': calculos['valor_liquido'],
                    'custo_produto': custo,
                    'lucro': calculos['lucro'],
                    'roi': calculos['roi'],
                    'status': status
                })

            except ValueError as ve:
                logger.warning(f"⚠️ Erro cálculo {id_venda}: {ve}")
                continue

        # 3. RELATÓRIO
        if resultados:
            escrever_resultados(resultados, args.output)
            logger.info(f"✅ Sucesso! Relatório em: {args.output}")
        else:
            logger.warning("⚠️ Nenhum dado processado.")

    except Exception as e:
        logger.error(f"❌ Erro Fatal: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
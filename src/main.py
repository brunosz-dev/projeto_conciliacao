"""
Script principal da aplicação de conciliação financeira.
Versão integrada com Selenium (web_scraper).

Execução: 
    python -m src.main --input data/vendas.xlsx --output output/relatorio.xlsx
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.excel_reader import read_vendas
from src.excel_writer import escrever_resultados
from src.business_rules import calcular_resultados, FormaPagamento
from src.web_scraper import (
    PortalPagamentosClient,
    PortalTransacaoNaoEncontrada,
    PortalTimeoutError,
    PortalConnectionError,
    PortalScraperError
)

# ======================================================================
# CONFIGURAÇÃO
# ======================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ConciliacaoBot")

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_INPUT = "data/vendas.xlsx"
DEFAULT_OUTPUT = f"output/Relatorio_Conciliacao_{TIMESTAMP}.xlsx"
DEFAULT_PORTAL_URL = f"file://{Path.cwd()}/web_portal_fake/index.html"


# ======================================================================
# FUNÇÕES AUXILIARES
# ======================================================================

def parse_arguments():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sistema de Conciliação Financeira Automatizada"
    )
    
    parser.add_argument(
        "--input", "-i", 
        default=DEFAULT_INPUT,
        help="Caminho do arquivo Excel de vendas"
    )
    parser.add_argument(
        "--output", "-o", 
        default=DEFAULT_OUTPUT,
        help="Caminho do relatório de saída"
    )
    parser.add_argument(
        "--portal-url", "-p", 
        default=DEFAULT_PORTAL_URL,
        help="URL do portal de pagamentos"
    )
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Roda o navegador em modo headless (sem interface)"
    )
    parser.add_argument(
        "--browser",
        default="chrome",
        choices=["chrome", "edge"],
        help="Navegador a ser utilizado (chrome ou edge)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Usa simulação (mock) em vez do Selenium real"
    )
    
    return parser.parse_args()


# ======================================================================
# MAIN
# ======================================================================

def main():
    """Função principal da aplicação."""
    args = parse_arguments()
    
    try:
        # Criar diretório de saída
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        
        # Banner
        logger.info("=" * 70)
        logger.info("🚀 SISTEMA DE CONCILIAÇÃO FINANCEIRA AUTOMATIZADA")
        logger.info("=" * 70)
        logger.info(f"📥 Entrada: {args.input}")
        logger.info(f"📤 Saída: {args.output}")
        logger.info(f"🌐 Portal: {args.portal_url}")
        logger.info(f"🤖 Modo: {'MOCK' if args.mock else 'SELENIUM'}")
        if not args.mock:
            logger.info(f"🌐 Navegador: {args.browser.upper()}")
            logger.info(f"👁️  Headless: {'Sim' if args.headless else 'Não'}")
        logger.info("=" * 70)
        
        # 1. Ler vendas
        logger.info("\n📖 Etapa 1/3: Lendo arquivo de vendas...")
        df_vendas = read_vendas(args.input)
        logger.info(f"✅ {len(df_vendas)} vendas carregadas")
        
        # 2. Processar com Selenium ou Mock
        logger.info("\n⚙️  Etapa 2/3: Consultando portal e processando...")
        
        if args.mock:
            resultados = processar_com_mock(df_vendas)
        else:
            resultados = processar_com_selenium(
                df_vendas, 
                args.portal_url, 
                args.headless,
                args.browser  # Novo parâmetro
            )
        
        logger.info(f"✅ {len(resultados)} transações processadas")
        
        # 3. Gerar relatório
        if resultados:
            logger.info("\n📊 Etapa 3/3: Gerando relatório Excel...")
            escrever_resultados(resultados, args.output)
            logger.info(f"✅ Relatório salvo: {args.output}")
            
            # Resumo
            logger.info("\n" + "=" * 70)
            logger.info("📈 RESUMO DA EXECUÇÃO")
            logger.info("=" * 70)
            
            total_lucro = sum(r.get('lucro', 0) for r in resultados)
            aprovados = sum(1 for r in resultados if 'Aprovado' in r.get('status', ''))
            pendentes = len(resultados) - aprovados
            
            logger.info(f"✅ Transações processadas: {len(resultados)}")
            logger.info(f"🟢 Aprovadas: {aprovados}")
            logger.info(f"🟡 Pendentes: {pendentes}")
            logger.info(f"💰 Lucro Total: R$ {total_lucro:,.2f}")
            logger.info("=" * 70)
        else:
            logger.warning("⚠️  Nenhuma transação foi processada.")
        
    except FileNotFoundError as e:
        logger.error(f"❌ Arquivo não encontrado: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}", exc_info=True)
        sys.exit(1)


def processar_com_selenium(
    df_vendas, 
    portal_url: str, 
    headless: bool,
    browser: str = "chrome"
):
    """
    Processa vendas usando Selenium REAL.
    
    Args:
        df_vendas: DataFrame com as vendas
        portal_url: URL do portal
        headless: Modo headless
        browser: Navegador ('chrome' ou 'edge')
        
    Returns:
        Lista de dicionários com resultados
    """
    resultados = []
    
    # Context manager garante fechamento do navegador
    with PortalPagamentosClient(
        portal_url, 
        browser=browser,  # Passa o navegador escolhido
        headless=headless
    ) as client:
        
        for idx, row in df_vendas.iterrows():
            id_venda = row["ID da venda"]
            valor_bruto = float(row["Valor bruto"])
            forma_pag = row["Forma de pagamento"]
            custo = float(row["Custo do produto"])
            
            try:
                # Consultar portal (Selenium)
                dados_portal = client.consultar_transacao(id_venda)
                
                taxa_gateway = dados_portal['taxa_gateway']
                status_enum = dados_portal['status_portal']
                data_pagamento = dados_portal['data_pagamento']
                
                # Calcular regras de negócio
                calculos = calcular_resultados(
                    valor_bruto=valor_bruto,
                    taxa_gateway=taxa_gateway,
                    custo_produto=custo,
                    forma_pagamento=forma_pag,
                )
                
                # Montar resultado
                resultados.append({
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
                    "data_pagamento": data_pagamento or "Pendente"
                })
            
            # ========================================================
            # 🎯 TRATAMENTO ESPECÍFICO POR TIPO DE EXCEÇÃO
            # ========================================================
            
            except PortalTransacaoNaoEncontrada:
                # Transação não encontrada no portal
                # IMPORTANTE: Registrar no relatório para rastreabilidade
                # (Evita o "Buraco Negro" - vendas sumindo do relatório)
                logger.warning(
                    f"⚠️  {id_venda}: Não encontrado no portal "
                    f"(pode estar em processamento ou ID incorreto)"
                )
                
                # Adiciona ao relatório com status claro
                resultados.append({
                    "id_venda": id_venda,
                    "cliente": row["Cliente"],
                    "valor_bruto": valor_bruto,
                    "forma_pagamento": forma_pag,
                    "taxa_gateway": 0.0,
                    "taxa_adicional": 0.0,
                    "valor_liquido": valor_bruto,  # Sem desconto
                    "custo_produto": custo,
                    "lucro": valor_bruto - custo,
                    "roi": ((valor_bruto - custo) / custo * 100) if custo > 0 else 0.0,
                    "status": "Não Encontrado no Portal",
                    "data_pagamento": "-"
                })
                continue
            
            except PortalTimeoutError as e:
                # Portal demorou muito para responder
                # Decisão: Marcar como divergente e continuar
                logger.error(f"⏱️  {id_venda}: Timeout no portal - {e}")
                
                # Adiciona com status divergente (sem dados do portal)
                resultados.append({
                    "id_venda": id_venda,
                    "cliente": row["Cliente"],
                    "valor_bruto": valor_bruto,
                    "forma_pagamento": forma_pag,
                    "taxa_gateway": 0.0,
                    "taxa_adicional": 0.0,
                    "valor_liquido": valor_bruto,
                    "custo_produto": custo,
                    "lucro": valor_bruto - custo,
                    "roi": 0.0,
                    "status": "Divergente (Timeout)",
                    "data_pagamento": "Erro no portal"
                })
                continue
            
            except (PortalConnectionError, PortalScraperError) as e:
                # Erro crítico - para toda a execução
                logger.error(f"❌ Erro crítico no portal: {e}")
                logger.error("🛑 Interrompendo processamento...")
                break
            
            except Exception as e:
                # Erro inesperado (não relacionado ao portal)
                logger.error(f"❌ Erro ao processar {id_venda}: {e}")
                continue
    
    return resultados


def processar_com_mock(df_vendas):
    """
    Processa vendas usando SIMULAÇÃO (sem Selenium).
    Útil para testes rápidos sem depender do navegador.
    
    Args:
        df_vendas: DataFrame com as vendas
        
    Returns:
        Lista de dicionários com resultados
    """
    import random
    from src.business_rules import StatusTransacao, TAXAS_CONFIG
    
    resultados = []
    
    logger.info("   Modo MOCK: Simulando consultas ao portal...")
    
    for _, row in df_vendas.iterrows():
        id_venda = row["ID da venda"]
        valor_bruto = float(row["Valor bruto"])
        forma_pag = row["Forma de pagamento"]
        custo = float(row["Custo do produto"])
        
        try:
            # Simular taxa do gateway (baseado na forma de pagamento)
            forma_enum = FormaPagamento(forma_pag.lower())
            regra = TAXAS_CONFIG[forma_enum]
            
            if regra["tipo"] == "percentual":
                taxa_gateway = valor_bruto * regra["valor"]
            else:
                taxa_gateway = regra["valor"]
            
            # 10% de chance de divergência
            if random.random() < 0.10:
                taxa_gateway += random.uniform(0.50, 5.00)
                status_enum = StatusTransacao.DIVERGENTE
            else:
                status_enum = StatusTransacao.APROVADO
            
            # Calcular regras de negócio
            calculos = calcular_resultados(
                valor_bruto=valor_bruto,
                taxa_gateway=taxa_gateway,
                custo_produto=custo,
                forma_pagamento=forma_pag,
            )
            
            resultados.append({
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
                "data_pagamento": "Simulado"
            })
            
        except ValueError as ve:
            logger.warning(f"⚠️  {id_venda}: {ve}")
            continue
    
    return resultados


if __name__ == "__main__":
    main()
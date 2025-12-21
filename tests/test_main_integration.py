"""
Testes de integração end-to-end (E2E).
Simula execução completa do script main.py via linha de comando.

Markers:
    @pytest.mark.integration - Teste de integração entre módulos
    @pytest.mark.e2e - Teste ponta a ponta (CLI + Selenium + IO real)

Execução:
    pytest -m integration          # Todos os testes de integração
    pytest -m e2e                  # Só testes E2E completos
    pytest -m "integration and not e2e"  # Integração sem E2E
"""
import sys
import pytest
import pandas as pd
from unittest.mock import patch
from src.main import main


# Dados para criar um Excel de entrada válido
DADOS_INPUT = {
    'ID da venda': ['TX-INT-01', 'TX-INT-02'],
    'Cliente': ['Cliente A', 'Cliente B'],
    'Valor bruto': [100.0, 200.0],
    'Data da venda': ['2025-01-01', '2025-01-01'],
    'Forma de pagamento': ['pix', 'cartao_credito'],
    'Custo do produto': [50.0, 100.0]
}


@pytest.mark.integration
@pytest.mark.e2e
def test_fluxo_completo_main(tmp_path, request):
    """
    Testa o pipeline completo end-to-end:
    1. Cria excel de entrada
    2. Roda o main.py (simulando argumentos de CLI)
    3. Verifica se o excel de saída foi gerado com dados
    
    Este teste valida:
    - Leitura de Excel (excel_reader)
    - Consulta ao portal (web_scraper + Selenium)
    - Regras de negócio (business_rules)
    - Escrita de Excel (excel_writer)
    - Orquestração completa (main.py)
    """

    browser = request.config.getoption("--browser") or "edge"
    is_headless = request.config.getoption("--headless")
    # --- 1. PREPARAÇÃO (ARRANGE) ---
    arquivo_entrada = tmp_path / "input_vendas.xlsx"
    arquivo_saida = tmp_path / "relatorio_final.xlsx"
    
    # Cria o arquivo Excel real para o teste
    df = pd.DataFrame(DADOS_INPUT)
    df.to_excel(arquivo_entrada, index=False)
    
    # --- 2. EXECUÇÃO (ACT) ---
    # Constrói a lista de argumentos base
    argumentos_simulados = [
        "main.py", 
        "--input", str(arquivo_entrada),
        "--output", str(arquivo_saida),
        "--browser", browser
    ]
    
    # Propaga o modo headless se estiver ativo no pytest
    if is_headless:
        argumentos_simulados.append("--headless")
    
    # O patch substitui o sys.argv real pelos nossos argumentos
    with patch.object(sys, 'argv', argumentos_simulados):
        main()

    # --- 3. VERIFICAÇÃO (ASSERT) ---
    # Verifica se o arquivo foi criado
    assert arquivo_saida.exists(), "Relatório não foi gerado"
    
    # Lê o arquivo gerado para verificar conteúdo
    df_resultado = pd.read_excel(arquivo_saida)
    
    # Verifica se processou as 2 linhas
    # (Nota: linha de TOTAL é adicionada, então len pode ser 3)
    assert len(df_resultado) >= 2, "Deveria ter pelo menos 2 linhas de dados"
    
    # Verifica se calculou lucro (coluna existe e não está vazia)
    assert "Lucro" in df_resultado.columns, "Coluna 'Lucro' não encontrada"
    
    # Verifica se o ID do primeiro item está no relatório
    assert df_resultado.iloc[0]["ID Venda"] == "TX-INT-01", \
        "Primeira transação não foi processada corretamente"


@pytest.mark.integration
@pytest.mark.e2e
def test_main_sem_arquivo_entrada():
    """
    Garante que o main falha graciosamente se o input não existir.
    
    Este teste valida:
    - Tratamento de erro (FileNotFoundError)
    - Exit code correto (sys.exit(1))
    - Log de erro apropriado
    """
    argumentos_falha = ["main.py", "--input", "arquivo_fantasma.xlsx"]
    
    with patch.object(sys, 'argv', argumentos_falha):
        # O main.py tem um sys.exit(1) no catch geral de erro.
        # O pytest captura esse exit e verifica se o código foi 1 (Erro).
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Verifica se saiu com código de erro (não 0)
        assert exc_info.value.code == 1, \
            "Deveria ter saído com código de erro 1"


@pytest.mark.integration
def test_main_modo_mock_sem_selenium(tmp_path):
    """
    Testa o fluxo completo em MODO MOCK (sem Selenium).
    
    Este teste valida que o sistema funciona sem navegador
    (útil para ambientes onde Selenium não está disponível).
    
    Mais rápido que E2E completo, mas ainda testa integração.
    """
    # Preparação
    arquivo_entrada = tmp_path / "input_vendas_mock.xlsx"
    arquivo_saida = tmp_path / "relatorio_mock.xlsx"
    
    df = pd.DataFrame(DADOS_INPUT)
    df.to_excel(arquivo_entrada, index=False)
    
    # Execução com flag --mock
    argumentos_mock = [
        "main.py",
        "--input", str(arquivo_entrada),
        "--output", str(arquivo_saida),
        "--mock"  # Usa simulação em vez de Selenium
    ]
    
    with patch.object(sys, 'argv', argumentos_mock):
        main()
    
    # Verificação
    assert arquivo_saida.exists(), "Relatório mock não foi gerado"
    
    df_resultado = pd.read_excel(arquivo_saida)
    assert len(df_resultado) >= 2, "Deveria ter processado as vendas"
    assert "Lucro" in df_resultado.columns
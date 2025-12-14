"""
Teste de Integração (End-to-End).
Simula a execução real do script main.py via linha de comando.
"""
import sys
import pytest
import pandas as pd
from unittest.mock import patch
from src.main import main

# Dados para criar um Excel de entrada válido na hora do teste
DADOS_INPUT = {
    'ID da venda': ['TX-INT-01', 'TX-INT-02'],
    'Cliente': ['Cliente A', 'Cliente B'],
    'Valor bruto': [100.0, 200.0],
    'Data da venda': ['2025-01-01', '2025-01-01'],
    'Forma de pagamento': ['pix', 'cartao_credito'],
    'Custo do produto': [50.0, 100.0]
}

@pytest.mark.integration
def test_fluxo_completo_main(tmp_path):
    """
    Testa o pipeline completo:
    1. Cria excel de entrada
    2. Roda o main.py (simulando argumentos de CLI)
    3. Verifica se o excel de saída foi gerado com dados
    """
    # --- 1. PREPARAÇÃO (ARRANGE) ---
    # Define caminhos temporários (não suja seu computador)
    arquivo_entrada = tmp_path / "input_vendas.xlsx"
    arquivo_saida = tmp_path / "relatorio_final.xlsx"
    
    # Cria o arquivo Excel real para o teste
    df = pd.DataFrame(DADOS_INPUT)
    df.to_excel(arquivo_entrada, index=False)
    
    # --- 2. EXECUÇÃO (ACT) ---
    # Aqui está a mágica: Simulamos que o usuário digitou:
    # python main.py --input ... --output ...
    argumentos_simulados = [
        "main.py", 
        "--input", str(arquivo_entrada),
        "--output", str(arquivo_saida)
    ]
    
    # O patch substitui o sys.argv real pelos nossos argumentos
    with patch.object(sys, 'argv', argumentos_simulados):
        main()

    # --- 3. VERIFICAÇÃO (ASSERT) ---
    # Verifica se o arquivo foi criado
    assert arquivo_saida.exists()
    
    # Lê o arquivo gerado para ver se tem conteúdo
    df_resultado = pd.read_excel(arquivo_saida)
    
    # Verifica se processou as 2 linhas
    # (A linha 1 é cabeçalho, a linha de totais é a última, então len deve ser compatível)
    # Lembre-se que o ExcelWriter adiciona linha de Total, então o DataFrame lido terá:
    # 2 linhas de dados + 1 linha de total = 3 linhas
    assert len(df_resultado) >= 2
    
    # Verifica se calculou algo (Ex: Coluna Lucro existe e não está vazia)
    assert "Lucro" in df_resultado.columns
    # Verifica se o ID do primeiro item está lá
    assert df_resultado.iloc[0]["ID Venda"] == "TX-INT-01"

@pytest.mark.integration
def test_main_sem_arquivo_entrada():
    """Garante que o main falha graciosamente se o input não existir."""
    argumentos_falha = ["main.py", "--input", "arquivo_fantasma.xlsx"]
    
    with patch.object(sys, 'argv', argumentos_falha):
        # O main.py tem um sys.exit(1) no catch geral de erro.
        # O pytest captura esse exit e verifica se o código foi 1 (Erro).
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
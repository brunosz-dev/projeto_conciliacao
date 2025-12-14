"""
Testes para o módulo excel_reader.py
Usa fixture 'tmp_path' do pytest para criar arquivos temporários.
"""
import pytest
import pandas as pd
from src.excel_reader import read_vendas, ExcelReaderError

# Dados válidos para criar um Excel de teste
DADOS_VALIDOS = {
    'ID da venda': ['TX-01'],
    'Cliente': ['Teste'],
    'Valor bruto': [100.0],
    'Data da venda': ['2025-01-01'],
    'Forma de pagamento': ['pix'],
    'Custo do produto': [50.0]
}

@pytest.mark.io
def test_read_vendas_sucesso(tmp_path):
    """Deve ler um arquivo Excel válido corretamente."""
    # 1. Arrange: Criar arquivo temporário
    df_origem = pd.DataFrame(DADOS_VALIDOS)
    arquivo_temp = tmp_path / "vendas_teste.xlsx"
    df_origem.to_excel(arquivo_temp, index=False)

    # 2. Act
    df_lido = read_vendas(str(arquivo_temp))

    # 3. Assert
    assert len(df_lido) == 1
    assert df_lido.iloc[0]['ID da venda'] == 'TX-01'
    assert df_lido.iloc[0]['Valor bruto'] == 100.0

@pytest.mark.io
def test_read_vendas_arquivo_inexistente():
    """Deve lançar ExcelReaderError se o arquivo não existir."""
    with pytest.raises(ExcelReaderError, match="não encontrado"):
        read_vendas("caminho/que/nao/existe.xlsx")

@pytest.mark.io
def test_read_vendas_colunas_faltando(tmp_path):
    """Deve falhar se faltar colunas obrigatórias."""
    # Arrange: Cria excel faltando a coluna 'Valor bruto'
    dados_incompletos = {'ID da venda': ['TX-01']} 
    arquivo_temp = tmp_path / "incompleto.xlsx"
    pd.DataFrame(dados_incompletos).to_excel(arquivo_temp, index=False)

    # Assert
    with pytest.raises(ExcelReaderError, match="Colunas obrigatórias faltando"):
        read_vendas(str(arquivo_temp))

@pytest.mark.io
def test_read_vendas_valores_negativos(tmp_path):
    """Deve falhar se houver valores monetários negativos."""
    dados_ruins = DADOS_VALIDOS.copy()
    dados_ruins['Valor bruto'] = [-100.0] # Inválido
    
    arquivo_temp = tmp_path / "negativo.xlsx"
    pd.DataFrame(dados_ruins).to_excel(arquivo_temp, index=False)

    with pytest.raises(ExcelReaderError, match="Valores brutos devem ser maiores que zero"):
        read_vendas(str(arquivo_temp))
"""
Módulo responsável pela leitura e validação da planilha de vendas.
"""
import pandas as pd
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelReaderError(Exception):
    """Exceção personalizada para erros de leitura do Excel."""
    pass


def read_vendas(file_path: str) -> pd.DataFrame:
    """
    Lê a planilha de vendas, valida e retorna os dados em formato DataFrame.
    
    Args:
        file_path (str): Caminho completo do arquivo Excel.
    
    Returns:
        pd.DataFrame: DataFrame com as vendas validadas.
        
    Raises:
        ExcelReaderError: Se houver problemas na leitura ou validação.
    
    Example:
        >>> df = read_vendas('data/vendas.xlsx')
        >>> print(df.head())
    """
    required_columns = [
        'ID da venda', 
        'Cliente', 
        'Valor bruto', 
        'Data da venda', 
        'Forma de pagamento',
        'Custo do produto'  # ⚠️ Você vai precisar dessa!
    ]
    
    try:
        logger.info(f"📖 Lendo arquivo: {file_path}")
        
        # Lê o arquivo Excel
        df = pd.read_excel(file_path)
        logger.info(f"✅ Arquivo lido com sucesso! Total de linhas: {len(df)}")
        
        # Validar colunas obrigatórias
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ExcelReaderError(
                f"❌ Colunas obrigatórias faltando: {', '.join(missing_columns)}\n"
                f"Colunas encontradas: {', '.join(df.columns)}"
            )
        
        # Validar valores nulos
        if df[required_columns].isnull().any().any():
            colunas_com_nulos = df[required_columns].columns[df[required_columns].isnull().any()].tolist()
            raise ExcelReaderError(
                f"❌ Valores ausentes encontrados nas colunas: {', '.join(colunas_com_nulos)}"
            )
        
        # Validações adicionais
        _validar_tipos_dados(df)
        _validar_valores(df)
        
        logger.info("✅ Validação concluída com sucesso!")
        return df
    
    except FileNotFoundError:
        logger.error(f"❌ Arquivo não encontrado: {file_path}")
        raise ExcelReaderError(f"Arquivo '{file_path}' não encontrado.")
    
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        raise ExcelReaderError(f"Erro ao processar arquivo: {str(e)}")


def _validar_tipos_dados(df: pd.DataFrame) -> None:
    """Valida se os tipos de dados estão corretos."""
    try:
        # Converter e validar tipos
        df['Valor bruto'] = pd.to_numeric(df['Valor bruto'], errors='raise')
        df['Custo do produto'] = pd.to_numeric(df['Custo do produto'], errors='raise')
        df['Data da venda'] = pd.to_datetime(df['Data da venda'], errors='raise')
    except Exception as e:
        raise ExcelReaderError(f"❌ Erro na validação de tipos: {str(e)}")


def _validar_valores(df: pd.DataFrame) -> None:
    """Valida se os valores fazem sentido."""
    # Valores brutos devem ser positivos
    if (df['Valor bruto'] <= 0).any():
        raise ExcelReaderError("❌ Valores brutos devem ser maiores que zero!")
    
    # Custos não podem ser negativos
    if (df['Custo do produto'] < 0).any():
        raise ExcelReaderError("❌ Custos não podem ser negativos!")
    
    # Formas de pagamento válidas
    formas_validas = ['cartao_credito', 'cartao_debito', 'pix', 'boleto']
    formas_invalidas = df[~df['Forma de pagamento'].str.lower().isin(formas_validas)]
    
    if not formas_invalidas.empty:
        raise ExcelReaderError(
            f"❌ Formas de pagamento inválidas encontradas: "
            f"{formas_invalidas['Forma de pagamento'].unique()}"
        )
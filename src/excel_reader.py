import pandas as pd

def read_vendas(file_path):
    """
    Função para ler a planilha de vendas, validar e retornar os dados em formato DataFrame.

    Args:
        file_path (str): Caminho completo do arquivo Excel.

    Returns:
        pd.DataFrame: DataFrame com as vendas.
    """
    try:
        # Lê o arquivo Excel
        df = pd.read_excel(file_path)

        # Validar se todas as colunas obrigatórias estão presentes
        required_columns = ['ID da venda', 'Cliente', 'Valor bruto', 'Data da venda', 'Forma de pagamento']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Colunas obrigatórias faltando. Necessário: {', '.join(required_columns)}")

        # Validação de valores nulos ou vazios
        if df.isnull().any().any():
            raise ValueError("Existem valores ausentes (nulos) na planilha.")

        # Retorna o DataFrame limpo
        return df
    
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    except ValueError as ve:
        print(f"Erro de valor: {ve}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

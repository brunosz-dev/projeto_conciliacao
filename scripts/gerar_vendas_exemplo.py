"""
Ferramenta para gerar massa de dados de teste.
Gera arquivo 'data/vendas.xlsx' com casos de sucesso e falha.
"""
import pandas as pd
from datetime import datetime
from pathlib import Path

def gerar_vendas_exemplo():
    """
    Cria vendas.xlsx com dados realistas.
    Mistura IDs que existem no portal fake com IDs inexistentes para testar erros.
    """
    print("📊 Gerando massa de dados para teste...")
    
    # 1. Dados compatíveis com o Portal Fake (Sucesso)
    vendas_sucesso = [
        {"ID da venda": "TX-001", "Cliente": "João Silva", "Valor bruto": 150.00, "Data da venda": datetime(2025, 12, 1), "Forma de pagamento": "pix", "Custo do produto": 75.00},
        {"ID da venda": "TX-002", "Cliente": "Maria Santos", "Valor bruto": 300.00, "Data da venda": datetime(2025, 12, 2), "Forma de pagamento": "cartao_credito", "Custo do produto": 180.00},
        {"ID da venda": "TX-003", "Cliente": "Pedro Oliveira", "Valor bruto": 80.00, "Data da venda": datetime(2025, 12, 3), "Forma de pagamento": "cartao_debito", "Custo do produto": 40.00},
        {"ID da venda": "TX-004", "Cliente": "Ana Costa", "Valor bruto": 500.00, "Data da venda": datetime(2025, 12, 3), "Forma de pagamento": "boleto", "Custo do produto": 300.00}, # Pendente
        {"ID da venda": "TX-005", "Cliente": "Carlos Souza", "Valor bruto": 1200.00, "Data da venda": datetime(2025, 12, 4), "Forma de pagamento": "pix", "Custo do produto": 800.00},
    ]

    # 2. Dados que NÃO existem no Portal (Teste de Robustez/404)
    vendas_erro = [
        {"ID da venda": "TX-006", "Cliente": "Fernanda Lima", "Valor bruto": 250.00, "Data da venda": datetime(2025, 12, 5), "Forma de pagamento": "cartao_credito", "Custo do produto": 120.00},
        {"ID da venda": "TX-007", "Cliente": "Roberto Alves", "Valor bruto": 95.00, "Data da venda": datetime(2025, 12, 5), "Forma de pagamento": "pix", "Custo do produto": 50.00},
        {"ID da venda": "TX-008", "Cliente": "Juliana Pereira", "Valor bruto": 420.00, "Data da venda": datetime(2025, 12, 6), "Forma de pagamento": "cartao_debito", "Custo do produto": 250.00},
        {"ID da venda": "TX-009", "Cliente": "Marcos Vieira", "Valor bruto": 680.00, "Data da venda": datetime(2025, 12, 7), "Forma de pagamento": "boleto", "Custo do produto": 400.00},
        {"ID da venda": "TX-010", "Cliente": "Patricia Rocha", "Valor bruto": 175.00, "Data da venda": datetime(2025, 12, 7), "Forma de pagamento": "pix", "Custo do produto": 90.00},
    ]

    df = pd.DataFrame(vendas_sucesso + vendas_erro)
    
    # Define caminho relativo robusto (pasta 'data' na raiz do projeto)
    # Tenta achar a raiz subindo níveis se necessário
    root_dir = Path.cwd()
    if root_dir.name == "tools":
        root_dir = root_dir.parent
        
    data_dir = root_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = data_dir / "vendas.xlsx"
    
    # Salvar
    df.to_excel(output_path, index=False)
    
    print(f"✅ Arquivo criado: {output_path}")
    print(f"📊 Total de linhas: {len(df)}")
    print("-" * 40)
    print("🧪 CENÁRIO DE TESTE:")
    print("   🔹 TX-001 a TX-005: Devem ser ENCONTRADOS ✅")
    print("   🔸 TX-006 a TX-010: Devem dar NÃO ENCONTRADO (tratado) ⚠️")

if __name__ == "__main__":
    gerar_vendas_exemplo()
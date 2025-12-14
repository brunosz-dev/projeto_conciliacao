"""
Testes unitários para o módulo business_rules.py.
Padrão utilizado: AAA (Arrange, Act, Assert).
"""
import pytest
from src.business_rules import (
    calcular_resultados,
    calcular_taxa_adicional,
    obter_informacoes_taxa,
    FormaPagamento,
    TAXAS_CONFIG
)

# =============================================================================
# 1. TESTES DE CÁLCULO DE TAXAS (Sucesso)
# =============================================================================

@pytest.mark.parametrize("valor_bruto, forma_pag, esperado", [
    (100.00, "cartao_credito", 2.50),  # 2.5% de 100
    (200.00, "cartao_debito", 3.60),   # 1.8% de 200
    (1000.00, "pix", 5.00),            # 0.5% de 1000
    (50.00, "boleto", 3.50),           # Taxa fixa, independe do valor
    (5000.00, "boleto", 3.50),         # Taxa fixa, valor alto
])
def test_calcular_taxa_adicional_sucesso(valor_bruto, forma_pag, esperado):
    """Verifica se o cálculo da taxa adicional está correto para todos os tipos."""
    # Act
    resultado = calcular_taxa_adicional(valor_bruto, forma_pag)
    
    # Assert
    assert resultado == pytest.approx(esperado, 0.01)

def test_calcular_taxa_input_maiusculo_espacos():
    """Verifica se a função normaliza strings (upper/lower/mixed)."""
    # Arrange
    valor = 100.00
    forma = "PiX"  # Input "sujo"
    
    # Act
    resultado = calcular_taxa_adicional(valor, forma)
    
    # Assert
    assert resultado == 0.50  # 0.5% de 100

# =============================================================================
# 2. TESTES DE REGRAS DE NEGÓCIO COMPLETAS (Sucesso)
# =============================================================================

def test_calcular_resultados_fluxo_padrao():
    """
    Testa o fluxo completo de uma venda padrão.
    Cenário:
    - Venda: R$ 100,00
    - Gateway: R$ 3,00
    - Custo: R$ 50,00
    - Tipo: PIX (Taxa 0.5% = R$ 0,50)
    
    Matemática esperada:
    - Líquido = 100 - 3,00 - 0,50 = 96,50
    - Lucro = 96,50 - 50,00 = 46,50
    - ROI = (46,50 / 50,00) * 100 = 93,00%
    """
    # Arrange
    dados = {
        "valor_bruto": 100.00,
        "taxa_gateway": 3.00,
        "custo_produto": 50.00,
        "forma_pagamento": "pix"
    }

    # Act
    resultado = calcular_resultados(**dados)

    # Assert
    assert resultado["taxa_adicional"] == 0.50
    assert resultado["valor_liquido"] == 96.50
    assert resultado["lucro"] == 46.50
    assert resultado["roi"] == 93.00

def test_calcular_resultados_prejuizo():
    """Verifica se o sistema calcula lucro negativo corretamente."""
    # Arrange
    # Venda baixa com custo alto e taxas
    resultado = calcular_resultados(
        valor_bruto=10.00,
        taxa_gateway=1.00,
        custo_produto=15.00,
        forma_pagamento="boleto" # Taxa R$ 3.50
    )
    
    # Math:
    # Taxa add: 3.50
    # Liq: 10 - 1.00 - 3.50 = 5.50
    # Lucro: 5.50 - 15.00 = -9.50
    
    # Assert
    assert resultado["lucro"] == -9.50
    assert resultado["valor_liquido"] == 5.50
    assert resultado["roi"] < 0

# =============================================================================
# 3. TESTES DE ERROS E VALIDAÇÕES (Exceptions)
# =============================================================================

def test_calcular_taxa_forma_invalida():
    """Deve lançar ValueError se a forma de pagamento não existir."""
    with pytest.raises(ValueError, match="Forma de pagamento inválida"):
        calcular_taxa_adicional(100.0, "bitcoin")

@pytest.mark.parametrize("campo, valor_invalido", [
    ("valor_bruto", 0),
    ("valor_bruto", -10),
    ("taxa_gateway", -1),
    ("custo_produto", -5)
])
def test_validar_valores_numericos_invalidos(campo, valor_invalido):
    """Deve lançar ValueError para valores numéricos inconsistentes."""
    params = {
        "valor_bruto": 100.0,
        "taxa_gateway": 5.0,
        "custo_produto": 50.0,
        "forma_pagamento": "pix"
    }
    # Injeta o valor inválido no dicionário de parâmetros
    params[campo] = valor_invalido

    with pytest.raises(ValueError):
        calcular_resultados(**params)

# =============================================================================
# 4. CASOS DE BORDA (Edge Cases)
# =============================================================================

def test_custo_zero_roi():
    """Se o custo for zero, ROI deve ser 0 (para evitar divisão por zero)."""
    resultado = calcular_resultados(
        valor_bruto=100.0,
        taxa_gateway=0.0,
        custo_produto=0.0,
        forma_pagamento="pix"
    )
    assert resultado["roi"] == 0.0
    assert resultado["lucro"] > 0

def test_obter_informacoes_taxa():
    """Testa se a função auxiliar retorna a config correta."""
    info = obter_informacoes_taxa("cartao_credito")
    assert info["tipo"] == "percentual"
    assert info["valor"] == 0.025
    assert info["percentual"] == "2.5%"

# =============================================================================
# 5. TESTE DE INTEGRIDADE (Configuração)
# =============================================================================

def test_single_source_of_truth():
    """Garante que todas as formas do Enum tenham uma configuração de taxa."""
    for forma in FormaPagamento:
        assert forma in TAXAS_CONFIG, f"Faltou configurar a taxa para {forma.name}"
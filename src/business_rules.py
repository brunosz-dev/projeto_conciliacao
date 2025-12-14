"""
Módulo de regras de negócio para cálculos financeiros.
"""
from typing import Dict, Union
from dataclasses import dataclass
from enum import Enum


class FormaPagamento(Enum):
    """Enum para formas de pagamento aceitas."""
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    PIX = "pix"
    BOLETO = "boleto"

class StatusTransacao(Enum):
    """Estados possíveis de uma transação no portal."""
    APROVADO = "Aprovado"
    PENDENTE = "Pendente"
    DIVERGENTE = "Pendente (Divergência)"


# Configuração de taxas (facilita manutenção!)
TAXAS_CONFIG = {
    FormaPagamento.CARTAO_CREDITO: {"tipo": "percentual", "valor": 0.025},
    FormaPagamento.CARTAO_DEBITO: {"tipo": "percentual", "valor": 0.018},
    FormaPagamento.PIX: {"tipo": "percentual", "valor": 0.005},
    FormaPagamento.BOLETO: {"tipo": "fixo", "valor": 3.50}
}


@dataclass
class ResultadoFinanceiro:
    """Estrutura de dados para resultado financeiro."""
    taxa_adicional: float
    valor_liquido: float
    lucro: float
    roi: float
    
    def to_dict(self) -> Dict[str, float]:
        """Converte para dicionário."""
        return {
            "taxa_adicional": round(self.taxa_adicional, 2),
            "valor_liquido": round(self.valor_liquido, 2),
            "lucro": round(self.lucro, 2),
            "roi": round(self.roi, 2)
        }


def calcular_taxa_adicional(valor_bruto: float, forma_pagamento: str) -> float:
    """
    Calcula a taxa adicional baseada na forma de pagamento.
    
    Args:
        valor_bruto: Valor da transação
        forma_pagamento: Forma de pagamento (ex: 'cartao_credito')
    
    Returns:
        float: Valor da taxa adicional
        
    Raises:
        ValueError: Se forma de pagamento for inválida
        
    Example:
        >>> calcular_taxa_adicional(100.0, 'pix')
        0.5
    """
    try:
        forma = FormaPagamento(forma_pagamento.lower())
        config = TAXAS_CONFIG[forma]
        
        if config["tipo"] == "percentual":
            return valor_bruto * config["valor"]
        else:  # fixo
            return config["valor"]
            
    except ValueError:
        formas_validas = [f.value for f in FormaPagamento]
        raise ValueError(
            f"❌ Forma de pagamento inválida: '{forma_pagamento}'\n"
            f"Formas válidas: {', '.join(formas_validas)}"
        )


def calcular_resultados(
    valor_bruto: float,
    taxa_gateway: float,
    custo_produto: float,
    forma_pagamento: str
) -> Dict[str, float]:
    """
    Calcula todos os resultados financeiros da transação.
    
    Args:
        valor_bruto: Valor bruto da venda
        taxa_gateway: Taxa cobrada pelo gateway
        custo_produto: Custo do produto
        forma_pagamento: Forma de pagamento utilizada
    
    Returns:
        Dict com taxa_adicional, valor_liquido, lucro e ROI
        
    Example:
        >>> resultado = calcular_resultados(100.0, 3.0, 50.0, 'pix')
        >>> print(resultado['lucro'])
        46.5
    """
    # Validações
    if valor_bruto <= 0:
        raise ValueError("❌ Valor bruto deve ser positivo!")
    if taxa_gateway < 0:
        raise ValueError("❌ Taxa gateway não pode ser negativa!")
    if custo_produto < 0:
        raise ValueError("❌ Custo do produto não pode ser negativo!")
    
    # Cálculos
    taxa_adicional = calcular_taxa_adicional(valor_bruto, forma_pagamento)
    valor_liquido = valor_bruto - taxa_gateway - taxa_adicional
    lucro = valor_liquido - custo_produto
    
    # ROI (Return on Investment)
    roi = (lucro / custo_produto * 100) if custo_produto > 0 else 0
    
    # Criar objeto resultado
    resultado = ResultadoFinanceiro(
        taxa_adicional=taxa_adicional,
        valor_liquido=valor_liquido,
        lucro=lucro,
        roi=roi
    )
    
    return resultado.to_dict()


def obter_informacoes_taxa(forma_pagamento: str) -> Dict[str, Union[str, float]]:
    """
    Retorna informações sobre a taxa de uma forma de pagamento.
    
    Args:
        forma_pagamento: Forma de pagamento
        
    Returns:
        Dict com tipo e valor da taxa
        
    Example:
        >>> info = obter_informacoes_taxa('pix')
        >>> print(info)
        {'tipo': 'percentual', 'valor': 0.005, 'percentual': '0.5%'}
    """
    forma = FormaPagamento(forma_pagamento.lower())
    config = TAXAS_CONFIG[forma].copy()
    
    if config["tipo"] == "percentual":
        config["percentual"] = f"{config['valor'] * 100}%"
    
    return config
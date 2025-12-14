def calcular_taxa_adicional(valor_bruto, forma_pagamento):
    forma = forma_pagamento.lower()

    if forma == "cartao_credito":
        return valor_bruto * 0.025
    elif forma == "cartao_debito":
        return valor_bruto * 0.018
    elif forma == "pix":
        return valor_bruto * 0.005
    elif forma == "boleto":
        return 3.50
    else:
        raise ValueError(f"Forma de pagamento inválida: {forma_pagamento}")


def calcular_resultados(valor_bruto, taxa_gateway, custo_produto, forma_pagamento):
    taxa_adicional = calcular_taxa_adicional(valor_bruto, forma_pagamento)

    valor_liquido = valor_bruto - taxa_gateway - taxa_adicional
    lucro = valor_liquido - custo_produto

    roi = 0
    if custo_produto > 0:
        roi = (lucro / custo_produto) * 100

    return {
        "taxa_adicional": round(taxa_adicional, 2),
        "valor_liquido": round(valor_liquido, 2),
        "lucro": round(lucro, 2),
        "roi": round(roi, 2)
    }

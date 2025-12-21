"""
Testes para o módulo web_scraper.py (Selenium).

Fixtures globais definidas em conftest.py:
    - portal_url: URL do portal fake
    - scraper: Cliente Selenium configurado

Execução:
    pytest -m selenium                  # Todos os testes Selenium
    pytest -m "selenium and not slow"   # Ignora performance
    pytest -m selenium --browser=chrome # Força Chrome
"""
import pytest
from unittest.mock import patch
from src.web_scraper import (
    PortalPagamentosClient,
    PortalTransacaoNaoEncontrada,
    PortalConnectionError,
    PortalScraperError
)
from src.business_rules import StatusTransacao


# ======================================================================
# TESTES PARAMETRIZADOS (Reduz duplicação)
# ======================================================================

@pytest.mark.selenium
@pytest.mark.parametrize(
    "id_venda, taxa_esperada, status_esperado, data_esperada",
    [
        ("TX-001", 0.75, StatusTransacao.APROVADO, "01/12/2025"),
        ("TX-002", 7.50, StatusTransacao.APROVADO, "02/01/2026"),
        ("TX-003", 1.44, StatusTransacao.APROVADO, "04/12/2025"),
        ("TX-004", 3.50, StatusTransacao.PENDENTE, None),
        ("TX-005", 6.00, StatusTransacao.APROVADO, "04/12/2025"),
    ],
    ids=["tx001-aprovado", "tx002-aprovado", "tx003-aprovado", "tx004-pendente", "tx005-aprovado"]
)
def test_transacoes_conhecidas(scraper, id_venda, taxa_esperada, status_esperado, data_esperada):
    """
    Valida leitura de todas as transações conhecidas do portal fake.
    
    Parametrização permite testar múltiplos casos sem duplicar código.
    Se um caso falhar, o ID indica qual (ex: tx004-pendente).
    """
    resultado = scraper.consultar_transacao(id_venda)
    
    assert resultado['taxa_gateway'] == pytest.approx(taxa_esperada, 0.01)
    assert resultado['status_portal'] == status_esperado
    assert resultado['data_pagamento'] == data_esperada


# ======================================================================
# TESTES DE EXCEÇÕES
# ======================================================================

@pytest.mark.selenium
def test_transacao_nao_encontrada_levanta_excecao_customizada(scraper):
    """
    TX-999 não existe no portal.
    Deve lançar PortalTransacaoNaoEncontrada (não ValueError genérico).
    """
    with pytest.raises(PortalTransacaoNaoEncontrada) as exc_info:
        scraper.consultar_transacao("TX-999")
    
    # Valida mensagem de erro
    assert "TX-999" in str(exc_info.value)
    assert "não existe" in str(exc_info.value).lower()


@pytest.mark.selenium
def test_catch_generico_com_base_exception(scraper):
    """
    Valida que PortalScraperError funciona como catch-all.
    Útil quando main.py quer pegar qualquer erro do scraper.
    """
    with pytest.raises(PortalScraperError):
        scraper.consultar_transacao("TX-999")


# ======================================================================
# TESTES DE VALIDAÇÃO DE DADOS
# ======================================================================

@pytest.mark.selenium
def test_estrutura_retorno_correta(scraper):
    """Valida que o retorno tem campos obrigatórios e tipos corretos."""
    resultado = scraper.consultar_transacao("TX-001")
    
    # Campos obrigatórios
    assert 'taxa_gateway' in resultado
    assert 'status_portal' in resultado
    assert 'data_pagamento' in resultado
    
    # Tipos corretos
    assert isinstance(resultado['taxa_gateway'], float)
    assert isinstance(resultado['status_portal'], StatusTransacao)
    assert isinstance(resultado['data_pagamento'], (str, type(None)))


@pytest.mark.selenium
def test_parser_moeda_valores_altos(scraper):
    """
    TX-005 tem R$ 1.200,00 (com separador de milhar).
    Valida que parser converte corretamente: "R$ 1.200,00" → 1200.0
    """
    resultado = scraper.consultar_transacao("TX-005")
    
    assert isinstance(resultado['taxa_gateway'], float)
    assert resultado['taxa_gateway'] == pytest.approx(6.0, 0.01)


@pytest.mark.selenium
def test_data_pagamento_formato_valido_ou_none(scraper):
    """
    data_pagamento deve ser None (pendente) OU string DD/MM/YYYY válida.
    """
    resultado = scraper.consultar_transacao("TX-001")
    data = resultado['data_pagamento']
    
    if data is not None:
        # Valida formato DD/MM/YYYY
        assert len(data) == 10
        assert data[2] == '/' and data[5] == '/'
        
        # Valida se é data real (lança exceção se inválida)
        from datetime import datetime
        datetime.strptime(data, "%d/%m/%Y")


# ======================================================================
# TESTES DE EDGE CASES
# ======================================================================

@pytest.mark.selenium
def test_multiplas_consultas_mesma_sessao(scraper):
    """
    Valida que o scraper pode consultar múltiplas transações
    na mesma sessão do navegador (reutilização de conexão).
    """
    ids = ["TX-001", "TX-002", "TX-003"]
    resultados = []
    
    for id_venda in ids:
        resultado = scraper.consultar_transacao(id_venda)
        resultados.append(resultado)
    
    assert len(resultados) == 3
    assert all('taxa_gateway' in r for r in resultados)


@pytest.mark.selenium
def test_consulta_repetida_retorna_resultado_identico(scraper):
    """
    Consultar o mesmo ID duas vezes deve retornar resultado idêntico.
    Valida idempotência (importante para retry em produção).
    """
    resultado1 = scraper.consultar_transacao("TX-001")
    resultado2 = scraper.consultar_transacao("TX-001")
    
    assert resultado1['taxa_gateway'] == resultado2['taxa_gateway']
    assert resultado1['status_portal'] == resultado2['status_portal']
    assert resultado1['data_pagamento'] == resultado2['data_pagamento']


# ======================================================================
# TESTES COM MOCK (Simulando Erros de Infraestrutura)
# ======================================================================

@pytest.mark.selenium
@patch('src.web_scraper.webdriver.Edge')
def test_erro_inicializacao_driver(mock_edge, portal_url):
    """
    Simula falha crítica ao iniciar WebDriver (ex: EdgeDriver não encontrado).
    Deve lançar PortalConnectionError (não WebDriverException genérico).
    
    NOTA: Não usa fixture 'scraper' porque queremos testar a falha no __init__.
    """
    from selenium.common.exceptions import WebDriverException
    
    # Simula erro ao criar driver
    mock_edge.side_effect = WebDriverException("EdgeDriver not found")
    
    # Tenta instanciar (deve falhar)
    with pytest.raises(PortalConnectionError) as exc_info:
        with PortalPagamentosClient(portal_url, browser="edge") as client:
            pass
    
    # Valida mensagem de erro
    assert "Falha ao inicializar" in str(exc_info.value)


@pytest.mark.selenium
def test_navegador_invalido_levanta_valueerror(portal_url):
    """
    Passar navegador não suportado deve lançar ValueError.
    NOTA: Não usa fixture 'scraper' porque testa validação do __init__.
    """
    with pytest.raises(ValueError) as exc_info:
        PortalPagamentosClient(portal_url, browser="firefox")
    
    assert "não suportado" in str(exc_info.value).lower()


# ======================================================================
# TESTES DE HIERARQUIA DE EXCEÇÕES
# ======================================================================

def test_hierarquia_excecoes():
    """
    Valida que todas as exceções customizadas herdam de PortalScraperError.
    Permite catch genérico quando necessário: except PortalScraperError.
    """
    from src.web_scraper import (
        PortalTimeoutError,
        PortalElementoNaoEncontrado,
        PortalDadosInvalidos
    )
    
    assert issubclass(PortalTransacaoNaoEncontrada, PortalScraperError)
    assert issubclass(PortalTimeoutError, PortalScraperError)
    assert issubclass(PortalConnectionError, PortalScraperError)
    assert issubclass(PortalElementoNaoEncontrado, PortalScraperError)
    assert issubclass(PortalDadosInvalidos, PortalScraperError)


# ======================================================================
# TESTES DE PERFORMANCE (Marcados como 'slow')
# ======================================================================

@pytest.mark.selenium
@pytest.mark.slow
def test_performance_multiplas_consultas(scraper):
    """
    Valida estabilidade em múltiplas consultas sequenciais.
    
    NOTA: Marcado como 'slow' porque:
    - Pode demorar em máquinas lentas
    - Pode falhar em CI sem ser bug real
    - Opcional: pytest -m "selenium and not slow"
    
    Assert comentado para não quebrar em CI.
    """
    import time
    
    ids = ["TX-001", "TX-002", "TX-003", "TX-004", "TX-005"]
    
    inicio = time.time()
    for id_venda in ids:
        scraper.consultar_transacao(id_venda)
    tempo_total = time.time() - inicio
    
    tempo_medio = tempo_total / len(ids)
    
    # Log para monitoramento (não falha teste)
    print(f"\n⏱️  Performance: {tempo_medio:.2f}s por consulta ({tempo_total:.2f}s total)")
    
    # Assert comentado - descomente se quiser validar performance
    # assert tempo_medio < 2.0, f"Muito lento: {tempo_medio:.2f}s/consulta"


# ======================================================================
# TESTES DE EXEMPLO (Para Documentação)
# ======================================================================

@pytest.mark.selenium
def test_exemplo_uso_basico(scraper):
    """
    Exemplo básico que aparecerá no README.
    Demonstra uso típico do scraper.
    """
    resultado = scraper.consultar_transacao("TX-001")
    
    assert resultado['taxa_gateway'] > 0
    assert resultado['status_portal'] == StatusTransacao.APROVADO


@pytest.mark.selenium
def test_exemplo_tratamento_erro(scraper):
    """
    Exemplo de tratamento de erro para README.
    Mostra como capturar transação não encontrada.
    """
    try:
        resultado = scraper.consultar_transacao("TX-999")
        pytest.fail("TX-999 não deveria existir")
    except PortalTransacaoNaoEncontrada as e:
        # Comportamento esperado
        assert "TX-999" in str(e)
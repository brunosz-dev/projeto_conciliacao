"""
Configuração central de testes (pytest).
Define fixtures globais e configurações.
"""
import pytest
from pathlib import Path
from src.web_scraper import PortalPagamentosClient


def pytest_configure(config):
    """Registra markers customizados."""
    config.addinivalue_line(
        "markers",
        "selenium: Testes que usam Selenium (requerem navegador)"
    )
    config.addinivalue_line(
        "markers",
        "slow: Testes lentos de performance (podem demorar)"
    )
    config.addinivalue_line(
        "markers",
        "business: Testes de lógica financeira"
    )
    config.addinivalue_line(
        "markers",
        "io: Testes de leitura e escrita de arquivos"
    )
    config.addinivalue_line(
        "markers",
        "integration: Testes de integração end-to-end"
    )


def pytest_addoption(parser):
    """Adiciona opções customizadas ao pytest."""
    parser.addoption(
        "--browser",
        action="store",
        default="edge",
        choices=["chrome", "edge"],
        help="Navegador para testes Selenium (padrão: edge)"
    )


# ======================================================================
# FIXTURES GLOBAIS
# ======================================================================

@pytest.fixture(scope="session")
def portal_url():
    """
    Retorna a URL do portal fake.
    Scope='session' = criado uma vez por sessão de testes.
    """
    base_dir = Path.cwd()
    html_path = base_dir / "web_portal_fake" / "index.html"
    
    if not html_path.exists():
        pytest.skip(
            "Portal fake não encontrado. "
            "Execute: python scripts/gerar_portal_fake.py"
        )
    
    return f"file://{html_path}"


@pytest.fixture
def scraper(portal_url, request):
    """
    Inicializa o scraper em modo headless.
    
    Usa o navegador especificado via --browser (padrão: edge).
    Se o navegador não estiver disponível, SKIP (não fallback).
    
    Example:
        pytest -m selenium --browser=chrome
    """
    browser = request.config.getoption("--browser")
    
    try:
        client = PortalPagamentosClient(
            portal_url,
            browser=browser,
            headless=True,
            timeout=5
        )
    except Exception as e:
        pytest.skip(
            f"Navegador '{browser}' indisponível: {e}\n"
            f"Instale o {browser} ou use --browser com outro navegador."
        )
    
    with client as bot:
        yield bot
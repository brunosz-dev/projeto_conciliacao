"""
Configuração central de testes (pytest).
Define fixtures globais e configurações.
"""
import pytest
from pathlib import Path
from src.web_scraper import PortalPagamentosClient


def pytest_configure(config):
    """Registra markers customizados."""
    markers = [
        "selenium: Testes que usam Selenium (requerem navegador)",
        "slow: Testes lentos de performance (podem demorar)",
        "business: Testes de lógica financeira",
        "io: Testes de leitura e escrita de arquivos",
        "integration: Testes de integração entre módulos",
        "e2e: Testes ponta a ponta (CLI + Selenium + IO real)",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_addoption(parser):
    """Adiciona opções customizadas ao pytest."""
    parser.addoption(
        "--browser",
        action="store",
        default="edge",
        choices=["chrome", "edge"],
        help="Navegador para testes Selenium (padrão: edge)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Executar testes sem interface gráfica (útil para CI)"
    )


# ======================================================================
# FIXTURES GLOBAIS
# ======================================================================

@pytest.fixture(scope="session")
def portal_url():
    """
    Retorna a URL do portal fake de forma compatível com CI/Linux.
    """
    base_dir = Path.cwd()
    html_path = base_dir / "web_portal_fake" / "index.html"
    
    if not html_path.exists():
        html_path = Path(__file__).resolve().parent.parent / "web_portal_fake" / "index.html"
    
    if not html_path.exists():
        pytest.skip(f"Portal fake não encontrado em: {html_path}")
    
    return html_path.as_uri()


@pytest.fixture
def scraper(portal_url, request):
    """
    Inicializa o scraper Selenium.

    Usa:
    - --browser (edge/chrome)
    - --headless (opcional)
    """
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    try:
        client = PortalPagamentosClient(
            portal_url,
            browser=browser,
            headless=headless,
            timeout=5
        )
    except Exception as e:
        pytest.skip(
            f"Navegador '{browser}' indisponível: {e}\n"
            f"Instale o {browser} ou use --browser com outro navegador."
        )

    with client as bot:
        yield bot

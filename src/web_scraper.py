"""
Módulo de automação web com Selenium.
Suporta Google Chrome e Microsoft Edge.
"""
import logging
from typing import Dict, Union, Optional
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, 
    TimeoutException as SeleniumTimeoutException,
    NoSuchElementException
)

from src.business_rules import StatusTransacao

logger = logging.getLogger("ConciliacaoBot")


# ======================================================================
# EXCEÇÕES CUSTOMIZADAS
# ======================================================================

class PortalScraperError(Exception):
    """Exceção base para erros do scraper."""
    pass


class PortalConnectionError(PortalScraperError):
    """Erro ao conectar no portal."""
    pass


class PortalTimeoutError(PortalScraperError):
    """Timeout ao aguardar resposta do portal."""
    pass


class PortalTransacaoNaoEncontrada(PortalScraperError):
    """Transação não existe no portal."""
    pass


class PortalElementoNaoEncontrado(PortalScraperError):
    """Elemento HTML esperado não foi encontrado."""
    pass


class PortalDadosInvalidos(PortalScraperError):
    """Dados extraídos do portal estão em formato inválido."""
    pass


# ======================================================================
# CLIENTE SELENIUM HÍBRIDO (Chrome/Edge)
# ======================================================================

class PortalPagamentosClient:
    """
    Cliente Selenium para consulta no portal de pagamentos.
    Suporta Google Chrome e Microsoft Edge.
    
    Implementa context manager para gerenciamento automático de recursos.
    Usa espera explícita inteligente para lidar com carregamento assíncrono.
    
    Args:
        portal_url: URL do portal (file:// ou http://)
        browser: Navegador a usar ('chrome' ou 'edge')
        headless: Se True, roda sem interface gráfica
        timeout: Tempo máximo de espera por elementos (segundos)
    
    Example:
        >>> # Usando Chrome (padrão)
        >>> with PortalPagamentosClient(url) as client:
        ...     resultado = client.consultar_transacao("TX-001")
        
        >>> # Usando Edge
        >>> with PortalPagamentosClient(url, browser="edge") as client:
        ...     resultado = client.consultar_transacao("TX-001")
    """

    def __init__(
        self, 
        portal_url: str, 
        browser: str = "chrome", 
        headless: bool = False, 
        timeout: int = 5
    ):
        """Inicializa o cliente Selenium."""
        self.portal_url = portal_url
        self.browser = browser.lower().strip()  # Normaliza
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        
        # Validação do navegador
        if self.browser not in ["chrome", "edge"]:
            raise ValueError(
                f"Navegador '{browser}' não suportado. "
                f"Use 'chrome' ou 'edge'."
            )

    def __enter__(self):
        """Inicializa o WebDriver e acessa o portal."""
        try:
            logger.info(f"🤖 Inicializando WebDriver ({self.browser.upper()})...")
            
            # Inicializa o navegador escolhido
            if self.browser == "edge":
                self._init_edge()
            else:
                self._init_chrome()
            
            self.wait = WebDriverWait(self.driver, self.timeout)
            
            logger.info(f"🌐 Acessando portal: {self.portal_url}")
            self.driver.get(self.portal_url)
            
            # Aguarda carregamento completo
            self.wait.until(
                EC.presence_of_element_located((By.ID, "search-input"))
            )
            logger.info("✅ Portal carregado com sucesso!")
            
        except SeleniumTimeoutException:
            if self.driver:
                self.driver.quit()
            raise PortalConnectionError(
                f"Portal não respondeu em {self.timeout}s. "
                f"Verifique se a URL está correta: {self.portal_url}"
            )
        except WebDriverException as e:
            if self.driver:
                self.driver.quit()
            raise PortalConnectionError(
                f"Falha ao inicializar {self.browser.upper()}: {e}\n"
                f"Verifique se o navegador e driver estão instalados."
            )
            
        return self

    def _init_chrome(self):
        """Configura e inicia o Google Chrome."""
        options = ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Configurações para estabilidade
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=options)

    def _init_edge(self):
        """Configura e inicia o Microsoft Edge."""
        options = EdgeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Configurações para estabilidade
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Edge(options=options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha o navegador automaticamente."""
        if self.driver:
            logger.info("🔒 Fechando navegador...")
            self.driver.quit()

    def consultar_transacao(
        self, 
        id_venda: str
    ) -> Dict[str, Union[float, StatusTransacao, Optional[str]]]:
        """
        Busca uma transação pelo ID e extrai dados do portal.
        
        Args:
            id_venda: ID da transação (ex: "TX-001")
        
        Returns:
            Dict com taxa_gateway, status_portal, data_pagamento
        
        Raises:
            PortalTimeoutError: Portal não respondeu a tempo
            PortalTransacaoNaoEncontrada: ID não existe no portal
            PortalElementoNaoEncontrado: Layout do portal mudou
            PortalDadosInvalidos: Dados em formato inesperado
        """
        logger.info(f"🔍 Buscando transação: {id_venda}")
        
        try:
            # 1. Localizar e preencher campo de busca
            search_input = self.driver.find_element(By.ID, "search-input")
            search_input.clear()
            search_input.send_keys(id_venda)
            
            # 2. Clicar no botão de busca
            btn_search = self.driver.find_element(By.ID, "btn-search")
            btn_search.click()
            
            # 3. Espera inteligente
            try:
                self.wait.until(
                    lambda d: (
                        d.find_element(By.ID, "result-section").is_displayed() or 
                        d.find_element(By.ID, "error-section").is_displayed()
                    )
                )
            except SeleniumTimeoutException:
                self._salvar_screenshot_erro(id_venda, "timeout")
                raise PortalTimeoutError(
                    f"Portal não respondeu para ID {id_venda} em {self.timeout}s"
                )
            
            # 4. Verificar se foi erro
            error_section = self.driver.find_element(By.ID, "error-section")
            if error_section.is_displayed():
                logger.warning(f"⚠️ Transação {id_venda} não encontrada no portal")
                raise PortalTransacaoNaoEncontrada(
                    f"ID {id_venda} não existe no portal ou ainda não foi processado"
                )
            
            # 5. Extrair dados
            dados = self._extrair_dados_resultado(id_venda)
            
            logger.info(
                f"✅ {id_venda}: Taxa R$ {dados['taxa_gateway']:.2f} | "
                f"Status: {dados['status_portal'].value}"
            )
            
            return dados
            
        except NoSuchElementException as e:
            self._salvar_screenshot_erro(id_venda, "elemento_nao_encontrado")
            raise PortalElementoNaoEncontrado(
                f"Elemento HTML não encontrado para {id_venda}: {e}\n"
                f"O layout do portal pode ter mudado."
            )
        except (PortalTimeoutError, PortalTransacaoNaoEncontrada, PortalElementoNaoEncontrado):
            raise
        except Exception as e:
            self._salvar_screenshot_erro(id_venda, "erro_generico")
            raise PortalScraperError(
                f"Erro inesperado ao consultar {id_venda}: {e}"
            )

    def _extrair_dados_resultado(
        self, 
        id_venda: str
    ) -> Dict[str, Union[float, StatusTransacao, Optional[str]]]:
        """Extrai os dados do painel de resultado."""
        try:
            el_taxa = self.driver.find_element(By.ID, "result-taxa")
            el_status = self.driver.find_element(By.ID, "result-status")
            el_data_pag = self.driver.find_element(By.ID, "result-data-pagamento")
            
            return {
                "taxa_gateway": self._parse_ptbr_float(el_taxa.text),
                "status_portal": self._parse_status_enum(el_status.text),
                "data_pagamento": self._parse_data_pagamento(el_data_pag.text)
            }
        except Exception as e:
            raise PortalDadosInvalidos(
                f"Erro ao extrair/converter dados do HTML para {id_venda}: {e}"
            )

    def _parse_ptbr_float(self, valor: str) -> float:
        """Converte string monetária PT-BR em float."""
        try:
            clean = (
                valor.replace("R$", "")
                     .replace(" ", "")
                     .replace(".", "")
                     .replace(",", ".")
            )
            return float(clean)
        except (ValueError, AttributeError) as e:
            raise PortalDadosInvalidos(
                f"Não foi possível converter valor monetário: '{valor}' → {e}"
            )

    def _parse_status_enum(self, status: str) -> StatusTransacao:
        """Converte string de status em Enum."""
        status_upper = status.upper().strip()
        
        if "APROVADO" in status_upper:
            return StatusTransacao.APROVADO
        elif "PENDENTE" in status_upper:
            return StatusTransacao.PENDENTE
        else:
            return StatusTransacao.DIVERGENTE

    def _parse_data_pagamento(self, data_texto: str) -> Optional[str]:
        """Processa o campo de data de pagamento."""
        data_limpa = data_texto.strip()
        
        if "Pendente" in data_limpa or "processamento" in data_limpa:
            return None
        
        if len(data_limpa) == 10 and data_limpa[2] == '/' and data_limpa[5] == '/':
            try:
                datetime.strptime(data_limpa, "%d/%m/%Y")
                return data_limpa
            except ValueError:
                logger.warning(f"⚠️ Data inválida: '{data_limpa}'")
                return None
        
        return None

    def _salvar_screenshot_erro(self, id_venda: str, tipo_erro: str) -> None:
        """Salva screenshot da página em caso de erro."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"erro_{tipo_erro}_{id_venda}_{timestamp}.png"
            
            screenshot_dir = Path("output") / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = screenshot_dir / filename
            self.driver.save_screenshot(str(filepath))
            
            logger.info(f"📸 Screenshot salvo: {filepath}")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível salvar screenshot: {e}")


# ======================================================================
# TESTE STANDALONE
# ======================================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    
    PORTAL_URL = f"file://{Path.cwd()}/web_portal_fake/index.html"
    
    print("=" * 70)
    print("🧪 TESTE HÍBRIDO - Chrome e Edge")
    print("=" * 70)
    
    # Testar ambos navegadores
    for browser in ["chrome", "edge"]:
        print(f"\n{'=' * 70}")
        print(f"🌐 Testando com {browser.upper()}")
        print("=" * 70)
        
        try:
            with PortalPagamentosClient(
                PORTAL_URL, 
                browser=browser, 
                headless=False
            ) as client:
                # Testar TX-001
                resultado = client.consultar_transacao("TX-001")
                print(f"✅ TX-001: R$ {resultado['taxa_gateway']:.2f} - {resultado['status_portal'].value}")
                
        except PortalConnectionError as e:
            print(f"❌ {browser.upper()} não disponível: {e}")
            print(f"   Instale o {browser.upper()} ou use --browser com outro navegador")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print(f"\n{'=' * 70}")
    print("✅ Teste concluído!")
    print("=" * 70)
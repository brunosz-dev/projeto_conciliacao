# 📊 Projeto de Conciliação Financeira

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Tests](https://img.shields.io/badge/tests-pytest-green.svg)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Sistema de conciliação financeira desenvolvido em Python para processar vendas, calcular taxas, lucro, ROI e gerar relatórios Excel formatados.

Este projeto foi estruturado com foco em **qualidade de código, testabilidade e arquitetura profissional**, simulando um cenário real de backend financeiro com integração a portal de pagamentos.

---

## 🚀 Visão Geral

O sistema realiza:

- Leitura de vendas a partir de arquivos Excel
- Validação rigorosa de dados
- Aplicação de regras de negócio financeiras
- Consulta automatizada a um **portal de pagamentos fake** (Selenium)
- Tratamento robusto de erros e exceções
- Geração de relatório final em Excel
- Log detalhado de execução
- Execução automatizada em **CI (GitHub Actions)**

A aplicação foi pensada para simular **um fluxo real de conciliação financeira**, do input bruto até o relatório final.

---

## 🧱 Arquitetura do Projeto

```
projeto_conciliacao/
│
├── src/
│ ├── business_rules.py # Regras de negócio e cálculos financeiros
│ ├── excel_reader.py # Leitura e validação de arquivos Excel
│ ├── excel_writer.py # Escrita e formatação do relatório Excel
│ ├── main.py # Orquestração do fluxo da aplicação (CLI)
│ ├── utils.py # Utilitários auxiliares
│ └── web_scraper.py # Automação web real com Selenium
│
├── web_portal_fake/ # Portal de pagamentos fake (HTML/CSS/JS)
│ ├── index.html
│ ├── styles.css
│ └── script.js
│
├── tests/
│ ├── test_business_rules.py # Testes unitários (lógica financeira)
│ ├── test_excel_reader.py # Testes de leitura (I/O)
│ ├── test_excel_writer.py # Testes de escrita (I/O)
│ └── test_main_integration.py # Testes end-to-end (pipeline completo)
│
├── .github/
│ └── workflows/
│ └── tests.yml # Pipeline CI (GitHub Actions)
│
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Como Executar

### Pré-requisitos

- Python 3.10+
- Google Chrome instalado
- ChromeDriver compatível com a versão do Chrome

---

### 1️⃣ Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows

### 2️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 3️⃣ Executar a aplicação

```bash
python -m src.main --input data/vendas.xlsx --output output/relatorio.xlsx
```

Parâmetros opcionais:

|      Flag      |                     Descrição                     |
| -------------- | ------------------------------------------------- |
| `--input`      | Caminho do Excel de vendas                        |
| `--output`     | Caminho do relatório final                        |
| `--portal-url` | URL do portal de pagamento (HTML local ou remoto) |
| `--headless`   | Executa o Selenium em modo headless               |
| `---mock`      | Executa o Selenium (simulação de portal)          |

---

## 🧪 Estratégia de Testes

O projeto utiliza **pytest** com segmentação clara por tipo de teste:

* `business` → Regras de negócio
* `io` → Leitura e escrita de arquivos
* `integration` → Fluxo completo (`main.py`)

### Executar todos os testes

```bash
pytest
```

### Executar por categoria

```bash
pytest -m business
pytest -m io
pytest -m integration
```

Pipeline CI - os testes são executados automaticamente via GitHub Actions a cada push.

### Cobertura de código

```bash
pytest --cov=src
```

Cobertura atual aproximada:

* Business Rules: **100%**
* I/O: **~90%**
* Main: **~80%**

---

## 🧠 Conceitos Aplicados

* Clean Code
* Single Responsibility Principle (SRP)
* Arquitetura modular
* Testes automatizados (Unitários e Integração)
* Selenium WebDriver (automação web)
* Tratamento semântico de exceções
* Logging estruturado
* CLI com argparse
* CI/CD com GitHub Actions

---

## 🌐 Portal de Pagamento (Simulação)

O projeto integra uma automação real com Selenium WebDriver utilizando um portal de pagamentos fake totalmente funcional, desenvolvido em HTML, CSS e JavaScript.

   • Uso de Context Manager (with PortalPagamentosClient(...))

   • Esperas explícitas inteligentes (WebDriverWait)

   • Hierarquia de exceções customizadas

   • Captura automática de screenshots em erros

   • Suporte a execução headless, ideal para CI/CD

O portal fake simula cenários reais:

   • Transação aprovada

   • Transação pendente

   • Transação inexistente

   • Layout estável para automação

---

## 🛣️ Roadmap

* [x] Regras de negócio completas
* [x] Testes unitários e de integração
* [x] Relatório Excel formatado
* [x] Portal de pagamentos fake (HTML/CSS/JS)
* [x] Automação web com Selenium
* [x] Pipeline CI (GitHub Actions)
* [ ] Testes automatizados do web scraper
* [ ] Gerador de dados de vendas (Excel)
* [ ] Exportação CSV / JSON

---

## 👤 Autor

**Bruno SZ 🇧🇷**
Desenvolvedor Python | Backend | Automação | Qualidade de Software

---

## 📄 Licença

Projeto desenvolvido para fins educacionais e de portfólio.


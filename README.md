# 📊 Projeto de Conciliação Financeira

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Tests](https://img.shields.io/badge/tests-pytest-green.svg)
![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Sistema de conciliação financeira desenvolvido em Python para processar vendas, calcular taxas, lucro, ROI e gerar relatórios Excel formatados.

Este projeto foi estruturado com foco em **qualidade de código, testabilidade e arquitetura profissional**, simulando um cenário real de backend financeiro.

---

## 🚀 Visão Geral

O sistema realiza:

* Leitura de vendas a partir de arquivos Excel
* Validação rigorosa de dados
* Aplicação de regras de negócio financeiras
* Simulação de consulta a gateway de pagamento (Web Scraping)
* Geração de relatório final em Excel
* Log detalhado de execução

Toda a aplicação é coberta por **testes unitários, testes de I/O e testes de integração end‑to‑end**.

---

## 🧱 Arquitetura do Projeto

```
projeto_conciliacao/
│
├── src/
│   ├── business_rules.py      # Regras de negócio e cálculos financeiros
│   ├── excel_reader.py        # Leitura e validação de arquivos Excel
│   ├── excel_writer.py        # Escrita e formatação do relatório Excel
│   ├── main.py                # Orquestração do fluxo da aplicação
│   ├── utils.py               # Utilitários futuros
│   └── web_scraper.py         # Placeholder para automação web
│
├── tests/
│   ├── test_business_rules.py # Testes unitários (lógica financeira)
│   ├── test_excel_reader.py   # Testes de leitura (I/O)
│   ├── test_excel_writer.py   # Testes de escrita (I/O)
│   └── test_main_integration.py # Testes end‑to‑end
│
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Como Executar

Pré-requisitos

    • Python 3.10+
    • Google Chrome instalado (para automação web)

### 1️⃣ Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 2️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 3️⃣ Executar a aplicação

```bash
python -m src.main --input data/vendas.xlsx --output output/relatorio.xlsx
```

Parâmetros opcionais:

| Flag           | Descrição                            |
| -------------- | ------------------------------------ |
| `--input`      | Caminho do Excel de vendas           |
| `--output`     | Caminho do relatório final           |
| `--portal-url` | URL do portal de pagamento (mock)    |
| `--headless`   | Flag preparada para automação futura |

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
* Testes automatizados (Unitários e Integração)
* Pytest fixtures & markers
* Dependency isolation
* Logging estruturado
* Arquitetura modular
* CLI com argparse

---

## 🌐 Portal de Pagamento (Simulação)

O projeto integra uma automação real utilizando Selenium WebDriver.

   • Padrão Utilizado: Context Manager (with PortalPagamentosClient() as bot).

   • Resiliência: Tratamento de exceções e esperas explícitas (WebDriverWait).

   • Configuração: Suporte a execução Headless (sem interface gráfica) para servidores CI/CD.

---

## 🛣️ Roadmap

* [x] Regras de negócio completas
* [x] Testes unitários e de integração
* [x] Relatório Excel formatado
* [ ] Integração com portal fake
* [ ] Pipeline CI (GitHub Actions)
* [ ] Exportação CSV / JSON

---

## 👤 Autor

**Bruno SZ 🇧🇷**
Desenvolvedor Python | Backend | Automação | Qualidade de Software

---

## 📄 Licença

Projeto desenvolvido para fins educacionais e de portfólio.
# trigger ci

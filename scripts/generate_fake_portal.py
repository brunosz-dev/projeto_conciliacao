import os

def create_portal_fake():
    """
    Cria um portal fake completo com HTML, CSS e JS.
    Atualizado com Data de Pagamento e IDs dinâmicos.
    """
    
    print("🌐 Criando Portal Financeiro Fake v2.0...")
    os.makedirs("projeto_conciliacao/web_portal_fake", exist_ok=True)
    
    # ========================================
    # 1. HTML (Com novo campo Data Pagamento)
    # ========================================
    html_content = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Gateway Pagamentos</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <h1>💳 Gateway Pagamentos</h1>
                <p class="subtitle">Ambiente de Homologação</p>
            </div>
            <div class="user-info"><span>👤 Admin</span></div>
        </header>

        <section class="search-section">
            <h2>🔍 Consultar Transação</h2>
            <div class="search-box">
                <input type="text" id="search-input" placeholder="ID da transação (ex: TX-001)" autocomplete="off">
                <button id="btn-search" class="btn btn-primary">Buscar</button>
            </div>
        </section>

        <section id="result-section" class="result-section hidden">
            <h3>📊 Detalhes</h3>
            <div class="card">
                <div class="card-header">
                    <span>ID:</span> <strong id="result-id">-</strong>
                </div>
                <div class="info-grid">
                    <div class="info-item"><label>Cliente:</label><span id="result-cliente">-</span></div>
                    <div class="info-item"><label>Data Venda:</label><span id="result-data">-</span></div>
                    <div class="info-item"><label>Data Pagamento:</label><span id="result-data-pagamento">-</span></div>
                    <div class="info-item"><label>Tipo:</label><span id="result-tipo">-</span></div>
                    <div class="info-item"><label>Valor Bruto:</label><span id="result-valor" class="value">-</span></div>
                    <div class="info-item"><label>Taxa Gateway:</label><span id="result-taxa" class="value">-</span></div>
                    <div class="info-item"><label>Status:</label><span id="result-status" class="status-badge">-</span></div>
                </div>
            </div>
        </section>

        <section id="error-section" class="error-section hidden">
            <div class="error-card">
                <span class="error-icon">⚠️</span>
                <p id="error-message">Transação não encontrada</p>
            </div>
        </section>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""
    
    # ========================================
    # 2. CSS (Igual ao anterior, sem mudanças drásticas)
    # ========================================
    css_content = """
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: sans-serif; }
    body { background: #f0f2f5; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; }
    section { background: white; padding: 25px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .search-box { display: flex; gap: 10px; }
    input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
    .btn { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
    .btn:hover { background: #2980b9; }
    .hidden { display: none; }
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
    .info-item label { display: block; color: #7f8c8d; font-size: 12px; font-weight: bold; margin-bottom: 4px; }
    .value { color: #27ae60; font-weight: bold; }
    .error-card { background: #fff3cd; color: #856404; padding: 15px; border-radius: 4px; text-align: center; }
    """

    # ========================================
    # 3. JS (Com lógica de Data Pagamento)
    # ========================================
    js_content = """
    const TRANSACTIONS_DB = {
        "TX-001": { id: "TX-001", cliente: "João Silva", data: "01/12/2025", dataPagamento: "01/12/2025", tipo: "PIX", valorBruto: 150.00, taxaGateway: 0.75, status: "Aprovado" },
        "TX-002": { id: "TX-002", cliente: "Maria Santos", data: "02/12/2025", dataPagamento: "02/01/2026", tipo: "Cartão de Crédito", valorBruto: 300.00, taxaGateway: 7.50, status: "Aprovado" },
        "TX-003": { id: "TX-003", cliente: "Pedro Oliveira", data: "03/12/2025", dataPagamento: "04/12/2025", tipo: "Cartão de Débito", valorBruto: 80.00, taxaGateway: 1.44, status: "Aprovado" },
        "TX-004": { id: "TX-004", cliente: "Ana Costa", data: "03/12/2025", dataPagamento: null, tipo: "Boleto", valorBruto: 500.00, taxaGateway: 3.50, status: "Pendente" },
        "TX-005": { id: "TX-005", cliente: "Carlos Souza", data: "04/12/2025", dataPagamento: "04/12/2025", tipo: "PIX", valorBruto: 1200.00, taxaGateway: 6.00, status: "Aprovado" }
    };

    const searchInput = document.getElementById('search-input');
    const btnSearch = document.getElementById('btn-search');
    const resultSection = document.getElementById('result-section');
    const errorSection = document.getElementById('error-section');

    btnSearch.addEventListener('click', buscar);
    searchInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') buscar() });

    function buscar() {
        const id = searchInput.value.trim().toUpperCase();
        if(!id) return;

        // Reset visual
        resultSection.classList.add('hidden');
        errorSection.classList.add('hidden');

        // Simula delay de rede (300ms)
        setTimeout(() => {
            const tx = TRANSACTIONS_DB[id];
            if (tx) exibir(tx);
            else exibirErro();
        }, 300);
    }

    function exibir(tx) {
        document.getElementById('result-id').textContent = tx.id;
        document.getElementById('result-cliente').textContent = tx.cliente;
        document.getElementById('result-data').textContent = tx.data;
        
        // Trata data de pagamento nula
        const dataPag = tx.dataPagamento ? tx.dataPagamento : "Pendente / Em processamento";
        document.getElementById('result-data-pagamento').textContent = dataPag;
        
        document.getElementById('result-tipo').textContent = tx.tipo;
        document.getElementById('result-valor').textContent = "R$ " + tx.valorBruto.toFixed(2).replace('.', ',');
        document.getElementById('result-taxa').textContent = "R$ " + tx.taxaGateway.toFixed(2).replace('.', ',');
        document.getElementById('result-status').textContent = tx.status;
        
        resultSection.classList.remove('hidden');
    }

    function exibirErro() {
        errorSection.classList.remove('hidden');
    }
    """

    arquivos = {
        "index.html": html_content,
        "styles.css": css_content,
        "script.js": js_content
    }
    
    for filename, content in arquivos.items():
        filepath = f"projeto_conciliacao/web_portal_fake/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Portal Fake v2.0 atualizado!")

if __name__ == "__main__":
    create_portal_fake()
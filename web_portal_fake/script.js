const TRANSACTIONS_DB = {
    "TX-001": {
        id: "TX-001",
        cliente: "João Silva",
        data: "01/12/2025",
        dataPagamento: "01/12/2025",
        tipo: "PIX",
        valorBruto: 150.00,
        taxaGateway: 0.75,
        status: "Aprovado"
    },
    "TX-002": {
        id: "TX-002",
        cliente: "Maria Santos",
        data: "02/12/2025",
        dataPagamento: "02/01/2026",
        tipo: "Cartão de Crédito",
        valorBruto: 300.00,
        taxaGateway: 7.50,
        status: "Aprovado"
    },
    "TX-003": {
        id: "TX-003",
        cliente: "Pedro Oliveira",
        data: "03/12/2025",
        dataPagamento: "04/12/2025",
        tipo: "Cartão de Débito",
        valorBruto: 80.00,
        taxaGateway: 1.44,
        status: "Aprovado"
    },
    "TX-004": {
        id: "TX-004",
        cliente: "Ana Costa",
        data: "03/12/2025",
        dataPagamento: null,
        tipo: "Boleto",
        valorBruto: 500.00,
        taxaGateway: 3.50,
        status: "Pendente"
    },
    "TX-005": {
    id: "TX-005",
    cliente: "Carlos Souza",
    data: "04/12/2025",
    dataPagamento: "04/12/2025",
    tipo: "PIX",
    valorBruto: 1200.00,
    taxaGateway: 6.00,
    status: "Aprovado"
    }
};

const searchInput = document.getElementById("search-input");
const btnSearch = document.getElementById("btn-search");
const resultSection = document.getElementById("result-section");
const errorSection = document.getElementById("error-section");

btnSearch.addEventListener("click", buscar);
searchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") buscar();
});

function buscar() {
    const id = searchInput.value.trim().toUpperCase();
    if (!id) return;

    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");

    setTimeout(() => {
        const tx = TRANSACTIONS_DB[id];
        if (tx) exibir(tx);
        else exibirErro();
    }, 300);
}

function exibir(tx) {
    document.getElementById("result-id").textContent = tx.id;
    document.getElementById("result-cliente").textContent = tx.cliente;
    document.getElementById("result-data").textContent = tx.data;

    const dataPag = tx.dataPagamento
        ? tx.dataPagamento
        : "Pendente / Em processamento";

    document.getElementById("result-data-pagamento").textContent = dataPag;
    document.getElementById("result-tipo").textContent = tx.tipo;
    document.getElementById("result-valor").textContent =
        "R$ " + tx.valorBruto.toFixed(2).replace(".", ",");
    document.getElementById("result-taxa").textContent =
        "R$ " + tx.taxaGateway.toFixed(2).replace(".", ",");
    document.getElementById("result-status").textContent = tx.status;

    resultSection.classList.remove("hidden");
}

function exibirErro() {
    errorSection.classList.remove("hidden");
}

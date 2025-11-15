async function loadKnowledgeBase() {
    try {
        const response = await fetch('/knowledge');
        const data = await response.json();

        const kbDiv = document.getElementById('knowledgeBase');
        kbDiv.innerHTML = `
            <h3>Fatos (${data.facts.length})</h3>
            ${data.facts.map(fact => `<div class="fact-item">${fact}</div>`).join('')}
            <h3>Regras (${data.rules.length})</h3>
            ${data.rules.map(rule => `<div class="rule-item">${rule}</div>`).join('')}
        `;
    } catch (error) {
        console.error('Erro ao carregar base de conhecimento:', error);
    }
}

async function runInference() {
    try {
        const response = await fetch('/infer', { method: 'POST' });
        const data = await response.json();

        const resultDiv = document.getElementById('queryResult');
        if (data.total_new > 0) {
            resultDiv.innerHTML = `
                <div class="result-true">
                    ✅ ${data.total_new} novos fatos inferidos!
                </div>
                <div>${data.new_facts.map(fact => `<div class="fact-item">${fact}</div>`).join('')}</div>
            `;
        } else {
            resultDiv.innerHTML = '<div class="result-false">Nenhum novo fato inferido</div>';
        }

        loadKnowledgeBase();
    } catch (error) {
        console.error('Erro ao executar inferência:', error);
    }
}

async function clearKnowledgeBase() {
    if (confirm('Tem certeza que deseja limpar toda a base de conhecimento?')) {
        try {
            const response = await fetch('/clear', { method: 'POST' });
            const data = await response.json();

            alert(data.message);
            loadKnowledgeBase();
            document.getElementById('queryResult').innerHTML = '';
            document.getElementById('proofTree').innerHTML = '';
        } catch (error) {
            console.error('Erro ao limpar base de conhecimento:', error);
        }
    }
}

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        const resultDiv = document.getElementById('uploadResult');

        if (data.error) {
            resultDiv.innerHTML = `<div class="result-false">Erro: ${data.error}</div>`;
        } else {
            resultDiv.innerHTML = `
                <div class="result-true">
                    ✅ Texto processado com sucesso!<br>
                    Fatos extraídos: ${data.total_facts}<br>
                    Regras extraídas: ${data.total_rules}
                </div>
            `;
            loadKnowledgeBase();
        }
    } catch (error) {
        console.error('Erro no upload:', error);
    }
});

document.getElementById('queryForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();

    if (!query) return;

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        const resultDiv = document.getElementById('queryResult');
        const proofDiv = document.getElementById('proofTree');

        if (data.result) {
            resultDiv.innerHTML = `<div class="result-true">✅ Consulta "${query}" é VERDADEIRA</div>`;
        } else {
            resultDiv.innerHTML = `<div class="result-false">❌ Consulta "${query}" é FALSA/DESCONHECIDA</div>`;
        }

        if (data.formatted_proof) {
            proofDiv.innerHTML = `
                <h3>Árvore de Prova:</h3>
                <div class="proof-tree">
                    <pre>${data.formatted_proof}</pre>
                </div>
            `;
        } else if (data.proof && data.proof.length > 0) {
            proofDiv.innerHTML = '<h3>Prova Detalhada:</h3>' + renderProof(data.proof);
        } else {
            proofDiv.innerHTML = '<div>Nenhuma prova disponível</div>';
        }

    } catch (error) {
        console.error('Erro na consulta:', error);
    }
});

function renderProof(proof) {
    if (!proof || proof.length === 0) return '<div>Nenhum passo de prova</div>';

    let html = '<div class="proof-steps">';

    proof.forEach((step) => {
        if (step.type === 'fact') {
            html += `<div class="proof-node fact">
                <strong>Fato Base:</strong> ${step.content}
            </div>`;
        } else if (step.type === 'rule') {
            html += `<div class="proof-node rule">
                <strong>Regra Aplicada:</strong> ${step.rule}<br>
                <strong>Substituição:</strong> ${JSON.stringify(step.substitution)}<br>
                <strong>Conclusão:</strong> ${step.conclusion}
            </div>`;
        }
    });

    html += '</div>';
    return html;
}

document.addEventListener('DOMContentLoaded', loadKnowledgeBase);
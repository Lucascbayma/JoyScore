const searchInput = document.getElementById('game-search-input');
const resultsContainer = document.getElementById('autocomplete-results');
let searchTimeout = null;

const debounce = (func, delay) => {
    return function(...args) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
};

const fetchGames = async (query) => {
    if (query.length < 2 || query.trim() === "") { // Reduzi para 2 caracteres para facilitar o teste
        resultsContainer.innerHTML = '';
        return;
    }

    // ===== CORREÇÃO AQUI =====
    // A URL foi ajustada para '/api/search/' para corresponder ao seu urls.py
    const url = `/api/search/?q=${encodeURIComponent(query)}`;

    try {
        resultsContainer.innerHTML = '<div class="autocomplete-loading">Buscando...</div>';

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Erro HTTP! Status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data.results);

    } catch (error) {
        console.error('Erro ao buscar jogos:', error);
        resultsContainer.innerHTML = '<div class="autocomplete-item error">Erro ao carregar sugestões.</div>';
    }
};

const displayResults = (games) => {
    resultsContainer.innerHTML = '';

    if (games.length === 0) {
        resultsContainer.innerHTML = '<div class="autocomplete-item">Nenhum resultado encontrado.</div>';
        return;
    }

    games.forEach(game => {
        const item = document.createElement('a');
        item.classList.add('autocomplete-item');
        
        // ATENÇÃO: Este link '/jogo/${game.id}/' vai precisar de uma página de detalhes do jogo no futuro.
        // Por enquanto, vamos focar em fazer a busca funcionar.
        item.href = `/avaliar/${game.id}/`; // Alterado para a página de avaliação que já existe

        item.innerHTML = `
            <img src="${game.background_image || '/static/img/default.jpg'}" alt="${game.name}" class="autocomplete-img">
            <span class="autocomplete-name">${game.name}</span>
        `;

        resultsContainer.appendChild(item);
    });
};

if (searchInput && resultsContainer) {
    searchInput.addEventListener('input', debounce((e) => {
        fetchGames(e.target.value.trim());
    }, 400));

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.innerHTML = '';
        }
    });
}
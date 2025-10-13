// CÓDIGO COMPLETO para: jogos_steam/static/jogos_steam/steam_tac_toe.js

document.addEventListener('DOMContentLoaded', () => {

    // --- SELEÇÃO DE ELEMENTOS ---
    const modal = document.getElementById('search-modal');
    const closeModalBtn = document.getElementById('modal-close-btn');
    const gameSlots = document.querySelectorAll('.game-slot');
    const modalGenresText = document.getElementById('modal-genres-text');
    const searchInput = document.getElementById('game-search-input');
    const searchResultsList = document.getElementById('search-results-list');
    // NOVOS ELEMENTOS
    const turnIndicatorText = document.getElementById('turn-text');
    const turnIndicatorImage = document.getElementById('turn-image');
    const resortearBtn = document.getElementById('resortear-btn');

    let activeSlot = null;
    let searchTimeout;
    let currentPlayer = 'team_red'; // Jogador 1 (Vermelho) começa

    // --- NOVA LÓGICA DE TURNO ---
    const updateTurnIndicator = () => {
        if (currentPlayer === 'team_red') {
            turnIndicatorText.textContent = 'Vez do Jogador 1';
            turnIndicatorText.className = 'text-red';
            // Placeholder de imagem vermelha (P1)
            turnIndicatorImage.src = 'https://placehold.co/100x100/e74c3c/FFFFFF?text=P1';
        } else {
            turnIndicatorText.textContent = 'Vez do Jogador 2';
            turnIndicatorText.className = 'text-blue';
            // Placeholder de imagem azul (P2)
            turnIndicatorImage.src = 'https://placehold.co/100x100/3498db/FFFFFF?text=P2';
        }
    };

    // --- LÓGICA DO MODAL E BUSCA ---
    const openModal = (slot) => {
        activeSlot = slot;
        const rowIndex = slot.dataset.row;
        const colIndex = slot.dataset.col;
        const rowGenre = document.getElementById(`label-row-${rowIndex}`).textContent.trim();
        const colGenre = document.getElementById(`label-col-${colIndex}`).textContent.trim();
        modalGenresText.textContent = `${rowGenre} e ${colGenre}`;
        modal.classList.add('visible');
        searchInput.focus();
    };

    const closeModal = () => {
        modal.classList.remove('visible');
        activeSlot = null;
        searchInput.value = '';
        searchResultsList.innerHTML = '';
    };

    const fetchGames = async (query) => {
        if (query.length < 3) {
            searchResultsList.innerHTML = '';
            return;
        }
        searchResultsList.innerHTML = '<li>Buscando...</li>';
        try {
            const response = await fetch(`/steam/api/search-games/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            displayResults(data.games);
        } catch (error) {
            console.error('Erro ao buscar jogos:', error);
            searchResultsList.innerHTML = '<li>Erro ao buscar. Tente novamente.</li>';
        }
    };

    const displayResults = (games) => {
        searchResultsList.innerHTML = '';
        if (games.length === 0) {
            searchResultsList.innerHTML = '<li>Nenhum jogo encontrado.</li>';
            return;
        }
        games.forEach(game => {
            const li = document.createElement('li');
            li.textContent = game.name;
            li.dataset.appid = game.appid;
            li.classList.add('search-result-item');
            li.addEventListener('click', () => handleGameSelection(game.appid));
            searchResultsList.appendChild(li);
        });
    };

    // --- LÓGICA DE VALIDAÇÃO E ATUALIZAÇÃO DO TABULEIRO ---
    const handleGameSelection = async (appid) => {
        if (!activeSlot) return;

        const rowIndex = activeSlot.dataset.row;
        const colIndex = activeSlot.dataset.col;
        const rowGenre = document.getElementById(`label-row-${rowIndex}`).textContent.trim();
        const colGenre = document.getElementById(`label-col-${colIndex}`).textContent.trim();
        const csrftoken = getCookie('csrftoken');

        try {
            const response = await fetch('/steam/api/validate-move/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                },
                body: new URLSearchParams({
                    'appid': appid, 'row_genre': rowGenre, 'col_genre': colGenre,
                }),
            });
            const data = await response.json();

            if (data.success) {
                updateBoard(data.image_url);
            } else {
                alert(data.message || 'Jogada inválida!');
                // Troca o turno mesmo se errar e atualiza o indicador
                currentPlayer = (currentPlayer === 'team_red') ? 'team_blue' : 'team_red';
                updateTurnIndicator();
            }

        } catch (error) {
            console.error('Erro ao validar jogada:', error);
            alert('Ocorreu um erro. Tente novamente.');
        } finally {
            closeModal();
        }
    };

    const updateBoard = (imageUrl) => {
        if (!activeSlot) return;

        activeSlot.innerHTML = '';
        activeSlot.classList.add('played');
        const img = document.createElement('img');
        img.src = imageUrl;
        activeSlot.appendChild(img);

        if (currentPlayer === 'team_red') {
            activeSlot.classList.add('played-slot-red');
            currentPlayer = 'team_blue'; // Passa a vez para o azul
        } else {
            activeSlot.classList.add('played-slot-blue');
            currentPlayer = 'team_red'; // Passa a vez para o vermelho
        }
        // Atualiza o indicador visual após a jogada
        updateTurnIndicator();
    };

    // --- EVENTOS ---
    gameSlots.forEach(slot => {
        slot.addEventListener('click', () => {
            if (!slot.classList.contains('played')) {
                openModal(slot);
            }
        });
    });

    closeModalBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (event) => {
        if (event.target === modal) closeModal();
    });

    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const query = searchInput.value;
        searchTimeout = setTimeout(() => fetchGames(query), 300);
    });

    // NOVO EVENTO: Botão de sortear temas
    resortearBtn.addEventListener('click', () => {
        // A forma mais simples de "sortear" é recarregar a página.
        // O backend já gera novos temas a cada carregamento.
        window.location.reload();
    });

    // Função auxiliar para cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // INICIALIZAÇÃO: Define o indicador de turno quando a página carrega
    updateTurnIndicator();
});
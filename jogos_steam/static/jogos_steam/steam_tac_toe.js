document.addEventListener('DOMContentLoaded', () => {

    // --- Seletores do Jogo Principal ---
    const gameSlots = document.querySelectorAll('.game-slot');
    const headerTurnText = document.getElementById('header-turn-text');
    const p1ScoreDisplay = document.getElementById('p1-score');
    const p2ScoreDisplay = document.getElementById('p2-score');
    const resortearBtn = document.getElementById('resortear-btn');
    const gameStatusBox = document.getElementById('game-status-box');

    // --- Seletores do Modal de Busca ---
    const searchModal = document.getElementById('search-modal');
    const closeSearchModalBtn = document.getElementById('modal-close-btn');
    const modalGenresText = document.getElementById('modal-genres-text');
    const searchInput = document.getElementById('game-search-input');
    const searchResultsList = document.getElementById('search-results-list');
    
    // --- Seletores do Modal de Configurações (NOVOS) ---
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeSettingsModalBtn = document.getElementById('settings-close-btn');
    const themesListContainer = document.getElementById('themes-list');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const settingsFeedback = document.getElementById('settings-feedback');

    // --- Variáveis de Estado ---
    const originalStatusContent = gameStatusBox ? gameStatusBox.innerHTML : '<span>STEAM-TAC-TOE</span>'; 
    let activeSlot = null;
    let searchTimeout;
    let currentPlayer = 'team_red';

    // --- Lógica de Erros e Turnos ---
    const showError = (message) => {
        gameStatusBox.textContent = message; 
        gameStatusBox.classList.add('error-message');
    };

    const hideError = () => {
        gameStatusBox.innerHTML = originalStatusContent; 
        gameStatusBox.classList.remove('error-message');
    };

    const updateTurnIndicator = () => {
        if (!headerTurnText) return;
        headerTurnText.classList.remove('text-red', 'text-blue');
        if (currentPlayer === 'team_red') {
            headerTurnText.textContent = "P1'S TURN";
            headerTurnText.classList.add('text-red');
        } else {
            headerTurnText.textContent = "P2'S TURN";
            headerTurnText.classList.add('text-blue');
        }
    };

    // --- Lógica do Modal de Busca ---
    const openSearchModal = (slot) => {
        hideError(); 
        activeSlot = slot;
        const rowIndex = slot.dataset.row;
        const colIndex = slot.dataset.col;
        const rowGenre = document.getElementById(`label-row-${rowIndex}`).textContent.trim();
        const colGenre = document.getElementById(`label-col-${colIndex}`).textContent.trim();
        modalGenresText.textContent = `${rowGenre} e ${colGenre}`;
        searchModal.classList.add('visible');
        searchInput.focus();
    };

    const closeSearchModal = () => {
        searchModal.classList.remove('visible');
        activeSlot = null;
        searchInput.value = '';
        searchResultsList.innerHTML = '';
    };

    // --- Lógica do Modal de Configurações (NOVA) ---
    const openSettingsModal = () => {
        const allThemes = JSON.parse(document.getElementById('all-themes-data').textContent);
        const currentThemes = JSON.parse(document.getElementById('current-themes-data').textContent);
        
        themesListContainer.innerHTML = ''; // Limpa a lista antes de popular
        settingsFeedback.textContent = ''; // Limpa o feedback

        allThemes.forEach(theme => {
            const isChecked = currentThemes.includes(theme);
            const themeId = `theme-${theme.replace(/\s+/g, '-')}`;
            
            const itemDiv = document.createElement('div');
            itemDiv.className = 'theme-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = themeId;
            checkbox.value = theme;
            checkbox.checked = isChecked;
            
            const label = document.createElement('label');
            label.htmlFor = themeId;
            label.textContent = theme;
            
            itemDiv.appendChild(checkbox);
            itemDiv.appendChild(label);
            themesListContainer.appendChild(itemDiv);

            // Adiciona o listener para validação
            checkbox.addEventListener('click', (event) => {
                const checkedCount = themesListContainer.querySelectorAll('input[type="checkbox"]:checked').length;
                if (checkedCount < 6) {
                    event.preventDefault(); // Impede de desmarcar
                    settingsFeedback.textContent = 'Você deve selecionar pelo menos 6 temas!';
                    setTimeout(() => { settingsFeedback.textContent = ''; }, 2000);
                }
            });
        });

        settingsModal.classList.add('visible');
    };

    const closeSettingsModal = () => {
        settingsModal.classList.remove('visible');
    };

    const saveSettings = () => {
        const selectedThemes = Array.from(themesListContainer.querySelectorAll('input:checked')).map(cb => cb.value);
        
        if (selectedThemes.length < 6) {
            settingsFeedback.textContent = 'Erro: Pelo menos 6 temas devem ser selecionados.';
            return;
        }

        const themesParam = encodeURIComponent(selectedThemes.join(','));
        window.location.href = `${window.location.pathname}?temas=${themesParam}`;
    };

    // --- Comunicação com a API ---
    const fetchGames = async (query) => {
        if (query.length < 3) { searchResultsList.innerHTML = ''; return; }
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
        if (games.length === 0) { searchResultsList.innerHTML = '<li>Nenhum jogo encontrado.</li>'; return; }
        games.forEach(game => {
            const li = document.createElement('li');
            li.textContent = game.name;
            li.dataset.appid = game.appid;
            li.classList.add('search-result-item');
            li.addEventListener('click', () => handleGameSelection(game.appid));
            searchResultsList.appendChild(li);
        });
    };

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
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrftoken },
                body: new URLSearchParams({ 'appid': appid, 'row_genre': rowGenre, 'col_genre': colGenre }),
            });
            const data = await response.json();

            if (data.success) {
                hideError(); 
                updateBoard(data.image_url);
            } else {
                showError(data.message || 'Jogada inválida!'); 
                currentPlayer = (currentPlayer === 'team_red') ? 'team_blue' : 'team_red';
                updateTurnIndicator();
            }
        } catch (error) {
            console.error('Erro ao validar jogada:', error);
            showError('Erro de conexão. Tente novamente.'); 
        } finally {
            closeSearchModal();
        }
    };
    
    // --- Atualização do Tabuleiro ---
    const updateBoard = (imageUrl) => {
        if (!activeSlot) return;
        activeSlot.innerHTML = '';
        activeSlot.classList.add('played');
        const img = document.createElement('img');
        img.src = imageUrl;
        activeSlot.appendChild(img);

        if (currentPlayer === 'team_red') {
            activeSlot.classList.add('played-slot-red');
            currentPlayer = 'team_blue';
        } else {
            activeSlot.classList.add('played-slot-blue');
            currentPlayer = 'team_red';
        }
        updateTurnIndicator();
    };

    // --- Função Utilitária ---
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

    // --- Listeners de Eventos ---
    gameSlots.forEach(slot => {
        slot.addEventListener('click', () => {
            if (!slot.classList.contains('played')) {
                openSearchModal(slot);
            }
        });
    });

    closeSearchModalBtn.addEventListener('click', closeSearchModal);
    searchModal.addEventListener('click', (event) => {
        if (event.target === searchModal) closeSearchModal();
    });
    
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const query = searchInput.value;
        searchTimeout = setTimeout(() => fetchGames(query), 300);
    });

    resortearBtn.addEventListener('click', () => {
        // Mantém os temas customizados ao resortear
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('temas')) {
            window.location.href = `${window.location.pathname}?${urlParams.toString()}`;
        } else {
            window.location.reload();
        }
    });
    
    // Listeners do modal de configurações (NOVOS)
    settingsBtn.addEventListener('click', openSettingsModal);
    closeSettingsModalBtn.addEventListener('click', closeSettingsModal);
    settingsModal.addEventListener('click', (event) => {
        if (event.target === settingsModal) closeSettingsModal();
    });
    saveSettingsBtn.addEventListener('click', saveSettings);

    // --- Inicialização ---
    updateTurnIndicator();
});
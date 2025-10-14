document.addEventListener('DOMContentLoaded', () => {

    // --- Seletores do Jogo Principal ---
    const gameSlots = document.querySelectorAll('.game-slot');
    const headerTurnText = document.getElementById('header-turn-text');
    const p1ScoreDisplay = document.getElementById('p1-score');
    const p2ScoreDisplay = document.getElementById('p2-score');
    const gameStatusBox = document.getElementById('game-status-box');
    const resortearBtn = document.getElementById('resortear-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const skipTurnBtn = document.getElementById('skip-turn-btn'); // NOVO
    const nextRoundBtn = document.getElementById('next-round-btn');

    // --- Seletores do Modal de Busca ---
    const searchModal = document.getElementById('search-modal');
    const closeSearchModalBtn = document.getElementById('modal-close-btn');
    const modalGenresText = document.getElementById('modal-genres-text');
    const searchInput = document.getElementById('game-search-input');
    const searchResultsList = document.getElementById('search-results-list');
    
    // --- Seletores do Modal de Configurações ---
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
    let p1Score = 0;
    let p2Score = 0;
    let gameOver = false;
    let movesMade = 0;
    let boardState = [ [null, null, null], [null, null, null], [null, null, null] ];

    // --- Lógica de Status (Erro, Turno, Vitória) ---
    const showError = (message) => {
        gameStatusBox.textContent = message; 
        gameStatusBox.classList.add('error-message');
    };

    const hideStatusMessages = () => {
        gameStatusBox.innerHTML = originalStatusContent; 
        gameStatusBox.classList.remove('error-message', 'win-message', 'win-p1', 'win-p2', 'draw-message');
    };

    const updateTurnIndicator = () => {
        if (!headerTurnText || gameOver) return;
        headerTurnText.classList.remove('text-red', 'text-blue');
        if (currentPlayer === 'team_red') {
            headerTurnText.textContent = "P1'S TURN";
            headerTurnText.classList.add('text-red');
        } else {
            headerTurnText.textContent = "P2'S TURN";
            headerTurnText.classList.add('text-blue');
        }
    };

    // --- Lógica do Jogo (Vitória, Empate, Reinício) ---
    const checkWinCondition = (player) => {
        for (let i = 0; i < 3; i++) {
            if (boardState[i][0] === player && boardState[i][1] === player && boardState[i][2] === player) return true;
            if (boardState[0][i] === player && boardState[1][i] === player && boardState[2][i] === player) return true;
        }
        if (boardState[0][0] === player && boardState[1][1] === player && boardState[2][2] === player) return true;
        if (boardState[0][2] === player && boardState[1][1] === player && boardState[2][0] === player) return true;
        return false;
    };
    
    const handleWin = (winner) => {
        gameOver = true;
        headerTurnText.textContent = "FIM DE JOGO";
        if (winner === 'team_red') {
            p1Score++;
            p1ScoreDisplay.textContent = p1Score;
            gameStatusBox.textContent = "P1 VENCEU!";
            gameStatusBox.classList.add('win-message', 'win-p1');
        } else {
            p2Score++;
            p2ScoreDisplay.textContent = p2Score;
            gameStatusBox.textContent = "P2 VENCEU!";
            gameStatusBox.classList.add('win-message', 'win-p2');
        }
        toggleActionButtons(true);
    };

    const handleDraw = () => {
        gameOver = true;
        headerTurnText.textContent = "FIM DE JOGO";
        gameStatusBox.textContent = "EMPATE!";
        gameStatusBox.classList.add('draw-message');
        toggleActionButtons(true);
    };

    const startNewRound = () => {
        boardState = [[null, null, null], [null, null, null], [null, null, null]];
        movesMade = 0;
        gameOver = false;
        currentPlayer = 'team_red';
        gameSlots.forEach(slot => {
            slot.innerHTML = '<div class="plus">＋</div>';
            slot.classList.remove('played', 'played-slot-red', 'played-slot-blue');
        });
        hideStatusMessages();
        updateTurnIndicator();
        toggleActionButtons(false);
    };

    const toggleActionButtons = (isGameOver) => {
        resortearBtn.style.display = isGameOver ? 'none' : 'block';
        settingsBtn.style.display = isGameOver ? 'none' : 'block';
        skipTurnBtn.style.display = isGameOver ? 'none' : 'block'; // ATUALIZADO
        nextRoundBtn.style.display = isGameOver ? 'block' : 'none';
    };

    // --- Lógica do Modal de Busca ---
    const openSearchModal = (slot) => {
        hideStatusMessages();
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

    // --- Lógica do Modal de Configurações ---
    const openSettingsModal = () => {
        const allThemes = JSON.parse(document.getElementById('all-themes-data').textContent);
        const currentThemes = JSON.parse(document.getElementById('current-themes-data').textContent);
        themesListContainer.innerHTML = '';
        settingsFeedback.textContent = '';
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
            checkbox.addEventListener('click', (event) => {
                const checkedCount = themesListContainer.querySelectorAll('input[type="checkbox"]:checked').length;
                if (checkedCount < 6) {
                    event.preventDefault();
                    settingsFeedback.textContent = 'Você deve selecionar pelo menos 6 temas!';
                    setTimeout(() => { settingsFeedback.textContent = ''; }, 2000);
                }
            });
        });
        settingsModal.classList.add('visible');
    };

    const closeSettingsModal = () => settingsModal.classList.remove('visible');

    const saveSettings = () => {
        const selectedThemes = Array.from(themesListContainer.querySelectorAll('input:checked')).map(cb => cb.value);
        if (selectedThemes.length < 6) {
            settingsFeedback.textContent = 'Erro: Pelo menos 6 temas devem ser selecionados.';
            return;
        }
        const themesParam = encodeURIComponent(selectedThemes.join(','));
        window.location.href = `${window.location.pathname}?temas=${themesParam}`;
    };

    // --- Comunicação com a API e atualização do Tabuleiro ---
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
                hideStatusMessages();
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
    
    const updateBoard = (imageUrl) => {
        if (!activeSlot) return;
        const playerWhoMoved = currentPlayer;
        const row = parseInt(activeSlot.dataset.row, 10);
        const col = parseInt(activeSlot.dataset.col, 10);

        boardState[row][col] = playerWhoMoved;
        movesMade++;

        activeSlot.innerHTML = '';
        activeSlot.classList.add('played');
        const img = document.createElement('img');
        img.src = imageUrl;
        activeSlot.appendChild(img);

        activeSlot.classList.add(playerWhoMoved === 'team_red' ? 'played-slot-red' : 'played-slot-blue');

        if (checkWinCondition(playerWhoMoved)) {
            handleWin(playerWhoMoved);
        } else if (movesMade === 9) {
            handleDraw();
        } else {
            currentPlayer = (playerWhoMoved === 'team_red') ? 'team_blue' : 'team_red';
            updateTurnIndicator();
        }
    };

    // --- Utilitários e Listeners ---
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

    gameSlots.forEach(slot => {
        slot.addEventListener('click', () => {
            if (!slot.classList.contains('played') && !gameOver) {
                openSearchModal(slot);
            }
        });
    });

    closeSearchModalBtn.addEventListener('click', closeSearchModal);
    searchModal.addEventListener('click', (event) => { if (event.target === searchModal) closeSearchModal(); });
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => fetchGames(searchInput.value), 300);
    });
    resortearBtn.addEventListener('click', () => {
        const urlParams = new URLSearchParams(window.location.search);
        window.location.href = urlParams.has('temas') ? `${window.location.pathname}?${urlParams.toString()}` : window.location.pathname;
    });
    
    // NOVO LISTENER PARA PULAR A VEZ
    skipTurnBtn.addEventListener('click', () => {
        if (gameOver) return; // Não faz nada se o jogo acabou
        currentPlayer = (currentPlayer === 'team_red') ? 'team_blue' : 'team_red';
        updateTurnIndicator();
    });

    settingsBtn.addEventListener('click', openSettingsModal);
    closeSettingsModalBtn.addEventListener('click', closeSettingsModal);
    settingsModal.addEventListener('click', (event) => { if (event.target === settingsModal) closeSettingsModal(); });
    saveSettingsBtn.addEventListener('click', saveSettings);
    nextRoundBtn.addEventListener('click', startNewRound);

    // --- Inicialização ---
    updateTurnIndicator();
});
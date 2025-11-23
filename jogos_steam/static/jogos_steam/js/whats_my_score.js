document.addEventListener('DOMContentLoaded', () => {
    const gameCardArea = document.getElementById('game-card-area');
    const comparisonDisplay = document.getElementById('comparison-display');
    const questionArea = document.getElementById('game-question-area');
    const resultMessage = document.getElementById('result-message');
    const currentStreakEl = document.getElementById('current-streak');
    const maxStreakEl = document.getElementById('max-streak');
    const btnHigher = document.getElementById('btn-higher');
    const btnLower = document.getElementById('btn-lower');
    const questionGame1NameEl = document.getElementById('question-game1-name'); 
    
    const API_ENDPOINT = '/steam/api/get-metacritic-games/'; 

    let currentGameState = null;
    let currentStreak = 0;
    let maxStreak = parseInt(localStorage.getItem('wmsMaxStreak') || '0', 10);
    
    let usedAppIds = []; 

    function updateScores(isCorrect) {
        if (isCorrect) {
            currentStreak++;
            if (currentStreak > maxStreak) {
                maxStreak = currentStreak;
                localStorage.setItem('wmsMaxStreak', maxStreak);
            }
        } else {
            currentStreak = 0;
            usedAppIds = []; 
        }
        currentStreakEl.textContent = currentStreak;
        maxStreakEl.textContent = maxStreak;
    }

    function disableButtons(disabled) {
        btnHigher.disabled = disabled;
        btnLower.disabled = disabled;
    }

    function resetGameUI() {
        gameCardArea.classList.add('loading');
        comparisonDisplay.style.display = 'none';
        questionArea.style.display = 'none';
        
        resultMessage.textContent = ''; 
        resultMessage.className = 'result-message'; 

        disableButtons(true);
        
        const scoreBox2 = document.getElementById('game2-score-box');
        const scoreText2 = document.getElementById('game2-score');

        if (scoreBox2 && scoreText2) {
            scoreBox2.classList.remove('score-visible');
            scoreBox2.classList.add('score-hidden');
            scoreText2.textContent = '?';
        }
    }

    function loadNewGame(mode = 'initial') {
        const loadingTextEl = document.getElementById('loading-message');
        if (loadingTextEl) {
            loadingTextEl.textContent = 'Carregando jogos...';
        }

        if (gameCardArea.classList.contains('loading') && mode !== 'initial' && currentGameState) return;

        resetGameUI();

        let fetchUrl = API_ENDPOINT;

        if (mode === 'rotation' && currentGameState) {
            const excludeList = usedAppIds.join(',');
            const scoreToExclude = currentGameState.game2.correct_metascore; 
            
            fetchUrl += `?exclude_appids=${excludeList}&current_score=${scoreToExclude}`;
        }
        
        fetch(fetchUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro de Servidor HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (loadingTextEl) {
                    loadingTextEl.textContent = '';
                }

                if (data.success) {
                    if (data.mode === 'initial') {
                        currentGameState = { game1: data.game1, game2: data.game2 };
                        usedAppIds = [data.game1.appid, data.game2.appid];

                    } else if (data.mode === 'rotation') {
                        const oldGame2 = currentGameState.game2;
                        
                        currentGameState.game1 = {
                            name: oldGame2.name,
                            image_url: oldGame2.image_url,
                            metascore: oldGame2.correct_metascore,
                            appid: oldGame2.appid
                        };
                        
                        currentGameState.game2 = {
                            name: data.game_data.name,
                            image_url: data.game_data.image_url,
                            appid: data.game_data.appid,
                            correct_metascore: data.game_data.correct_metascore,
                        };
                        usedAppIds.push(data.game_data.appid);
                    }
                    
                    renderGameUI();
                    
                } else {
                    document.getElementById('loading-message').textContent = data.message || "Erro desconhecido. Recarregando...";
                    gameCardArea.classList.remove('loading');
                    disableButtons(true);
                    
                    if (data.message.includes("nota diferente")) {
                         setTimeout(() => loadNewGame('initial'), 5000); 
                    } else {
                        usedAppIds = []; 
                        setTimeout(() => loadNewGame('initial'), 5000); 
                    }
                }
            })
            .catch(error => {
                console.error('Erro de rede ou Servidor:', error);
                document.getElementById('loading-message').textContent = `Falha na comunicação: ${error.message}. Recarregando...`;
                gameCardArea.classList.remove('loading');
                disableButtons(true);
                setTimeout(() => loadNewGame('initial'), 5000); 
            });
    }

    function renderGameUI() {
        const game1 = currentGameState.game1;
        const game2 = currentGameState.game2;

        document.getElementById('game1-name').textContent = game1.name;
        document.getElementById('game1-image').src = game1.image_url;
        document.getElementById('game1-score').textContent = game1.metascore;

        document.getElementById('game2-name').textContent = game2.name;
        document.getElementById('game2-image').src = game2.image_url;
        
        questionGame1NameEl.textContent = game1.name; 
        
        document.getElementById('btn-higher').innerHTML = `MAIOR que ${game2.name}`;
        document.getElementById('btn-lower').innerHTML = `MENOR que ${game2.name}`;

        gameCardArea.classList.remove('loading');
        comparisonDisplay.style.display = 'flex';
        questionArea.style.display = 'block';
        disableButtons(false);
    }


    function revealAnswer(isCorrect) {
        const scoreBox2 = document.getElementById('game2-score-box');
        const scoreText2 = document.getElementById('game2-score');

        scoreText2.textContent = currentGameState.game2.correct_metascore;
        scoreBox2.classList.remove('score-hidden');
        scoreBox2.classList.add('score-visible');
        
        disableButtons(true);
        
        if (isCorrect) {
            updateScores(true);
            resultMessage.textContent = 'Parabéns, você acertou! Próximo desafio em 5 segundos.';
            resultMessage.classList.add('success');
            
            setTimeout(() => {
                loadNewGame('rotation');
            }, 5000); 

        } else {
            updateScores(false); 
            resultMessage.textContent = `Que pena! A nota do outro jogo era ${currentGameState.game2.correct_metascore}. Novo jogo em 5 segundos.`;
            resultMessage.classList.add('error');
            
            setTimeout(() => {
                loadNewGame('initial');
            }, 5000); 
        }
    }

    function handleAnswer(choice) {
        if (!currentGameState) return;

        const game1Score = currentGameState.game1.metascore;
        const game2Score = currentGameState.game2.correct_metascore;
        
        const isHigher = game1Score > game2Score; 
        const isCorrect = (choice === 'higher' && isHigher) || (choice ==='lower' && !isHigher);
        
        revealAnswer(isCorrect);
    }

    updateScores();

    btnHigher.addEventListener('click', () => handleAnswer('higher'));
    btnLower.addEventListener('click', () => handleAnswer('lower'));
    
    loadNewGame('initial');
});
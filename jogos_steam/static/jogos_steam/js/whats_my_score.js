document.addEventListener('DOMContentLoaded', () => {
    // Elementos DOM e Variáveis de Estado
    const gameCardArea = document.getElementById('game-card-area');
    const comparisonDisplay = document.getElementById('comparison-display');
    const questionArea = document.getElementById('game-question-area');
    const resultMessage = document.getElementById('result-message');
    const currentStreakEl = document.getElementById('current-streak');
    const maxStreakEl = document.getElementById('max-streak');
    const btnHigher = document.getElementById('btn-higher');
    const btnLower = document.getElementById('btn-lower');
    // Elementos da Pergunta
    const questionGame1NameEl = document.getElementById('question-game1-name'); 
    
    // URL da API
    const API_ENDPOINT = '/steam/api/get-metacritic-games/'; 

    let currentGameState = null;
    let currentStreak = 0;
    let maxStreak = parseInt(localStorage.getItem('wmsMaxStreak') || '0', 10);
    
    // Lista de AppIDs usados na streak atual para evitar repetição.
    let usedAppIds = []; 

    // --- Funções de Placar e Botões ---
    function updateScores(isCorrect) {
        if (isCorrect) {
            currentStreak++;
            if (currentStreak > maxStreak) {
                maxStreak = currentStreak;
                localStorage.setItem('wmsMaxStreak', maxStreak);
            }
        } else {
            currentStreak = 0;
            usedAppIds = []; // ZERA A LISTA DE JOGOS USADOS APÓS PERDER
        }
        currentStreakEl.textContent = currentStreak;
        maxStreakEl.textContent = maxStreak;
    }

    function disableButtons(disabled) {
        btnHigher.disabled = disabled;
        btnLower.disabled = disabled;
    }

    function resetGameUI() {
        // Exibe a área de carregamento
        gameCardArea.classList.add('loading');
        comparisonDisplay.style.display = 'none';
        questionArea.style.display = 'none';
        
        // ⚠️ CORREÇÃO 1: Limpa a mensagem de resultado da rodada anterior
        resultMessage.textContent = ''; 
        resultMessage.className = 'result-message'; 

        disableButtons(true);
        
        // Resetar o quadrado da nota do Jogo 2
        const scoreBox2 = document.getElementById('game2-score-box');
        const scoreText2 = document.getElementById('game2-score');

        if (scoreBox2 && scoreText2) {
            scoreBox2.classList.remove('score-visible');
            scoreBox2.classList.add('score-hidden');
            scoreText2.textContent = '?';
        }
    }

    // --- Função Principal de Busca de Jogo ---
    function loadNewGame(mode = 'initial') {
        const loadingTextEl = document.getElementById('loading-message');
        if (loadingTextEl) {
            loadingTextEl.textContent = 'Carregando jogos...';
        }

        // Trava para evitar cliques duplos durante o carregamento
        if (gameCardArea.classList.contains('loading') && mode !== 'initial' && currentGameState) return;

        resetGameUI();

        let fetchUrl = API_ENDPOINT;

        // Se for rotação, envia a lista de jogos excluídos (AppIDs) E a nota do jogo atual
        if (mode === 'rotation' && currentGameState) {
            const excludeList = usedAppIds.join(',');
            
            // ⬇️ --- ALTERAÇÃO AQUI --- ⬇️
            // Pega a nota do Jogo 2 (que acabou de ser revelado e vai para a esquerda)
            // para que a API não retorne um novo jogo com a mesma nota.
            const scoreToExclude = currentGameState.game2.correct_metascore; 
            
            fetchUrl += `?exclude_appids=${excludeList}&current_score=${scoreToExclude}`;
            // ⬆️ --- FIM DA ALTERAÇÃO --- ⬆️

        }
        
        fetch(fetchUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro de Servidor HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Ao receber resposta, limpa a mensagem de carregamento inicial
                if (loadingTextEl) {
                    loadingTextEl.textContent = '';
                }

                if (data.success) {
                    // --- Lógica de Processamento de Dados do Backend ---
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
                    
                    // --- Renderiza a tela ---
                    renderGameUI();
                    
                } else {
                    document.getElementById('loading-message').textContent = data.message || "Erro desconhecido. Recarregando...";
                    gameCardArea.classList.remove('loading');
                    disableButtons(true);
                    
                    // Se o erro for sobre "não encontrar jogo com nota diferente", 
                    // apenas reinicia o jogo para o usuário não ficar preso.
                    if (data.message.includes("nota diferente")) {
                         // Apenas espera 5s e recomeça do zero
                         setTimeout(() => loadNewGame('initial'), 5000); 
                    } else {
                        // Se for outro erro (ex: 100 jogos), reinicia o pool
                        usedAppIds = []; // Zera o pool
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

        // Atualiza UI para Game 1
        document.getElementById('game1-name').textContent = game1.name;
        document.getElementById('game1-image').src = game1.image_url;
        document.getElementById('game1-score').textContent = game1.metascore;

        // Atualiza UI para Game 2
        document.getElementById('game2-name').textContent = game2.name;
        document.getElementById('game2-image').src = game2.image_url;
        
        // ⚠️ CORREÇÃO 2: Pergunta: A nota Metacritic de [Jogo da ESQUERDA] é:
        questionGame1NameEl.textContent = game1.name; 
        
        // ⚠️ CORREÇÃO 2: Botões: MAIOR/MENOR que [Jogo da DIREITA]
        document.getElementById('btn-higher').innerHTML = `MAIOR que ${game2.name}`;
        document.getElementById('btn-lower').innerHTML = `MENOR que ${game2.name}`;

        // Exibe a área do jogo
        gameCardArea.classList.remove('loading');
        comparisonDisplay.style.display = 'flex';
        questionArea.style.display = 'block';
        disableButtons(false);
    }


    function revealAnswer(isCorrect) {
        const scoreBox2 = document.getElementById('game2-score-box');
        const scoreText2 = document.getElementById('game2-score');

        // Revela a nota correta
        scoreText2.textContent = currentGameState.game2.correct_metascore;
        scoreBox2.classList.remove('score-hidden');
        scoreBox2.classList.add('score-visible');
        
        disableButtons(true);
        
        if (isCorrect) {
            updateScores(true);
            resultMessage.textContent = 'Parabéns, você acertou! Próximo desafio em 5 segundos.';
            resultMessage.classList.add('success');
            
            // ROTAÇÃO
            setTimeout(() => {
                loadNewGame('rotation');
            }, 5000); 

        } else {
            updateScores(false); 
            resultMessage.textContent = `Que pena! A nota do outro jogo era ${currentGameState.game2.correct_metascore}. Novo jogo em 5 segundos.`;
            resultMessage.classList.add('error');
            
            // MODO INICIAL (Totalmente novos)
            setTimeout(() => {
                loadNewGame('initial');
            }, 5000); 
        }
    }

    function handleAnswer(choice) {
        if (!currentGameState) return;

        const game1Score = currentGameState.game1.metascore;
        const game2Score = currentGameState.game2.correct_metascore;
        
        // ⚠️ CORREÇÃO 2: Lógica de Resposta: Jogo 1 é MAIOR que Jogo 2?
        const isHigher = game1Score > game2Score; 
        const isCorrect = (choice === 'higher' && isHigher) || (choice ==='lower' && !isHigher);
        
        revealAnswer(isCorrect);
    }

    // --- Inicialização ---
    updateScores();

    // Adiciona event listeners aos botões
    btnHigher.addEventListener('click', () => handleAnswer('higher'));
    btnLower.addEventListener('click', () => handleAnswer('lower'));
    
    // Inicia o jogo
    loadNewGame('initial');
});
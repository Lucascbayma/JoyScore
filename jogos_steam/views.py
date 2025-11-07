import random
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import time 
import sys 
import json 

# --- Funções de Utilitário (MANTIDAS) ---

def normalize_genre(genre_string):
    """Converte uma string de gênero para um formato padronizado."""
    return genre_string.lower().replace('-', '').replace(' ', '')

ALL_AVAILABLE_THEMES = [
    "Action", "Indie", "Adventure", "RPG", "Strategy", "Simulation",
    "Casual", "Sports", "Racing", "Violent", "Single-player", "Multi-player",
    "Free to Play", "Early Access", "Massively Multiplayer", "Co-op"
]

# LISTA FIXA DE 100 APPIDS DE ALTA QUALIDADE
HIGH_RATED_APPIDS = [
    620, 292030, 1245620, 105600, 892970, 379430, 730, 1174180, 230410, 386210, 
    550, 4000, 3830, 20920, 22370, 41000, 48700, 57095, 61767, 200710, 203160, 
    209270, 219640, 238320, 238460, 239140, 250900, 255710, 268590, 275850, 295110, 
    298110, 305620, 310560, 346110, 368020, 377840, 413150, 431600, 457140, 460790, 
    489830, 546560, 582010, 588650, 612880, 644830, 646570, 678800, 750920, 814380, 
    933110, 960170, 990080, 1091500, 1094040, 1184370, 1203620, 1313380, 1373500, 
    1426210, 1449850, 1465360, 1506830, 1612400, 1675200, 1745780, 1817080, 19380, 
    21360, 391540, 39190, 50620, 239160, 294100, 345350, 353380, 377160, 383980, 
    397550, 413080, 451340, 520270, 548430, 588430, 594650, 606830, 648350, 702890, 
    753640, 952060, 976730, 1097840, 11270, 211830, 218620, 289070, 319630, 367520, 
    412020, 49520, 578080, 698780, 774880, 920210, 1118310, 1289380, 1203620, 1449850 
]

STEAM_APPS = [{'appid': appid, 'name': str(appid)} for appid in HIGH_RATED_APPIDS]
print(f"\n[STEAM API - FINAL] {len(STEAM_APPS)} AppIDs de ALTA QUALIDADE carregados (Servidor Instantâneo).", file=sys.stderr, flush=True)

# --- Views e APIs do Steam Tac Toe (MANTIDAS) ---

def steam_tac_toe_view(request):
    """Renderiza a página principal do jogo Steam Tac Toe."""
    custom_themes_str = request.GET.get('temas')
    
    if custom_themes_str:
        custom_themes_list = [theme.strip() for theme in custom_themes_str.split(',')]
        valid_themes = [theme for theme in custom_themes_list if theme in ALL_AVAILABLE_THEMES]
        themes_to_use = valid_themes if len(valid_themes) >= 6 else ALL_AVAILABLE_THEMES
    else:
        themes_to_use = ALL_AVAILABLE_THEMES
    
    num_to_sample = min(6, len(themes_to_use))
    generos_escolhidos = random.sample(themes_to_use, num_to_sample)
    
    while len(generos_escolhidos) < 6:
        fallback_theme = random.choice(ALL_AVAILABLE_THEMES)
        if fallback_theme not in generos_escolhidos:
            generos_escolhidos.append(fallback_theme)

    context = {
        'linhas': generos_escolhidos[:3],
        'colunas': generos_escolhidos[3:],
        'todos_os_temas': ALL_AVAILABLE_THEMES,
        'temas_atuais': themes_to_use,
    }
    return render(request, 'jogos_steam/steam_tac_toe.html', context)


def search_steam_games_api(request):
    """API para buscar jogos pelo nome a partir da lista pré-carregada."""
    query = request.GET.get('q', '').lower()
    if not query or len(query) < 3: 
        return JsonResponse({'games': []})
    
    results = [app for app in STEAM_APPS if query in app.get('name', '').lower()]
    return JsonResponse({'games': results[:10]})

def validate_game_move_api(request):
    """API para validar se um jogo pertence a dois gêneros específicos."""
    if request.method == 'POST':
        appid = request.POST.get('appid', '').strip()
        row_genre = request.POST.get('row_genre', '').strip()
        col_genre = request.POST.get('col_genre', '').strip()

        if not all([appid, row_genre, col_genre]):
            return JsonResponse({'success': False, 'message': 'Dados incompletos.'}, status=400)
        
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get(appid) or not data[appid]['success']: 
                return JsonResponse({'success': False, 'message': 'Não foi possível encontrar detalhes para este jogo.'})

            game_data = data[appid]['data']
            game_name = game_data.get('name', 'Este jogo')
            
            game_genres = [g['description'] for g in game_data.get('genres', [])]
            game_categories = [c['description'] for c in game_data.get('categories', [])]
            all_tags_from_api = game_genres + game_categories

            normalized_row = normalize_genre(row_genre)
            normalized_col = normalize_genre(col_genre)
            all_normalized_tags = {normalize_genre(tag) for tag in all_tags_from_api}

            if normalized_row in all_normalized_tags and normalized_col in all_normalized_tags:
                return JsonResponse({'success': True, 'image_url': game_data.get('header_image')})
            else:
                valid_genres_for_bingo = [
                    theme for theme in ALL_AVAILABLE_THEMES 
                    if normalize_genre(theme) in all_normalized_tags
                ]

                if not valid_genres_for_bingo:
                    message = f"Não foi possível validar os gêneros de '{game_name}' com os temas do bingo."
                else:
                    genres_str = ', '.join(valid_genres_for_bingo)
                    message = f"Jogada inválida! '{game_name}' não se encaixa em '{row_genre}' e '{col_genre}'. No bingo, os temas dele são: {genres_str}."
                
                return JsonResponse({'success': False, 'message': message})

        except requests.exceptions.RequestException:
            return JsonResponse({'success': False, 'message': 'Erro de conexão ao consultar a API da Steam.'}, status=500)
        except KeyError:
            return JsonResponse({'success': False, 'message': 'Erro ao processar a resposta da API da Steam.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)


# --- Funções do NOVO JOGO: WHAT'S MY SCORE ---

def get_game_details_and_metascore(appid):
    """Busca os detalhes do jogo, incluindo o Metascore (nota Metacritic)."""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=br&l=pt"
    
    # DELAY CRÍTICO: 2.0 SEGUNDOS
    time.sleep(2.0) 
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if not data.get(str(appid)) or not data[str(appid)]['success']:
            return None
            
        game_data = data[str(appid)]['data']
        
        # Filtro de nota: Metacritic >= 70
        metacritic = game_data.get('metacritic')
        
        if metacritic:
            metascore_value = metacritic.get('score', 0)
            
            if metascore_value >= 70:
                return {
                    'name': game_data.get('name'),
                    'appid': appid,
                    'metascore': metascore_value,
                    'image_url': game_data.get('header_image'), 
                }
        return None 
        
    except requests.exceptions.RequestException as e:
        print(f"[STEAM API - DEBUG] ERRO CONEXÃO Detalhes: AppID {appid}. Mensagem: {e}", file=sys.stderr, flush=True)
        return None
    except KeyError:
        return None


def get_one_unique_high_rated_game(exclude_appids):
    """Tenta encontrar UM jogo com Metacritic >= 70, excluindo os AppIDs fornecidos."""
    
    attempts = 0
    MAX_ATTEMPTS = 500 
    
    attempted_appids = set(exclude_appids) 
    
    if not STEAM_APPS:
        return None
        
    print(f"[STEAM API - DEBUG] 2. Iniciando busca por 1 novo jogo (Excluindo: {len(exclude_appids)} AppIDs)...", file=sys.stderr, flush=True)

    available_apps = [app for app in STEAM_APPS if app.get('appid') not in attempted_appids]
    
    if not available_apps:
        print("[STEAM API - DEBUG] SUCESSO! 100 jogos foram usados. O pool será REINICIADO.", file=sys.stderr, flush=True)
        return None 
        
    while attempts < MAX_ATTEMPTS:
        attempts += 1
            
        random_app = random.choice(available_apps)
        appid = random_app.get('appid')

        if not appid or appid in attempted_appids:
            continue
        
        attempted_appids.add(appid)
            
        game_details = get_game_details_and_metascore(appid)
        
        if game_details:
            print(f"[STEAM API - DEBUG] Encontrado Jogo: {game_details['name']} (Tentativa: {attempts})", file=sys.stderr, flush=True)
            return game_details
        
    print(f"[STEAM API - DEBUG] FALHA! Nenhum jogo qualificado encontrado em {attempts} tentativas.", file=sys.stderr, flush=True)
    return None 

def get_two_unique_high_rated_games():
    """Busca os dois primeiros jogos, garantindo notas diferentes."""
    game1 = get_one_unique_high_rated_game(exclude_appids=[])
    if not game1:
        return None, None
        
    game2 = None
    attempts = 0
    MAX_INNER_ATTEMPTS = 15
    
    while not game2 and attempts < MAX_INNER_ATTEMPTS:
        # ⚠️ CORREÇÃO DO NOME DO PARÂMETRO
        game2_candidate = get_one_unique_high_rated_game(exclude_appids=[game1['appid']])
        
        if game2_candidate and game2_candidate['metascore'] != game1['metascore']:
            game2 = game2_candidate
        
        attempts += 1

    return game1, game2 


# View para renderizar a página do jogo (MANTIDA)
def whats_my_score_view(request):
    """Renderiza a página principal do jogo What's My Score."""
    return render(request, 'jogos_steam/whats_my_score.html')

# A view que irá buscar os dados via AJAX e enviá-los de volta (LÓGICA DE ROTAÇÃO)
def get_metacritic_games_api(request):
    """Endpoint API que retorna jogos para o What's My Score."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
        
    if not STEAM_APPS:
        return JsonResponse({'success': False, 'message': 'Erro de Inicialização: A lista de 100 AppIDs de teste está vazia.'}, status=503)
    
    # --- Lógica de Rotação (Se houver parâmetros de exclusão) ---
    exclude_ids_str = request.GET.get('exclude_appids', '')
    
    # 1. Modo de Rotação (carregar apenas 1 novo jogo)
    if exclude_ids_str:
        try:
            exclude_ids = [int(x.strip()) for x in exclude_ids_str.split(',') if x.strip()]
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Parâmetros de AppID inválidos.'}, status=400)

        # Busca apenas um novo jogo (o game2)
        # ⚠️ CORREÇÃO DO NOME DO PARÂMETRO
        new_game = get_one_unique_high_rated_game(exclude_appids=exclude_ids)
        
        if new_game:
            response_data = {
                'success': True,
                'mode': 'rotation',
                'game_data': {
                    'name': new_game['name'],
                    'image_url': new_game['image_url'],
                    'appid': new_game['appid'],
                    'correct_metascore': new_game['metascore'], 
                }
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'message': 'Parabéns, você usou todos os 100 jogos! Recarregue para reiniciar o pool.'})

    # 2. Modo de Inicialização (carregar 2 novos jogos)
    else:
        game1, game2 = get_two_unique_high_rated_games()
        
        if game1 and game2:
            games_pair = random.sample([game1, game2], 2)
            
            response_data = {
                'success': True,
                'mode': 'initial',
                'game1': {
                    'name': games_pair[0]['name'],
                    'image_url': games_pair[0]['image_url'],
                    'metascore': games_pair[0]['metascore'], 
                    'appid': games_pair[0]['appid'],
                },
                'game2': {
                    'name': games_pair[1]['name'],
                    'image_url': games_pair[1]['image_url'],
                    'appid': games_pair[1]['appid'],
                    'correct_metascore': games_pair[1]['metascore'], 
                },
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'message': 'O jogo não pôde ser carregado. Não foram encontrados dois jogos qualificados com notas diferentes.'})
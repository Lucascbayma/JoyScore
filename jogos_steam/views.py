import random
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import time 
import sys 
import json 

# --- Funções de Utilitário ---
def normalize_genre(genre_string):
    # Remove espaços, hifens e deixa minúsculo para facilitar a comparação
    # Ex: "Single-player" vira "singleplayer"
    return genre_string.lower().replace('-', '').replace(' ', '')

ALL_AVAILABLE_THEMES = [
    "Action", "Indie", "Adventure", "RPG", "Strategy", "Simulation",
    "Casual", "Sports", "Racing", "Violent", "Single-player", "Multi-player",
    "Free to Play", "Early Access", "Massively Multiplayer", "Co-op"
]

# --- LISTA DE ELITE: JOGOS FAMOSOS ---
TOP_FAMOUS_GAMES = [
    {'appid': 730, 'name': 'Counter-Strike 2'}, {'appid': 570, 'name': 'Dota 2'},
    {'appid': 271590, 'name': 'Grand Theft Auto V'}, {'appid': 1172470, 'name': 'Apex Legends'},
    {'appid': 1245620, 'name': 'Elden Ring'}, {'appid': 1091500, 'name': 'Cyberpunk 2077'},
    {'appid': 292030, 'name': 'The Witcher 3: Wild Hunt'}, {'appid': 1086940, 'name': 'Baldur\'s Gate 3'},
    {'appid': 2215430, 'name': 'Ghost of Tsushima'}, {'appid': 413150, 'name': 'Stardew Valley'},
    {'appid': 105600, 'name': 'Terraria'}, {'appid': 1174180, 'name': 'Red Dead Redemption 2'},
    {'appid': 489830, 'name': 'The Elder Scrolls V: Skyrim'}, {'appid': 3096070, 'name': 'Ghost of Yotei'},
    {'appid': 1145360, 'name': 'Hades'}, {'appid': 945360, 'name': 'Among Us'},
    {'appid': 397540, 'name': 'Borderlands 3'}, {'appid': 239140, 'name': 'Dying Light'},
    {'appid': 1623730, 'name': 'Palworld'}, {'appid': 553850, 'name': 'HELLDIVERS 2'},
    {'appid': 230410, 'name': 'Warframe'}, {'appid': 359550, 'name': 'Rainbow Six Siege'},
    {'appid': 252490, 'name': 'Rust'}, {'appid': 578080, 'name': 'PUBG: BATTLEGROUNDS'}
]

# --- FONTE DE DADOS 1: "WHAT'S MY SCORE" ---
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
WMS_APP_POOL = [{'appid': appid, 'name': str(appid)} for appid in HIGH_RATED_APPIDS]
print(f"\n[WMS API] {len(WMS_APP_POOL)} AppIDs de ALTA QUALIDADE carregados para 'What's My Score'.", file=sys.stderr, flush=True)

# --- FONTE DE DADOS 2: "STEAM TAC TOE" ---
def load_steam_app_list():
    print("\n[STEAM TAC TOE] Pronto. Modo 'Live Search' (Store) ativado.", file=sys.stderr, flush=True)

# --- Views ---

def steam_tac_toe_view(request):
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
    """
    Busca jogos e FABRICA a imagem correta para garantir que ela exista.
    """
    query = request.GET.get('q', '').strip().lower()
    if not query or len(query) < 2: 
        return JsonResponse({'games': []})
    
    results = []
    
    # 1. Busca na Lista Local (Top Games)
    for game in TOP_FAMOUS_GAMES:
        if query in game['name'].lower():
            img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{game['appid']}/header.jpg"
            results.append({'appid': game['appid'], 'name': game['name'], 'image': img_url})
            
    # 2. Busca na Loja (Para todo o resto)
    url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=portuguese&cc=BR"
    
    try:
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            local_ids = {g['appid'] for g in results}
            
            for item in items:
                if item['id'] not in local_ids:
                    manual_image = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{item['id']}/header.jpg"
                    results.append({'appid': item['id'], 'name': item['name'], 'image': manual_image})
    except Exception:
        pass 
            
    return JsonResponse({'games': results[:10]})

def validate_game_move_api(request):
    """
    Valida a jogada pedindo dados em INGLÊS para bater com a lista de temas.
    """
    if request.method == 'POST':
        appid = request.POST.get('appid', '').strip()
        row_genre = request.POST.get('row_genre', '').strip()
        col_genre = request.POST.get('col_genre', '').strip()

        if not all([appid, row_genre, col_genre]):
            return JsonResponse({'success': False, 'message': 'Dados incompletos.'}, status=400)
        
        # [IMPORTANTE] l=english garante que "Single-player" venha como "Single-player"
        # e não "Um jogador", para bater com a sua lista ALL_AVAILABLE_THEMES.
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=8)
            data = response.json()

            if not data.get(str(appid)) or not data[str(appid)]['success']: 
                return JsonResponse({'success': False, 'message': 'Erro ao verificar detalhes do jogo.'})

            game_data = data[str(appid)]['data']
            game_name = game_data.get('name', 'Este jogo')
            image_url = game_data.get('header_image')
            
            # Coleta Gêneros e Categorias da API
            # Categories é onde fica "Single-player", "Multi-player", "Co-op"
            # Genres é onde fica "Action", "RPG", "Indie"
            genres_api = [g['description'] for g in game_data.get('genres', [])]
            categories_api = [c['description'] for c in game_data.get('categories', [])]
            
            all_tags = genres_api + categories_api
            
            # Normaliza tudo para comparação
            norm_row = normalize_genre(row_genre)
            norm_col = normalize_genre(col_genre)
            all_norm_tags = {normalize_genre(tag) for tag in all_tags}
            
            # DEBUG: Mostra no terminal o que a Steam devolveu (em inglês)
            print(f"\n[VALIDAÇÃO] Jogo: {game_name}", file=sys.stderr)
            print(f"Tags Steam (EN): {all_tags}", file=sys.stderr)
            print(f"Bingo Pede: {row_genre} & {col_genre}", file=sys.stderr)

            if norm_row in all_norm_tags and norm_col in all_norm_tags:
                return JsonResponse({'success': True, 'image_url': image_url})
            else:
                # Filtra apenas os gêneros que são válidos no Bingo para mostrar na mensagem
                valid_matches = [t for t in ALL_AVAILABLE_THEMES if normalize_genre(t) in all_norm_tags]
                
                # Tradução amigável para a mensagem de erro (Opcional, mas legal)
                error_msg = f"Jogada inválida! No bingo, '{game_name}' se encaixa em: {', '.join(valid_matches)}."
                if not valid_matches:
                    error_msg = f"'{game_name}' não possui os gêneros necessários cadastrados na Steam."
                    
                return JsonResponse({'success': False, 'message': error_msg})

        except Exception as e:
            print(f"[ERRO VALIDAÇÃO] {e}", file=sys.stderr)
            return JsonResponse({'success': False, 'message': 'Erro de conexão com a Steam.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)


# --- What's My Score (Intocado) ---
def get_game_details_and_metascore(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=br&l=pt"
    time.sleep(2.0) 
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not data.get(str(appid)) or not data[str(appid)]['success']: return None
        game_data = data[str(appid)]['data']
        meta = game_data.get('metacritic')
        if meta and meta.get('score', 0) >= 70:
            return {'name': game_data.get('name'), 'appid': appid, 'metascore': meta['score'], 'image_url': game_data.get('header_image')}
        return None 
    except Exception: return None

def get_one_unique_high_rated_game(exclude_appids, score_to_exclude=0):
    attempts, MAX_ATTEMPTS = 0, 500
    attempted_appids = set(exclude_appids)
    if not WMS_APP_POOL: return None
    available = [app for app in WMS_APP_POOL if app.get('appid') not in attempted_appids]
    if not available: return None
    
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        appid = random.choice(available).get('appid')
        if not appid or appid in attempted_appids: continue
        attempted_appids.add(appid)
        game = get_game_details_and_metascore(appid)
        if game:
            if score_to_exclude == 0 or game['metascore'] != score_to_exclude: return game
    return None 

def get_two_unique_high_rated_games():
    g1 = get_one_unique_high_rated_game([], 0)
    if not g1: return None, None
    g2 = None
    attempts = 0
    while not g2 and attempts < 15:
        g2 = get_one_unique_high_rated_game([g1['appid']], g1['metascore'])
        attempts += 1
    return g1, g2

def whats_my_score_view(request): return render(request, 'jogos_steam/whats_my_score.html')

def get_metacritic_games_api(request):
    if request.method != 'GET': return JsonResponse({'success': False}, status=405)
    if not WMS_APP_POOL: return JsonResponse({'success': False}, status=503)
    exclude_str = request.GET.get('exclude_appids', '')
    if exclude_str:
        try:
            exclude = [int(x) for x in exclude_str.split(',') if x.strip()]
            score = int(request.GET.get('current_score', '0'))
        except ValueError: return JsonResponse({'success': False}, status=400)
        new_game = get_one_unique_high_rated_game(exclude, score)
        if new_game:
            return JsonResponse({'success': True, 'mode': 'rotation', 'game_data': {'name': new_game['name'], 'image_url': new_game['image_url'], 'appid': new_game['appid'], 'correct_metascore': new_game['metascore']}})
        else: return JsonResponse({'success': False, 'message': 'Fim dos jogos!'})
    else:
        g1, g2 = get_two_unique_high_rated_games()
        if g1 and g2:
            pair = random.sample([g1, g2], 2)
            return JsonResponse({'success': True, 'mode': 'initial', 'game1': {'name': pair[0]['name'], 'image_url': pair[0]['image_url'], 'metascore': pair[0]['metascore'], 'appid': pair[0]['appid']}, 'game2': {'name': pair[1]['name'], 'image_url': pair[1]['image_url'], 'appid': pair[1]['appid'], 'correct_metascore': pair[1]['metascore']}})
        return JsonResponse({'success': False, 'message': 'Erro ao carregar.'})

load_steam_app_list()
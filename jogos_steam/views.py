import random
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

def normalize_genre(genre_string):
    return genre_string.lower().replace('-', '').replace(' ', '')

ALL_AVAILABLE_THEMES = [
    "Action", "Indie", "Adventure", "RPG", "Strategy", "Simulation",
    "Casual", "Sports", "Racing", "Violent", "Single-player", "Multi-player",
    "Free to Play", "Early Access", "Massively Multiplayer", "Co-op"
]

def steam_tac_toe_view(request):
    custom_themes_str = request.GET.get('temas')
    
    if custom_themes_str:
        custom_themes_list = [theme.strip() for theme in custom_themes_str.split(',')]
        # Filtra para garantir que apenas temas válidos da lista principal sejam usados
        valid_themes = [theme for theme in custom_themes_list if theme in ALL_AVAILABLE_THEMES]
        # Se, após a filtragem, houver menos de 6 temas válidos, usa a lista completa como fallback
        themes_to_use = valid_themes if len(valid_themes) >= 6 else ALL_AVAILABLE_THEMES
    else:
        themes_to_use = ALL_AVAILABLE_THEMES
    
    # Garante que há temas suficientes para sortear
    num_to_sample = min(6, len(themes_to_use))
    generos_escolhidos = random.sample(themes_to_use, num_to_sample)
    
    # Preenche com temas padrão se não houver 6 após o sorteio (caso de emergência)
    while len(generos_escolhidos) < 6:
        fallback_theme = random.choice(ALL_AVAILABLE_THEMES)
        if fallback_theme not in generos_escolhidos:
            generos_escolhidos.append(fallback_theme)

    context = {
        'linhas': generos_escolhidos[:3],
        'colunas': generos_escolhidos[3:],
        'todos_os_temas': ALL_AVAILABLE_THEMES,
        'temas_atuais': themes_to_use, # Envia a lista de temas atualmente em uso para o template
    }
    return render(request, 'jogos_steam/steam_tac_toe.html', context)


def get_steam_app_list():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('applist', {}).get('apps', [])
    except requests.exceptions.RequestException:
        return []

STEAM_APPS = get_steam_app_list()

def search_steam_games_api(request):
    query = request.GET.get('q', '').lower()
    if not query or len(query) < 3: return JsonResponse({'games': []})
    results = [app for app in STEAM_APPS if query in app.get('name', '').lower()]
    return JsonResponse({'games': results[:10]})


def validate_game_move_api(request):
    if request.method == 'POST':
        appid = request.POST.get('appid', '').strip()
        row_genre = request.POST.get('row_genre', '').strip()
        col_genre = request.POST.get('col_genre', '').strip()

        if not all([appid, row_genre, col_genre]):
            return JsonResponse({'success': False, 'message': 'Dados incompletos.'}, status=400)
        
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        
        try:
            response = requests.get(url); response.raise_for_status(); data = response.json()
            if not data[appid]['success']: 
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
                    message = f"{game_name} não se encaixa em '{row_genre}' e '{col_genre}'. Ele não possui nenhum dos gêneros do nosso bingo."
                else:
                    genres_str = ', '.join(valid_genres_for_bingo)
                    message = f"Jogada inválida! '{game_name}' não é '{row_genre}' e '{col_genre}'. No bingo, ele se encaixa em: {genres_str}."
                
                return JsonResponse({'success': False, 'message': message})

        except (requests.exceptions.RequestException, KeyError):
            return JsonResponse({'success': False, 'message': 'Erro ao consultar a API da Steam.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
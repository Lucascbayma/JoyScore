# CÓDIGO COMPLETO e FINALMENTE CORRIGIDO para: jogos_steam/views.py

import random
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

# ... (as outras views não mudam, mas estão aqui para garantir) ...
def steam_tac_toe_view(request):
    LISTA_DE_GENEROS = [
        "Action", "Indie", "Adventure", "RPG", "Strategy", "Simulation",
        "Casual", "Sports", "Racing", "Violent", "Singleplayer", "Multiplayer",
        "Free to Play", "Early Access", "Massively Multiplayer", "Co-op"
    ]
    generos_escolhidos = random.sample(LISTA_DE_GENEROS, 6)
    context = {
        'linhas': generos_escolhidos[:3],
        'colunas': generos_escolhidos[3:],
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
    if not query or len(query) < 3:
        return JsonResponse({'games': []})
    
    results = [app for app in STEAM_APPS if query in app.get('name', '').lower()]
    limited_results = results[:10]
    return JsonResponse({'games': limited_results})


def validate_game_move_api(request):
    if request.method == 'POST':
        appid = request.POST.get('appid', '').strip()
        row_genre = request.POST.get('row_genre', '').strip()
        col_genre = request.POST.get('col_genre', '').strip()

        if not all([appid, row_genre, col_genre]):
            return JsonResponse({'success': False, 'message': 'Dados incompletos.'}, status=400)

        # --- A CORREÇÃO FINAL ESTÁ AQUI ---
        # Removemos o parâmetro '&l=brazilian' para forçar a API a responder em INGLÊS.
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        # --- FIM DA CORREÇÃO ---
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if not data[appid]['success']:
                return JsonResponse({'success': False, 'message': 'Jogo não encontrado na Steam.'})

            game_data = data[appid]['data']
            
            game_genres = [genre['description'] for genre in game_data.get('genres', [])]
            game_categories = [cat['description'] for cat in game_data.get('categories', [])]
            all_tags = game_genres + game_categories

            if row_genre in all_tags and col_genre in all_tags:
                return JsonResponse({
                    'success': True,
                    'image_url': game_data.get('header_image')
                })
            else:
                tags_formatadas = ", ".join(all_tags)
                mensagem_erro = (
                    f'Errado! O jogo "{game_data.get("name")}" não se encaixa em "{row_genre}" e "{col_genre}".\n\n'
                    f'Os gêneros/categorias dele são: {tags_formatadas}'
                )
                return JsonResponse({'success': False, 'message': mensagem_erro})

        except (requests.exceptions.RequestException, KeyError):
            return JsonResponse({'success': False, 'message': 'Erro ao comunicar com a API da Steam.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)
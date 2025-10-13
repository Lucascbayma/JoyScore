# CÓDIGO COMPLETO para: jogos_steam/urls.py

from django.urls import path
from . import views

app_name = 'jogos_steam'

urlpatterns = [
    # URL da página do jogo
    path('steam-tac-toe/', views.steam_tac_toe_view, name='steam_tac_toe'),

    # URL da nossa API de busca
    path('api/search-games/', views.search_steam_games_api, name='api_search_games'),
    
    # --- INÍCIO DO NOVO CÓDIGO ---
    # URL da nossa API de validação
    path('api/validate-move/', views.validate_game_move_api, name='api_validate_move'),
    # --- FIM DO NOVO CÓDIGO ---
]
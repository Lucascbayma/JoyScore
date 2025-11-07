from django.urls import path
from . import views

app_name = 'jogos_steam'

urlpatterns = [
    # URL da página do jogo Steam Tac Toe (MANTIDA)
    path('steam-tac-toe/', views.steam_tac_toe_view, name='steam_tac_toe'),

    # URLs da API do Steam Tac Toe (MANTIDAS)
    path('api/search-games/', views.search_steam_games_api, name='api_search_games'),
    path('api/validate-move/', views.validate_game_move_api, name='api_validate_move'),

    # 🎮 NOVO JOGO: WHAT'S MY SCORE
    path('whats-my-score/', views.whats_my_score_view, name='whats_my_score'),
    path('api/get-metacritic-games/', views.get_metacritic_games_api, name='api_metacritic_games'),
]
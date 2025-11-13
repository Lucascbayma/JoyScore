# jogos/urls.py

from django.urls import path
from . import views

app_name = 'jogos' 

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'), 
    path('biblioteca/', views.minha_biblioteca, name='biblioteca'),
    path('filtrar/', views.filtrar_por_genero, name='filtrar_por_genero'),
    path('configuracoes/', views.configuracoes_conta, name='configuracoes_conta'),
    path('buscar/', views.buscar_jogos, name='buscar_jogos'),
    path('minha-biblioteca/', views.minha_biblioteca, name='minha_biblioteca'),
    path('adicionar/<int:jogo_id>/', views.adicionar_biblioteca, name='adicionar_biblioteca'),
    path('avaliar/<int:jogo_id>/', views.avaliar, name='avaliar'),
    path('api/search/', views.autocomplete_search, name='api_autocomplete'),

    path('avaliar/api/<int:rawg_id>/', views.redirecionar_para_avaliacao, name='avaliar_from_rawg'),
    # --- FIM DA ALTERAÇÃO ---
]
from django.urls import path
from . import views

app_name = 'jogos' 

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),  
    path('registro/', views.registro, name='registro'),
    # PATH para história 1
    path('buscar/', views.buscar_jogos, name='buscar_jogos'),

    # PATH para mostrar Jogos do usuário
    path('minha-biblioteca/', views.minha_biblioteca, name='minha_biblioteca'),
    
    # PATH para História 2
    path('adicionar/<int:jogo_id>/', views.adicionar_biblioteca, name='adicionar_biblioteca'),

    # História 3: Avaliar um Jogo
    path('avaliar/<int:jogo_id>/', views.avaliar, name='avaliar'),

    # Função de Busca inteligente
    path('api/search/', views.autocomplete_search, name='api_autocomplete'),
]
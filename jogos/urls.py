from django.urls import path
from .views import (
    buscar_jogos,
    minha_biblioteca,
    adicionar_biblioteca,
    avaliar
)

app_name = 'jogos' 

urlpatterns = [
    # PATH para história 1
    path('buscar/', buscar_jogos, name='buscar_jogos'),

    # PATH para mostrar Jogos do usuário
    path('minha-biblioteca/', minha_biblioteca, name='minha_biblioteca'),
    
    # PATH para História 2
    path('adicionar/<int:jogo_id>/', adicionar_biblioteca, name='adicionar_biblioteca'),

    # História 3: Avaliar um Jogo
    path('avaliar/<int:jogo_id>/', avaliar, name='avaliar'),
]
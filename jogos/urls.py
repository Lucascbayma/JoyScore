from django.urls import path
from . import views

app_name = 'jogos' 

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.home, name='temp_home'), # Alterado de views.login, mudança temporaria
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'), # URL para sair
    path('biblioteca/', views.minha_biblioteca, name='biblioteca'),

    path('buscar/', views.buscar_jogos, name='buscar_jogos'),
    path('minha-biblioteca/', views.minha_biblioteca, name='minha_biblioteca'),
    path('adicionar/<int:jogo_id>/', views.adicionar_biblioteca, name='adicionar_biblioteca'),
    path('avaliar/<int:jogo_id>/', views.avaliar, name='avaliar'),
    path('api/search/', views.autocomplete_search, name='api_autocomplete'),
]
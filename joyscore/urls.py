from django.contrib import admin
from django.urls import path, include
from jogos.views import github_webhook

urlpatterns = [
    # Rota para o painel de administração do Django
    path('admin/', admin.site.urls),

    # Rota para o seu novo app da Steam 
    path('steam/', include('jogos_steam.urls')),

    # CORREÇÃO: Adicionando o namespace 'jogos' para resolver o NoReverseMatch
    path('', include(('jogos.urls', 'jogos'), namespace='jogos')), 

    # Adicionando o webhook na raiz
    path('webhook/github/', github_webhook, name='github_webhook'),
]
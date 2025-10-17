from django.contrib import admin
from django.urls import path, include
from jogos.views import github_webhook

urlpatterns = [
    # Rota para o painel de administração do Django
    path('admin/', admin.site.urls),

    # Rota para o seu novo app da Steam
    # Qualquer URL que comece com /steam/ será gerenciada por ele
    path('steam/', include('jogos_steam.urls')),

    # Rota para o seu app original (RAWG)
    # O path '' diz ao Django que este app cuida da PÁGINA INICIAL e outras rotas
    path('', include('jogos.urls')),

    # Adicionando o webhook na raiz
    path('webhook/github/', github_webhook, name='github_webhook'),
]
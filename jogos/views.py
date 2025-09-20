from django.shortcuts import render
from .models import Jogo
from django.db.models import Q

# Create your views here.

def buscar_jogos(request):
    pesquisa = request.GET.get('q')
    jogos = Jogo.objects.all()

    if pesquisa:
        jogos = jogos.filter(Q(titulo__icontains=pesquisa) | Q(desenvolvedor__icontains=pesquisa) | Q(genero__icontains=pesquisa)).distinct() # Esse distinct é pra que não tenha resultados duplicados
    context = {'jogos': jogos, 'pesquisa': pesquisa,}

    return render(request, 'buscar_jogos.hmtl', context)

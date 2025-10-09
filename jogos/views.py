from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Jogo, Add_Biblioteca, Avaliar
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
from django.views.decorators.http import require_GET

# Imports para autenticação
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages

RAWG_API_KEY = settings.API_KEY
RAWG_BASE_URL = "https://api.rawg.io/api"


def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('jogos:registro')
        if User.objects.filter(username=username).exists():
            messages.error(request, f'O apelido "{username}" já está em uso!')
            return redirect('jogos:registro')
        if User.objects.filter(email=email).exists():
            messages.error(request, f'O e-mail "{email}" já foi cadastrado!')
            return redirect('jogos:registro')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        auth_login(request, user)
        messages.success(request, f'Conta criada com sucesso! Bem-vindo, {username}.')
        return redirect('jogos:home')

    return render(request, 'jogos/registro.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('jogos:home')
        else:
            messages.error(request, 'Apelido ou senha inválidos.')
            return redirect('jogos:login')
            
    return render(request, 'jogos/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('jogos:login')


@login_required
def avaliar(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)
    
    esta_na_biblioteca = Add_Biblioteca.objects.filter(
        usuario=request.user, 
        jogo=jogo
    ).exists()

    avaliacao_existente = Avaliar.objects.filter(usuario=request.user, Jogo=jogo).first()

    if request.method == 'POST':
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario')

        if not nota:
            messages.error(request, 'Você precisa selecionar pelo menos uma estrela para avaliar.')
            return redirect('jogos:avaliar', jogo_id=jogo.id)

        Avaliar.objects.update_or_create(
            usuario=request.user,
            Jogo=jogo,
            defaults={'nota': nota, 'comentario': comentario}
        )
        
        messages.success(request, 'Sua avaliação foi salva com sucesso!')
        return redirect('jogos:avaliar', jogo_id=jogo.id)

    context = {
        'jogo': jogo, 
        'avaliacao_existente': avaliacao_existente,
        'esta_na_biblioteca': esta_na_biblioteca 
    }
    return render(request, 'jogos/avaliar_jogo.html', context)

@login_required
def buscar_jogos(request):
    pesquisa = request.GET.get('q')
    jogos = Jogo.objects.all()
    if pesquisa:
        jogos = jogos.filter(
            Q(titulo__icontains=pesquisa) |
            Q(desenvolvedor__icontains=pesquisa) |
            Q(genero__icontains=pesquisa)
        ).distinct()

    context = {'jogos': jogos, 'pesquisa': pesquisa}
    return render(request, 'jogos/buscar_jogos.html', context)


@login_required
def adicionar_biblioteca(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)
    
    registro_biblioteca = Add_Biblioteca.objects.filter(
        usuario=request.user, 
        jogo=jogo
    ).first()

    if registro_biblioteca:
        registro_biblioteca.delete()
        messages.success(request, f'O jogo "{jogo.titulo}" foi removido da sua biblioteca.')
    else:
        Add_Biblioteca.objects.create(usuario=request.user, jogo=jogo)
        messages.success(request, f'O jogo "{jogo.titulo}" foi adicionado à sua biblioteca.')

    return redirect('jogos:avaliar', jogo_id=jogo.id)


@login_required
def minha_biblioteca(request):
    itens_biblioteca = Add_Biblioteca.objects.filter(
        usuario=request.user
    ).order_by('-data_adicionado')
    
    jogos_na_biblioteca = [item.jogo for item in itens_biblioteca]

    context = {
        'jogos': jogos_na_biblioteca, 
    }
    
    return render(request, 'jogos/biblioteca.html', context)


def home(request):
    titulos_selecionados = [
        "The Witcher 3: Wild Hunt",
        "Red Dead Redemption 2",
        "Grand Theft Auto V",
        "Hollow Knight",
        "Portal 2",
        "Minecraft",
        "God of War",
        "Elden Ring",
        "Fortnite Battle Royale",
        "The Legend of Zelda: Breath of the Wild",
    ]

    jogos_populares = Jogo.objects.filter(
        titulo__in=titulos_selecionados
    ).order_by('titulo')
    
    context = {
        'jogos_populares': jogos_populares, 
    }
    return render(request, 'jogos/home.html', context)

@require_GET
def autocomplete_search(request):
    query = request.GET.get('q')
    
    if not query:
        return JsonResponse({'results': []})

    jogos_encontrados = Jogo.objects.filter(
        titulo__icontains=query
    ).order_by('titulo')[:4]
    results_list = []
    for jogo in jogos_encontrados:
        results_list.append({
            "id": jogo.id,
            "name": jogo.titulo,
            "released": jogo.ano_lancamento.isoformat() if jogo.ano_lancamento else None,
            "background_image": jogo.background_image, 
        })
        
    return JsonResponse({'results': results_list})
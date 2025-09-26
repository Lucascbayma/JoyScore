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

# --- NOVAS FUNÇÕES DE AUTENTICAÇÃO ---

def registro(request):
    if request.method == 'POST':
        # Pegando os dados do formulário pelo atributo 'name'
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validações
        if password != password2:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('jogos:registro')
        if User.objects.filter(username=username).exists():
            messages.error(request, f'O apelido "{username}" já está em uso!')
            return redirect('jogos:registro')
        if User.objects.filter(email=email).exists():
            messages.error(request, f'O e-mail "{email}" já foi cadastrado!')
            return redirect('jogos:registro')
        
        # Criando o usuário
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        # Logando o usuário recém-criado
        auth_login(request, user)
        messages.success(request, f'Conta criada com sucesso! Bem-vindo, {username}.')
        return redirect('jogos:home')

    return render(request, 'registro.html')


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
            
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('jogos:login')


# --- FUNÇÃO AVALIAR REFEITA SEM FORMS ---

@login_required
def avaliar(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)
    
    # Busca se o usuário já fez uma avaliação para este jogo
    avaliacao_existente = Avaliar.objects.filter(usuario=request.user, Jogo=jogo).first()

    if request.method == 'POST':
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario')

        if not nota:
            messages.error(request, 'Você precisa selecionar pelo menos uma estrela para avaliar.')
            return redirect('jogos:avaliar', jogo_id=jogo.id)

        # Usando update_or_create para criar uma nova avaliação ou atualizar uma existente
        Avaliar.objects.update_or_create(
            usuario=request.user,
            Jogo=jogo,
            defaults={'nota': nota, 'comentario': comentario}
        )
        
        messages.success(request, 'Sua avaliação foi salva com sucesso!')
        # Idealmente, você redirecionaria para a página de detalhes do jogo
        return redirect('jogos:home') # Altere para a página de detalhes do jogo se tiver uma

    context = {'jogo': jogo, 'avaliacao_existente': avaliacao_existente}
    return render(request, 'avaliar_jogo.html', context)


# --- SUAS OUTRAS VIEWS (mantidas como estavam) ---

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
    return render(request, 'buscar_jogos.html', context)


@login_required
def adicionar_biblioteca(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)
    Add_Biblioteca.objects.get_or_create(usuario=request.user, jogo=jogo)
    return redirect('minha_biblioteca')


@login_required
def minha_biblioteca(request):
    itens_biblioteca = Add_Biblioteca.objects.filter(
        usuario=request.user
    ).order_by('-data_adicionado')

    context = {'itens_biblioteca': itens_biblioteca}
    return render(request, 'minha_biblioteca.html', context)


def home(request):
    titulos_selecionados = [
        "The Witcher 3: Wild Hunt",
        "Red Dead Redemption 2",
        "Grand Theft Auto V",
        "The Elder Scrolls V: Skyrim",
        "Portal 2",
        "Minecraft",
        "God of War",
        "Elden Ring",
        "Fortnite",
        "The Legend of Zelda: Breath of the Wild",
    ]

    jogos_populares = Jogo.objects.filter(
        titulo__in=titulos_selecionados
    ).order_by('titulo')
    
    context = {
        'jogos_populares': jogos_populares, 
    }
    return render(request, 'home.html', context)

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
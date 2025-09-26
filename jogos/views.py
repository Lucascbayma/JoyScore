from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Jogo, Add_Biblioteca, Avaliar
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
from django.views.decorators.http import require_GET

RAWG_API_KEY = settings.API_KEY
RAWG_BASE_URL = "https://api.rawg.io/api"


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


@login_required
def avaliar(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)

    # Criamos o form inline
    class AvaliacaoForm(forms.ModelForm):
        class Meta:
            model = Avaliar
            fields = ['nota', 'comentario']  # ajuste conforme os campos do seu model Avaliar

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.jogo = jogo
            avaliacao.usuario = request.user
            avaliacao.save()
            return redirect('página_do_jogo', jogo_id=jogo.id)
    else:
        form = AvaliacaoForm()

    context = {'jogo': jogo, 'form': form}
    return render(request, 'avaliar_jogo.html', context)


def home(request):
    url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&page_size=20"

    dados_jogos = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        dados_jogos = data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API RAWG: {e}")

    context = {'jogos_rawg': dados_jogos}
    return render(request, 'home.html', context)

@require_GET
def autocomplete_search(request):
    query = request.GET.get('q')
    
    if not query:
        return JsonResponse({'results': []})

    params = {
        'key': settings.API_KEY,
        'search': query,
        'search_precise': 'true', 
        'page_size': 3,
    }
    
    search_url = f'{RAWG_BASE_URL}/games'
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data)

    except requests.RequestException as e:
        print(f"Erro ao conectar com a API: {e}")
        return JsonResponse({'error': 'Erro de comunicação com a API.'}, status=500)
def login(request):
    return render(request, 'login.html')
    

# jogos/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Jogo, Add_Biblioteca, Avaliar, Profile
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
from django.views.decorators.http import require_GET
import math 
import random # Mantemos o import do random
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import os
import subprocess
import logging
import dateutil.parser # <-- IMPORT NECESSÁRIO PARA CONVERTER DATA DA API

RAWG_API_KEY = settings.API_KEY
RAWG_BASE_URL = "https://api.rawg.io/api"


def _get_all_genres(request):
    """Função auxiliar para buscar a lista de gêneros da API RAWG."""
    genres_url = f"{RAWG_BASE_URL}/genres?key={RAWG_API_KEY}"
    try:
        all_genres_response = requests.get(genres_url)
        all_genres_response.raise_for_status()
        return all_genres_response.json().get('results', [])
    except requests.RequestException:
        messages.error(request, "Não foi possível buscar a lista de gêneros da API.")
        return []


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
    esta_na_biblioteca = Add_Biblioteca.objects.filter(usuario=request.user, jogo=jogo).exists()
    avaliacao_existente = Avaliar.objects.filter(usuario=request.user, Jogo=jogo).first()
    if request.method == 'POST':
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario')
        if not nota:
            messages.error(request, 'Você precisa selecionar pelo menos uma estrela para avaliar.')
            return redirect('jogos:avaliar', jogo_id=jogo.id)
        Avaliar.objects.update_or_create(usuario=request.user, Jogo=jogo, defaults={'nota': nota, 'comentario': comentario})
        messages.success(request, 'Sua avaliação foi salva com sucesso!')
        return redirect('jogos:avaliar', jogo_id=jogo.id)
    context = {'jogo': jogo, 'avaliacao_existente': avaliacao_existente, 'esta_na_biblioteca': esta_na_biblioteca }
    return render(request, 'jogos/avaliar_jogo.html', context)

# --- INÍCIO DA ALTERAÇÃO (NOVA VIEW "PONTE") ---

@login_required
def redirecionar_para_avaliacao(request, rawg_id):
    """
    Esta view age como uma "ponte". 
    1. Recebe um ID da API RAWG.
    2. Verifica se o jogo já existe no banco de dados local (usando 'rawg_id').
    3. Se não existe, busca na API RAWG e cria o jogo localmente.
    4. Redireciona o usuário para a página 'avaliar' padrão com o ID local do jogo.
    """
    try:
        # 1. Tenta encontrar o jogo no banco local pelo rawg_id
        jogo = Jogo.objects.get(rawg_id=rawg_id)
    
    except Jogo.DoesNotExist:
        # 2. Se não encontrar, busca na API RAWG para criar
        game_details_url = f"{RAWG_BASE_URL}/games/{rawg_id}?key={RAWG_API_KEY}"
        try:
            response = requests.get(game_details_url)
            response.raise_for_status()
            data = response.json()

            # Pega os dados da API
            titulo = data.get('name')
            devs = data.get('developers', [])
            desenvolvedor = ", ".join([d.get('name') for d in devs]) if devs else ""
            
            release_date_str = data.get('released')
            release_date_obj = None
            if release_date_str:
                try:
                    # Converte a string 'YYYY-MM-DD' para um objeto date
                    release_date_obj = dateutil.parser.parse(release_date_str).date()
                except ValueError:
                    release_date_obj = None # Ignora se a data for inválida

            genres = data.get('genres', [])
            genero = genres[0].get('name', "") if genres else ""
            
            # 3. Cria o jogo no banco local
            # Usamos get_or_create pelo título para evitar duplicatas
            jogo, created = Jogo.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'rawg_id': rawg_id,
                    'desenvolvedor': desenvolvedor,
                    'ano_lancamento': release_date_obj,
                    'genero': genero,
                    'background_image': data.get('background_image'),
                    'descricao': data.get('description_raw', '')
                }
            )
            
            # Se o jogo foi 'pego' (created=False) mas não tinha o rawg_id, atualiza.
            if not created and not jogo.rawg_id:
                jogo.rawg_id = rawg_id
                jogo.save()
        
        except requests.RequestException:
            messages.error(request, "Não foi possível buscar os detalhes do jogo na API. Tente novamente.")
            return redirect('jogos:filtrar_por_genero')
        except Exception as e:
            # Captura erro se o título já existir (unique=True)
            messages.error(request, f"Ocorreu um erro ao salvar o jogo: {e}.")
            return redirect('jogos:filtrar_por_genero')

    # 4. Redireciona para a página de avaliação normal com o ID LOCAL
    return redirect('jogos:avaliar', jogo_id=jogo.id)

# --- FIM DA ALTERAÇÃO ---


@login_required
def buscar_jogos(request):
    pesquisa = request.GET.get('q')
    jogos = Jogo.objects.all()
    if pesquisa:
        jogos = jogos.filter(Q(titulo__icontains=pesquisa) | Q(desenvolvedor__icontains=pesquisa) | Q(genero__icontains=pesquisa)).distinct()
    context = {'jogos': jogos, 'pesquisa': pesquisa}
    return render(request, 'jogos/buscar_jogos.html', context)

@login_required
def adicionar_biblioteca(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)
    registro_biblioteca = Add_Biblioteca.objects.filter(usuario=request.user, jogo=jogo).first()
    if registro_biblioteca:
        registro_biblioteca.delete()
        messages.success(request, f'O jogo "{jogo.titulo}" foi removido da sua biblioteca.')
    else:
        Add_Biblioteca.objects.create(usuario=request.user, jogo=jogo)
        messages.success(request, f'O jogo "{jogo.titulo}" foi adicionado à sua biblioteca.')
    return redirect('jogos:avaliar', jogo_id=jogo.id)

@login_required
def minha_biblioteca(request):
    itens_biblioteca = Add_Biblioteca.objects.filter(usuario=request.user).order_by('-data_adicionado')
    jogos_na_biblioteca = [item.jogo for item in itens_biblioteca]
    context = {'jogos': jogos_na_biblioteca, }
    return render(request, 'jogos/biblioteca.html', context)

def home(request):
    RECOMENDACOES_POR_GENERO = { 'Action': ["Grand Theft Auto V", "Red Dead Redemption 2", "Marvel's Spider-Man", "God of War", "Doom Eternal", "Sekiro: Shadows Die Twice"], 'Indie': ["Hollow Knight", "Stardew Valley", "Celeste", "Cuphead", "Hades", "Disco Elysium"], 'Adventure': ["The Witcher 3: Wild Hunt", "The Legend of Zelda: Breath of the Wild", "Uncharted 4: A Thief's End", "Tomb Raider (2013)", "Life is Strange", "Alan Wake 2"], 'RPG': ["Elden Ring", "Persona 5 Royal", "Final Fantasy VII Remake", "Mass Effect Legendary Edition", "Fallout: New Vegas", "Cyberpunk 2077"], 'Strategy': ["Sid Meier's Civilization V", "XCOM 2", "StarCraft II: Wings of Liberty", "Into the Breach", "Age of Empires II: Definitive Edition", "Total War: WARHAMMER II"], 'Shooter': ["Counter-Strike: Global Offensive", "Apex Legends", "Overwatch 2", "Call of Duty: Modern Warfare", "Battlefield 4", "Destiny 2"], 'Puzzle': ["Portal 2", "The Witness", "Baba Is You", "Inside", "Return of the Obra Dinn", "Tetris Effect: Connected"], 'Simulation': ["Minecraft", "The Sims 4", "Cities: Skylines", "Microsoft Flight Simulator", "Kerbal Space Program", "Euro Truck Simulator 2"], 'Sports': ["FIFA 23", "NBA 2K23", "Rocket League", "Forza Horizon 5", "Madden NFL 23", "EA Sports FC 24"], 'Racing': ["Forza Horizon 5", "Gran Turismo 7", "Mario Kart 8 Deluxe", "Need for Speed: Heat", "DiRT Rally 2.0", "Assetto Corsa"], 'Fighting': ["Mortal Kombat 11", "Street Fighter 6", "Tekken 7", "Super Smash Bros. Ultimate", "Guilty Gear -Strive-", "Dragon Ball FighterZ"], 'Platformer': ["Celeste", "Hollow Knight", "Super Mario Odyssey", "Ori and the Will of the Wisps", "Shovel Knight: Treasure Trove", "Cuphead"], }
    
    jogos_recomendados = []
    
    if request.user.is_authenticated:
        try:
            random.seed(request.user.id)

            profile = request.user.profile
            generos_favoritos = profile.generos_favoritos
            
            if generos_favoritos:
                jogos_na_biblioteca_ids = Add_Biblioteca.objects.filter(usuario=request.user).values_list('jogo_id', flat=True)
                ids_ja_recomendados = set()
                
                random.shuffle(generos_favoritos)

                for genero in generos_favoritos:
                    if len(jogos_recomendados) >= 10: break
                    
                    candidatos = RECOMENDACOES_POR_GENERO.get(genero, [])
                    random.shuffle(candidatos)
                    adicionados_neste_genero = 0

                    for titulo_jogo in candidatos:
                        jogo = Jogo.objects.filter(titulo=titulo_jogo).exclude(id__in=jogos_na_biblioteca_ids).exclude(id__in=ids_ja_recomendados).first()
                        
                        if jogo and adicionados_neste_genero < 2:
                            jogos_recomendados.append(jogo)
                            ids_ja_recomendados.add(jogo.id)
                            adicionados_neste_genero += 1
                            if len(jogos_recomendados) >= 10: break
                
                if len(jogos_recomendados) < 10:
                    fallback_queryset = Jogo.objects.exclude(id__in=jogos_na_biblioteca_ids).exclude(id__in=ids_ja_recomendados)
                    fallback_list = list(fallback_queryset)
                    random.shuffle(fallback_list)

                    restantes = 10 - len(jogos_recomendados)
                    jogos_recomendados.extend(fallback_list[:restantes])

        except Profile.DoesNotExist:
            pass

    titulos_populares = [ "The Witcher 3: Wild Hunt", "Red Dead Redemption 2", "Grand Theft Auto V", "Hollow Knight", "Portal 2", "Minecraft", "God of War", "Elden Ring", "Fortnite Battle Royale", "The Legend of Zelda: Breath of the Wild", ]
    jogos_populares = Jogo.objects.filter( titulo__in=titulos_populares ).order_by('titulo')
    titulos_favs = [ "Pokémon X, Y", "Marvel's Spider-Man", "The Witcher 3: Wild Hunt", "Bloodborne", "FIFA 22", "Hollow Knight", ]
    jogos_favs = Jogo.objects.filter( titulo__in=titulos_favs ).order_by('titulo')
    titulos_acao = [ "Sekiro: Shadows Die Twice", "Devil May Cry 5", "Doom Eternal", "Marvel Rivals", "Marvel's Spider-Man", "Assassin's Creed Valhalla", "Alan Wake 2", "Batman: Arkham Knight", "God of War: Ragnarök", ]
    jogos_acao = Jogo.objects.filter( titulo__in=titulos_acao ).order_by('titulo')
    titulos_indie = [ "Hades", "Cuphead", "Celeste", "Stardew Valley", "Hollow Knight", "Ori and the Will of the Wisps", "Disco Elysium", ]
    jogos_indie = Jogo.objects.filter( titulo__in=titulos_indie ).order_by('titulo')
    titulos_rpg = [ "Final Fantasy VII Remake", "Persona 5 Royal", "Dragon Age: Inquisition", "Mass Effect Legendary Edition", "Fallout: New Vegas", "FINAL FANTASY XV", "World of Warcraft", ]
    jogos_rpg = Jogo.objects.filter( titulo__in=titulos_rpg ).order_by('titulo')
    titulos_shooter = [ "Call of Duty: Modern Warfare", "Apex Legends", "Overwatch 2", "Destiny 2", "Counter-Strike: Global Offensive", "Battlefield 4", "Halo 3", "S.T.A.L.K.E.R.: Clear Sky", ]
    jogos_shooter = Jogo.objects.filter( titulo__in=titulos_shooter ).order_by('titulo')
    titulos_playstation = [ "Astro Bot", "The Last of Us", "The Last of Us Part II", "Uncharted 4: A Thief's End", "God of War", "God of War: Ragnarök", "Ghost of Tsushima", "Marvel's Spider-Man", "Horizon Zero Dawn", "Bloodborne" ]
    jogos_playstation = Jogo.objects.filter(titulo__in=titulos_playstation).order_by('titulo')
    titulos_nintendo = [ "Super Smash Bros. Ultimate", "Super Mario Odyssey", "Animal Crossing: New Horizons", "Little Nightmares", "The Binding of Isaac", "The Legend of Zelda: Breath of the Wild", "Pokémon: Let's Go, Pikachu! and Eevee!", "Mario Kart 8", ]
    jogos_nintendo = Jogo.objects.filter(titulo__in=titulos_nintendo).order_by('titulo')
    
    context = { 
        'jogos_recomendados': jogos_recomendados,
        'jogos_favs': jogos_favs,
        'jogos_populares': jogos_populares, 
        'jogos_acao': jogos_acao, 
        'jogos_indie': jogos_indie, 
        'jogos_rpg': jogos_rpg, 
        'jogos_shooter': jogos_shooter,
        'jogos_playstation': jogos_playstation,
        'jogos_nintendo': jogos_nintendo,
    }
    return render(request, 'jogos/home.html', context)

@require_GET
def autocomplete_search(request):
    query = request.GET.get('q')
    if not query:
        return JsonResponse({'results': []})
    jogos_encontrados = Jogo.objects.filter(titulo__icontains=query).order_by('titulo')[:4]
    results_list = []
    for jogo in jogos_encontrados:
        results_list.append({ "id": jogo.id, "name": jogo.titulo, "released": jogo.ano_lancamento.isoformat() if jogo.ano_lancamento else None, "background_image": jogo.background_image, })
    return JsonResponse({'results': results_list})

@login_required
def filtrar_por_genero(request):
    all_genres = _get_all_genres(request)
    selected_genres_ids_str = request.GET.getlist('genres')
    selected_genres_ids = [int(gid) for gid in selected_genres_ids_str if gid.isdigit()]
    page_number = request.GET.get('page', 1)
    games_page = {'results': [], 'has_previous': False, 'previous_page_number': 1, 'number': 1, 'has_next': False, 'next_page_number': 1 }
    search_error = None
    form_submitted = 'genres' in request.GET
    if form_submitted:
        if not selected_genres_ids:
            search_error = "Por favor, selecione pelo menos 1 gênero para filtrar."
        elif len(selected_genres_ids) > 2:
            search_error = "Você só pode selecionar até 2 gêneros."
        else:
            genres_param = ",".join(selected_genres_ids_str)
            page_size = 15
            games_url = f"{RAWG_BASE_URL}/games?key={RAWG_API_KEY}&genres={genres_param}&ordering=name&page_size={page_size}&page={page_number}"
            try:
                response = requests.get(games_url)
                response.raise_for_status()
                data = response.json()
                total_games = data.get('count', 0)
                total_pages = math.ceil(total_games / page_size)
                current_page_num = int(page_number)
                games_page['results'] = data.get('results', [])
                games_page['number'] = current_page_num
                if current_page_num > 1:
                    games_page['has_previous'] = True
                    games_page['previous_page_number'] = current_page_num - 1
                if current_page_num < total_pages:
                    games_page['has_next'] = True
                    games_page['next_page_number'] = current_page_num + 1
            except requests.RequestException:
                search_error = "Ocorreu um erro ao buscar os jogos. Tente novamente."
    genres_query_string = "&".join([f"genres={gid}" for gid in selected_genres_ids_str])
    context = {'all_genres': all_genres, 'games_page': games_page, 'selected_genres_ids': selected_genres_ids, 'search_error': search_error, 'form_submitted': form_submitted, 'genres_query_string': genres_query_string, }
    return render(request, 'jogos/filtrar.html', context)

@login_required
def configuracoes_conta(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        generos_selecionados = request.POST.getlist('genres')
        profile.generos_favoritos = generos_selecionados
        profile.save()
        return redirect('jogos:configuracoes_conta')
    all_genres = _get_all_genres(request)
    context = {'all_genres': all_genres, 'profile': profile }
    return render(request, 'jogos/configuracoes.html', context)

logger = logging.getLogger(__name__)

REPO_PATH = '/home/LcsBayma/joyscore/'
VENV_NAME = 'venv_joyscore'

@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        try:
            from GitPython.repo import Repo 
            
            REPO_PATH = '/home/LcsBayma/joyscore/'

            repo = Repo(REPO_PATH)
            origin = repo.remotes.origin
            origin.pull()
            
            return HttpResponse('Deployment concluído!', status=200)

        except ImportError:
            return HttpResponse('Erro de importação de GitPython no servidor.', status=500)
        except Exception as e:
            pass

    return HttpResponse('Método não permitido.', status=405)
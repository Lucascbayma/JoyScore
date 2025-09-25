from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Jogo, Add_Biblioteca
from .models import Jogo, Avaliar
from .forms import AvaliacaoForm #precisamos criar esse formulário

@login_required #verifica se o usuario esta logado.
def buscar_jogos(request):
    pesquisa = request.GET.get('q')
    jogos = Jogo.objects.all()

    if pesquisa:
        jogos = jogos.filter(Q(titulo__icontains=pesquisa) | Q(desenvolvedor__icontains=pesquisa) | Q(genero__icontains=pesquisa)).distinct() # Esse distinct é pra que não tenha resultados duplicados
    
    context = {'jogos': jogos, 'pesquisa': pesquisa,}

    return render(request, 'buscar_jogos.html', context)

@login_required
def adicionar_biblioteca(request, jogo_id):
    #Busca o jogo ou retorna erro se não existir.
    jogo = get_object_or_404(Jogo, pk=jogo_id)
    
    # Cria biblioteca caso não exista.
    Add_Biblioteca.objects.get_or_create(usuario=request.user, jogo=jogo)
    
    return redirect('minha_biblioteca')


@login_required
def minha_biblioteca(request):
    # Busca os jogos da biblioteca.
    itens_biblioteca = Add_Biblioteca.objects.filter(
        usuario=request.user
    ).order_by('-data_adicionado')  #Ordena por data.
    
    context = {
        'itens_biblioteca': itens_biblioteca
    }
    return render(request, 'minha_biblioteca.html', context)


@login_required
def avaliar(request,jogo_id):
    jogo = get_object_or_404(jogo,pk = jogo_id)

    if request.method== 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao= form.save(commit=False)
            avaliacao.jogo = jogo
            avaliacao.usuario = request.user
            avaliacao.save()
            return redirect('página_do_jogo',jogo_id = jogo.id)
    else:
        form= AvaliacaoForm()

    context= {
        'jogo': jogo,
        'form': form,
    }
    return render(request,'avaliar_jogo.html',context)

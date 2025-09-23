import os
import django
import requests
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joyscore.settings')
django.setup()

from jogos.models import Jogo
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('API_KEY')

def buscar_e_salvar_jogos():
    # PARA buscar os jogos na API e salvar no banco de dados do próprio Django.
    url = "https://api.rawg.io/api/games"
    params = {
        'key': API_KEY,
        'page_size': 40 # Ajustar o número de jogos por pesquisa.
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Dá um erro se a pesquisa falhar!

        data = response.json()
        jogos_encontrados = data.get('results', [])
        print(f"Foram encontrados {len(jogos_encontrados)} jogos no banco de dados.")
        
        for jogo_api in jogos_encontrados:
            titulo = jogo_api.get('name')
            
            # A API retorna dicionários para gêneros e para desenvolvedores,
            # Então vamos extrair os nomes e juntá-los em uma única string.
            generos_raw = jogo_api.get('genres', [])
            genero = ', '.join([g['name'] for g in generos_raw])
            
            desenvolvedor = ''
            
            ano_lancamento_raw = jogo_api.get('released')
            ano_lancamento = None
            if ano_lancamento_raw:
                try:
                    # Para converter a data de string para o formato do Django.
                    ano_lancamento = ano_lancamento_raw
                except (ValueError, TypeError):
                    ano_lancamento = None

            if not titulo:
                continue # Pula se tiver jogos sem título

            try:
                # get_or_create serve para evitar duplicatas e salvar o jogo
                jogo, created = Jogo.objects.get_or_create(
                    titulo=titulo,
                    defaults={
                        'desenvolvedor': desenvolvedor,
                        'ano_lancamento': ano_lancamento,
                        'genero': genero,
                    }
                )
                if created:
                    print(f"Jogo '{jogo.titulo}' adicionado ao banco de dados.")
                else:
                    print(f"Jogo '{jogo.titulo}' já existe no banco de dados.")
            except IntegrityError:
                print(f"Erro de integridade ao adicionar '{titulo}'. Título duplicado ou inválido.")

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição da API: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == '__main__':
    buscar_e_salvar_jogos()
    
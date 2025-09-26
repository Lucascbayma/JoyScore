import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from jogos.models import Jogo
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa jogos populares da API RAWG para o banco de dados local usando paginação.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=100, # Valor padrão: 100 jogos
            help='Número total de jogos que você deseja tentar importar.'
        )

    def handle(self, *args, **kwargs):
        api_key = settings.API_KEY
        
        current_url = f"https://api.rawg.io/api/games?key={api_key}&page_size=40" 
        
        total_a_importar = 400
        jogos_importados = 0
        total_processado = 0
        
        self.stdout.write(self.style.NOTICE(f'Iniciando importação de até {total_a_importar} jogos da RAWG...'))

        while current_url and total_processado < total_a_importar:
            self.stdout.write(f'Buscando página: {current_url}')
            
            try:
                response = requests.get(current_url)
                response.raise_for_status()
                data = response.json()
                
                for game_data in data.get('results', []):
                    if total_processado >= total_a_importar:
                        break 
                    
                    data_lancamento_str = game_data.get('released')
                    ano_lancamento = None
                    if data_lancamento_str:
                        try:
                            ano_lancamento = datetime.strptime(data_lancamento_str, '%Y-%m-%d').date()
                        except ValueError:
                            pass 

                    genero = ', '.join([g['name'] for g in game_data.get('genres', [])])
                    
                    jogo_obj, created = Jogo.objects.update_or_create(
                        titulo=game_data['name'],
                        defaults={
                            'ano_lancamento': ano_lancamento,
                            'desenvolvedor': 'RAWG API', 
                            'genero': genero,
                            'background_image': game_data.get('background_image'),
                        }
                    )

                    if created:
                        jogos_importados += 1
                    
                    total_processado += 1

                current_url = data.get('next') 
                
            except requests.RequestException as e:
                self.stderr.write(self.style.ERROR(f'Erro ao conectar ou buscar dados da RAWG: {e}'))
                break
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Ocorreu um erro no processamento: {e}'))
                break 

        self.stdout.write(self.style.SUCCESS(f'Importação concluída. Total de jogos processados: {total_processado}. {jogos_importados} novos jogos adicionados/atualizados.'))
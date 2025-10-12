# jogos/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
# Imports para criar o Profile automaticamente
from django.db.models.signals import post_save
from django.dispatch import receiver

class Jogo(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    desenvolvedor = models.CharField(max_length=200, blank=True)
    ano_lancamento = models.DateField(blank=True,null=True)
    genero = models.CharField(max_length=50, blank=True)
    background_image = models.URLField(max_length=500, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.titulo
    
class Avaliar(models.Model):
    Jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name="avaliacoes")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nota = models.IntegerField(validators= [MinValueValidator(1),MaxValueValidator(5)]) 
    comentario = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        # Correção de um pequeno erro no f-string (era self.Buscar.titulo)
        return f"Avaliação do jogo {self.Jogo.titulo} por {self.usuario.username} - {self.nota} estrelas"
    

class Add_Biblioteca(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE)
    data_adicionado = models.DateTimeField(auto_now_add=True)

    class Meta: # Correção: 'class verificar' deve ser 'class Meta'
        unique_together = ('usuario', 'jogo')

    def __str__(self):
        return f"{self.jogo.titulo} foi adicionado na sua biblioteca!"

class Profile(models.Model):
    # Cria uma ligação um-para-um com o modelo de usuário padrão do Django.
    # Se um usuário for deletado, seu perfil também será.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Usamos um JSONField para guardar uma lista de nomes de gêneros. É flexível e perfeito para isso.
    # Exemplo de como os dados serão salvos: ['Action', 'RPG', 'Indie']
    generos_favoritos = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

# Esta função mágica (signal) cria um Profile automaticamente
# toda vez que um novo Usuário é criado no seu sistema.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Esta função salva o Profile toda vez que o User é salvo.
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # Lida com o caso de usuários existentes antes da criação do Profile
        Profile.objects.create(user=instance)
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.

class Jogo(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    desenvolvedor = models.CharField(max_length=200, blank=True)
    ano_lancamento = models.DateField(blank=True,null=True)
    genero = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.titulo
    
class Avaliar(models.Model):
    Jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name="avaliacoes")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Isso é pra vincular a avaliação ao usuário!
    nota = models.IntegerField(
        validators= [MinValueValidator(1),MaxValueValidator(5)] # 5 estrelas
    ) 
    comentario = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return f"Avaliação do jogo {self.Buscar.titulo} por {self.usuario.username} - {self.nota} estrelas"
    

class Add_Biblioteca(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE)
    data_adicionado = models.DateTimeField(auto_now_add=True)

    class verificar:
        unico = ('usuario', 'jogo') # Isso vai servir pra que o user não add o mesmo jogo 2 vzs na biblioteca 

    def __str__(self):
        return f"{self.jogo.titulo} foi adicionado na sua biblioteca!"

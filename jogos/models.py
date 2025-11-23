from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone

class Jogo(models.Model):
    rawg_id = models.IntegerField(
        unique=True, 
        null=True, 
        blank=True, 
        help_text="ID do jogo na API RAWG"
    )
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
    data_da_avaliacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Avaliação do jogo {self.Jogo.titulo} por {self.usuario.username} - {self.nota} estrelas"
    
    class Meta:
        ordering = ['-data_da_avaliacao']
        unique_together = ('usuario', 'Jogo') 
    

class Add_Biblioteca(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE)
    data_adicionado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'jogo')

    def __str__(self):
        return f"{self.jogo.titulo} foi adicionado na sua biblioteca!"

class JornadaGamer(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jornadas")
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name="jornadas")
    
    horas_jogadas = models.PositiveIntegerField(default=0, verbose_name="Horas Jogadas")
    trofeus_totais = models.PositiveIntegerField(default=0, verbose_name="Total de Troféus")
    trofeus_conquistados = models.PositiveIntegerField(default=0, verbose_name="Troféus Conquistados")

    class Meta:
        unique_together = ('usuario', 'jogo')

    def __str__(self):
        return f"Jornada de {self.usuario.username} em {self.jogo.titulo}"

    @property
    def porcentagem_conclusao(self):
        if self.trofeus_totais == 0:
            return 0
        porcentagem = (self.trofeus_conquistados / self.trofeus_totais) * 100
        return round(porcentagem)
    
    def clean(self):
        if self.trofeus_conquistados > self.trofeus_totais:
            raise ValidationError('O número de troféus conquistados não pode ser maior que o total.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    generos_favoritos = models.JSONField(default=list, blank=True)

    avatar = models.CharField(max_length=255, blank=True, null=True, help_text="Caminho para o avatar predefinido")
    jogo_favorito = models.ForeignKey(Jogo, on_delete=models.SET_NULL, null=True, blank=True, related_name="perfis_favoritos")

    def __str__(self):
        return f'Perfil de {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
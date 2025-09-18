from django.db import models

# Create your models here.

class buscar(models.Model):
    titulo = models.CharField(max_length=200)
    desenvolvedor = models.CharField(max_length=200, blank=True)
    ano_lancamento = models.DateField(blank=True)
    genero = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.titulo
    
class avaliar(models.Model):
    nota = models.IntegerField(max_length=1) # 5 estrelas
    comentario = models.CharField(max_length=1000)



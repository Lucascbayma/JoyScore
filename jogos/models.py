from django.db import models

# Create your models here.

class Buscar(models.Model):
    titulo = models.CharField(max_length=200)
    desenvolvedor = models.CharField(max_length=200, blank=True)
    ano_lancamento = models.DateField(blank=True,null=True)
    genero = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.titulo
    
class Avaliar(models.Model):
    Buscar = models.ForeignKey(Buscar, on_delete=models.CASCADE, related_name="avaliacoes")
    nota = models.IntegerField(
        validacao=[MinValueValidator(1),MaxValueValidator(5)] # 5 estrelas
    ) 
    comentario = models.CharField(max_length=1000)

    def __str__(self):
        return f" Avaliação: {self.titulo} - {self.nota} estrelas"
    

class Add_Biblioteca(models.Model):
    titulo = models.CharField(max_length=200)
    desenvolvedor = models.CharField(max_length=200, blank=False)
    ano_lancamento = models.DateField(blank=False,null=False)
    genero = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return f"{self.titulo} adicionado na biblioteca!"

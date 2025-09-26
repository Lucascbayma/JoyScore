from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Jogo, Avaliar, Add_Biblioteca

class JogoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'desenvolvedor', 'genero', 'ano_lancamento')
    search_fields = ('titulo', 'desenvolvedor', 'genero')
    list_filter = ('genero', 'desenvolvedor')
    ordering = ('titulo',)

class AvaliarAdmin(admin.ModelAdmin):
    list_display = ('Jogo', 'usuario', 'nota', 'comentario')
    list_filter = ('Jogo', 'usuario', 'nota')
    list_editable = ('nota',)
    ordering = ('-id',) 

class AddBibliotecaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'jogo', 'data_adicionado')
    list_filter = ('data_adicionado',)
    search_fields = ('jogo__titulo', 'usuario__username')
    readonly_fields = ('data_adicionado',)

admin.site.register(Jogo, JogoAdmin)
admin.site.register(Avaliar, AvaliarAdmin)
admin.site.register(Add_Biblioteca, AddBibliotecaAdmin)

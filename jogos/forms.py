from django import forms
from .models import Avaliar

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliar 
        
        fields = ['nota', 'comentario'] 

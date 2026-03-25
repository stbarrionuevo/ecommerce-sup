from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistroFormularioPersonalizado(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=50,required=True, label="Apellido")
    email= forms.EmailField(required=True, label="Correo Electronico")


class Meta:
    model = User
    fields = ['username','first_name','last_name','email']
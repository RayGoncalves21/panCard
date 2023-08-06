from django import forms


class EnviarImagemForm(forms.Form):
    arquivo = forms.FileField(label='arquivo')

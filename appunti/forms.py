from django import forms

class Login(forms.Form):
    nomeutente=forms.CharField(required=True,max_length=30)
    password=forms.CharField(widget=forms.PasswordInput(),required=True,max_length=30)

class AddApp(forms.Form):
    nome=forms.CharField(required=True,max_length=50)
    etichetta=forms.CharField(required=True,max_length=25)
    pagine=forms.CharField(required=True,max_length=4)
    prezzo=forms.CharField(required=True,max_length=4)
    anno=forms.CharField(required=True,max_length=1)
    codicecorso=forms.CharField(required=True,max_length=6)
    info=forms.CharField(required=True,max_length=1000)

class CorsiForm(forms.Form):
    nome=forms.CharField(required=True,max_length=50)

class ImpostaApp(forms.Form):
    nomeutente=forms.CharField(required=True,max_length=30)
    password=forms.CharField(required=False,max_length=30)
    codicefile=forms.CharField(required=True,max_length=10)
    tipo=forms.CharField(required=False,max_length=1)

class Cambiopassword(forms.Form):
    vecchia=forms.CharField(required=True,max_length=30)
    nuova=forms.CharField(required=True,max_length=30)
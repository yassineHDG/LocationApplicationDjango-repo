
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Objet
from .models import Avis
from django import forms
from .models import Reservation

# Formulaire d'inscription
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Prénom", max_length=30, required=True)
    last_name = forms.CharField(label="Nom", max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# Formulaire de connexion
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class ObjetForm(forms.ModelForm):
    class Meta:
        model = Objet
        fields = ['nom', 'description', 'prix', 'disponibilite', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'prix': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo_profil']

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['commentaire', 'note']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Laisser un commentaire...'}),
            'note': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }



class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_debut', 'date_fin']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'format': '%m-%d-%Y'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'format': '%m-%d-%Y'}),
        }

from django import forms
from .models import Contrat
class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = ['texte']

from django import forms

class PaiementForm(forms.Form):
    numero_carte = forms.CharField(label="Numéro de carte", max_length=16)
    nom_titulaire = forms.CharField(label="Nom du titulaire", max_length=100)
    date_expiration = forms.CharField(label="Date d'expiration", max_length=5)
    cvv = forms.CharField(label="CVV", max_length=4)

from django import forms

class RemboursementForm(forms.Form):
    raison = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label="Raison du remboursement")

from django import forms
from .models import Messagerie

class MessageForm(forms.ModelForm):
    class Meta:
        model = Messagerie
        fields = ['body']  # On n'utilise pas 'subject' ici car ce champ est optionnel dans la messagerie rapide
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Écrire un message...',
                'class': 'form-control',
            }),
        }


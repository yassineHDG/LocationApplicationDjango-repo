from django.db import models

# Create your models here.
# base/models.py
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    # Les fichiers seront uploadés vers MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    biographie = models.TextField()
    note_moyenne = models.DecimalField(max_digits=3, decimal_places=2)
    nb_locations = models.IntegerField()
    fiabilite = models.DecimalField(max_digits=5, decimal_places=2)
    photo_profil = models.ImageField(upload_to='images/', default='images/default.jpg')
    
        
    def __str__(self):
        return self.user.username

class Avis(models.Model):
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avis_auteurs")
    cible = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avis_recepteurs")
    note = models.IntegerField()  # Note donnée entre 1 et 5
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avis de {self.auteur.username} pour {self.cible.username} - {self.note}/5"
    
    
class Objet(models.Model):
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilite = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.nom 
    
class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('refusee', 'Refusée'),
    ]
     
    objet = models.ForeignKey(Objet, on_delete=models.CASCADE)
    locataire = models.ForeignKey(User, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"{self.objet.nom} réservé par {self.locataire.username} ({self.statut})"
    


class Contrat(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    texte = models.TextField()
    date_signature = models.DateField(null=True, blank=True)
    est_signe = models.BooleanField(default=False)

    def __str__(self):
        return f"Contrat pour {self.reservation.objet.nom} - {self.reservation.locataire.username}"
    
class Paiement(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    etat = models.CharField(max_length=20, choices=[('effectué', 'Effectué'), ('remboursé', 'Remboursé')])
    date_paiement = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Paiement de {self.montant_total}€ pour {self.reservation.objet.nom}"

class Facture(models.Model):
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    detail = models.TextField()
    date_emission = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Facture pour {self.paiement.reservation.objet.nom}"

class Remboursement(models.Model):
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    raison = models.TextField()
    date_remboursement = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Remboursement de {self.montant}€ pour {self.paiement.reservation.objet.nom}"
    

from django.db import models
from django.contrib.auth.models import User

class Messagerie(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.sender.username} à {self.recipient.username} : {self.subject}"

    




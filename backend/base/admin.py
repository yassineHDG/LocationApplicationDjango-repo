from django.contrib import admin
from .models import Profile
from .models import Avis
from .models import Objet
from .models import Contrat 
from .models import Reservation
from .models import Paiement
from .models import Facture
from .models import Remboursement
# Register your models here.

admin.site.register(Profile)
admin.site.register(Avis)
admin.site.register(Objet)
admin.site.register(Contrat)
admin.site.register(Reservation)   
admin.site.register(Paiement)
admin.site.register(Facture)
admin.site.register(Remboursement)
 

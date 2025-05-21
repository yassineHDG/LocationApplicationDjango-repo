from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.db.models import Avg

from .models import Profile, Avis, Objet, Reservation
from .forms import RegisterForm, LoginForm, ObjetForm, AvisForm, ReservationForm
from datetime import timedelta
from .models import Contrat
from .forms import ContratForm


from django.views import View
from django.shortcuts import render
from .models import Reservation, Contrat
from .forms import PaiementForm
from .models import Paiement, Facture
from .models import Remboursement
from .forms import RemboursementForm


class Home(View):
    def get(self, request):
        contrats_non_signes = []
        if request.user.is_authenticated:
            reservations_confirmées = Reservation.objects.filter(locataire=request.user, statut='confirmée')
            contrats_non_signes = Contrat.objects.filter(reservation__in=reservations_confirmées, est_signe=False)

        return render(request, "home.html", {
            'contrats_non_signes': contrats_non_signes
        })




class Register(View):
    def get(self, request):
        return render(request, 'register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Création du profil avec les données du formulaire
            Profile.objects.create(
                user=user,
                biographie="",
                note_moyenne=0.0,
                nb_locations=0,
                fiabilite=100.0,
                photo_profil='images/default.jpg'
            )
            return redirect('/api/Home')
        return render(request, 'register.html', {'form': form})

class Login(View):
    def get(self, request):
        return render(request, 'login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/api/Home')
        return render(request, 'login.html', {'form': form})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('/api/Home')


class UserProfile(View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        user_profile = Profile.objects.get(user=user)
        avis_list = Avis.objects.filter(cible=user)
        moyenne = avis_list.aggregate(moyenne=Avg('note'))['moyenne'] or 0.0
        return render(request, 'profile.html', {
            'user_profile': user_profile,
            'avis_list': avis_list,
            'note_moyenne': round(moyenne, 2),
        })


@method_decorator(login_required, name='dispatch')
class EditBiographie(View):
    def get(self, request):
        return render(request, 'edit_biographie.html', {'biographie': request.user.profile.biographie})

    def post(self, request):
        profile = request.user.profile
        profile.biographie = request.POST.get('biographie')
        profile.save()
        return redirect(f'/api/Profile/{request.user.id}/')


class AjouterAvis(View):
    def get(self, request, user_id):
        cible = get_object_or_404(User, pk=user_id)
        return render(request, 'ajouter_avis.html', {'form': AvisForm(), 'cible': cible})

    def post(self, request, user_id):
        cible = get_object_or_404(User, pk=user_id)
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.auteur = request.user
            avis.cible = cible
            avis.save()
            return redirect(f'/api/Profile/{user_id}/')
        return render(request, 'ajouter_avis.html', {'form': form, 'cible': cible})


class ObjectList(View):
    def get(self, request):
        objets = Objet.objects.all()  # Récupérer tous les objets

        for objet in objets:
            # Trouver la dernière réservation confirmée pour chaque objet
            last_reservation = Reservation.objects.filter(
                objet=objet,
                statut="confirmée"
            ).order_by('-date_fin').first()

            if last_reservation:
                prochaine_dispo = last_reservation.date_fin + timedelta(days=1)
                objet.prochaine_dispo = prochaine_dispo
            else:
                objet.prochaine_dispo = None  # Pas de réservation, donc l'objet est disponible

        return render(request, 'object_list.html', {'objets': objets})


@method_decorator(login_required, name='dispatch')
class ObjectAdd(View):
    def get(self, request):
        form = ObjetForm()
        return render(request, 'add_object.html', {'form': ObjetForm()})

    def post(self, request):
        form = ObjetForm(request.POST, request.FILES)
        if form.is_valid():
            objet = form.save(commit=False)
            objet.proprietaire = request.user
            objet.save()
            return redirect('object_list')
        return render(request, 'add_object.html', {'form': form})


class ObjectEdit(UpdateView):
    model = Objet
    form_class = ObjetForm
    template_name = 'modify.html'
    success_url = reverse_lazy('object_list')


class ObjectDelete(DeleteView):
    model = Objet
    template_name = 'delete.html'
    success_url = reverse_lazy('object_list')


class ReservationCreate(View):
    def get(self, request, objet_id):
        objet = get_object_or_404(Objet, pk=objet_id)
        return render(request, 'reservation_form.html', {'form': ReservationForm(), 'objet': objet})

    def post(self, request, objet_id):
        objet = get_object_or_404(Objet, pk=objet_id)
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.objet = objet
            reservation.locataire = request.user
            reservation.save()
            return redirect('object_list')
        return render(request, 'reservation_form.html', {'form': form, 'objet': objet})
    
    def form_valid(self, form):
        date_debut = form.cleaned_data['date_debut']
        date_fin = form.cleaned_data['date_fin']
        objet = self.kwargs['objet_id']

        # Vérifier les chevauchements avec les réservations existantes
        conflits = Reservation.objects.filter(
            objet_id=objet,
            statut="confirmée",
            date_debut__lt=date_fin,
            date_fin__gt=date_debut,
        )

        if conflits.exists():
            form.add_error(None, "Cet objet est déjà réservé sur cette période.")
            return self.form_invalid(form)

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ReservationsAConfirmerView(ListView):
    model = Reservation
    template_name = 'reservations_a_confirmer.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.filter(
            objet__proprietaire=self.request.user,
            statut='en_attente'
        )


@require_POST
@login_required
def refuser_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, objet__proprietaire=request.user)
    reservation.statut = 'refusée'
    reservation.save()
    return redirect('reservations_a_confirmer')

@login_required
def confirmer_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, objet__proprietaire=request.user)
    reservation.statut = 'confirmée'
    reservation.save()
    
    # Rediriger vers la création du contrat
    return redirect('creer_contrat', reservation_id=reservation.id)



class CreerContratView(View):
    def get(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        form = ContratForm()
        return render(request, 'creer_contrat.html', {'form': form, 'reservation': reservation})

    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        form = ContratForm(request.POST)
        if form.is_valid():
            contrat = form.save(commit=False)
            contrat.reservation = reservation
            contrat.save()
            return redirect('reservations_a_confirmer')  # ou une autre page
        return render(request, 'creer_contrat.html', {'form': form, 'reservation': reservation})
    
from datetime import date
class SignerContratView(View):
    def post(self, request, contrat_id):
        contrat = get_object_or_404(Contrat, id=contrat_id)
        if request.user == contrat.reservation.locataire:
            contrat.est_signe = True
            contrat.date_signature = date.today()
            contrat.save()
        return redirect('paiement', reservation_id=contrat.reservation.id)
    
class PaiementView(View):
    def get(self, request, reservation_id):
        form = PaiementForm()
        reservation = get_object_or_404(Reservation, id=reservation_id)
        montant_total = reservation.objet.prix * ((reservation.date_fin - reservation.date_debut).days + 1)
        return render(request, 'paiement.html', {'form': form, 'montant_total': montant_total, 'reservation': reservation})

    def post(self, request, reservation_id):
        form = PaiementForm(request.POST)
        reservation = get_object_or_404(Reservation, id=reservation_id)
        montant_total = reservation.objet.prix * ((reservation.date_fin - reservation.date_debut).days + 1)

        if form.is_valid():
            paiement = Paiement.objects.create(
                reservation=reservation,
                montant_total=montant_total,
                etat='effectué'
            )
            Facture.objects.create(
                paiement=paiement,
                montant=montant_total,
                detail=f"Paiement pour {reservation.objet.nom} du {reservation.date_debut} au {reservation.date_fin}"
            )
            return redirect('facture_detail', paiement_id=paiement.id)
        return render(request, 'paiement.html', {'form': form, 'montant_total': montant_total, 'reservation': reservation})

class FactureDetailView(View):
    def get(self, request, paiement_id):
        paiement = get_object_or_404(Paiement, id=paiement_id)
        facture = get_object_or_404(Facture, paiement=paiement)
        return render(request, 'facture.html', {'facture': facture})
    
class DemanderRemboursementView(View):
    def get(self, request, paiement_id):
        paiement = get_object_or_404(Paiement, id=paiement_id)
        form = RemboursementForm()
        return render(request, 'demande_remboursement.html', {'form': form, 'paiement': paiement})

    def post(self, request, paiement_id):
        paiement = get_object_or_404(Paiement, id=paiement_id)
        form = RemboursementForm(request.POST)
        if form.is_valid():
            Remboursement.objects.create(
                paiement=paiement,
                montant=paiement.montant_total,
                raison=form.cleaned_data['raison']
            )
            return redirect('home')  # ou vers une page de confirmation
        return render(request, 'demande_remboursement.html', {'form': form, 'paiement': paiement})
    
# Nouvelles vues pour les fonctionnalités demandées

@method_decorator(login_required, name='dispatch')
class ListeFacturesView(View):
    def get(self, request):
        # Récupérer toutes les factures de l'utilisateur connecté
        factures = Facture.objects.filter(
            paiement__reservation__locataire=request.user
        ).select_related('paiement', 'paiement__reservation', 'paiement__reservation__objet')
        
        return render(request, 'factures_liste.html', {'factures': factures})

@method_decorator(login_required, name='dispatch')
class ListeRemboursementsView(View):
    def get(self, request):
        # Récupérer tous les remboursements de l'utilisateur connecté
        remboursements = Remboursement.objects.filter(
            paiement__reservation__locataire=request.user
        ).select_related('paiement', 'paiement__reservation', 'paiement__reservation__objet')
        
        return render(request, 'remboursements_liste.html', {'remboursements': remboursements})
    
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def modifier_photo(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=request.user.id)  
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'modifier_photo.html', {'form': form})



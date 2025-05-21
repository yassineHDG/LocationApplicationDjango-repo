from django.urls import path
from . import views 
from .views import Profile
from .views import ReservationsAConfirmerView
from .views import confirmer_reservation, refuser_reservation
from .views import CreerContratView, SignerContratView
from .views import PaiementView
from .views import FactureDetailView
from .views import ListeFacturesView
from .views import ListeRemboursementsView

urlpatterns=[
    path('Home/',views.Home.as_view(),name='home'),
    path('Register/',views.Register.as_view(),name='register'),
    path('Login/',views.Login.as_view(),name='login'),
    path('Profile/<int:user_id>/', views.UserProfile.as_view(), name='profile'),
    path('Object/',views.ObjectList.as_view(),name='object_list'),
    path('Add/', views.ObjectAdd.as_view(), name='add_objet'),
    path('Modify/<int:pk>/', views.ObjectEdit.as_view(), name='modify_objet'),
    path('Delete/<int:pk>/', views.ObjectDelete.as_view(), name='delete_objet'),
    path('Logout/', views.Logout.as_view(), name='logout'),
    path('Avis/<int:user_id>/', views.AjouterAvis.as_view(), name='ajouter_avis'),
    path('EditBiographie/', views.EditBiographie.as_view(), name='edit_biographie'),
    path('Reservation/<int:objet_id>/', views.ReservationCreate.as_view(), name='reservation'),
    path('reservations/a_confirmer/', ReservationsAConfirmerView.as_view(), name='reservations_a_confirmer'),
    path('reservations/<int:reservation_id>/confirmer/', confirmer_reservation, name='confirmer_reservation'),
    path('reservations/<int:reservation_id>/refuser/', refuser_reservation, name='refuser_reservation'),
    path('contrat/creer/<int:reservation_id>/', CreerContratView.as_view(), name='creer_contrat'),
    path('contrat/signer/<int:contrat_id>/', SignerContratView.as_view(), name='signer_contrat'),
    path('paiement/<int:reservation_id>/', PaiementView.as_view(), name='paiement'),
    path('facture/<int:paiement_id>/', FactureDetailView.as_view(), name='facture_detail'),
    path('remboursement/<int:paiement_id>/', views.DemanderRemboursementView.as_view(), name='demander_remboursement'),
    path('modifier-photo/', views.modifier_photo, name='modifier_photo'),


    # Nouvelles routes pour les fonctionnalités demandées
    path('factures/', ListeFacturesView.as_view(), name='factures_liste'),
    path('remboursements/', ListeRemboursementsView.as_view(), name='remboursements_liste'),




]



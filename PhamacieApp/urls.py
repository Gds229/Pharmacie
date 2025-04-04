from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django import views
from PhamacieApp import views
urlpatterns=[
path('produits.html',views.Produits,name="produits"),
path('phamacie.html',views.Phamacie,name="phamacie"),
path('compte.html',views.Compte,name="compte"),
path('compte.html',views.Deconnexion,name="deconnexion"),
path('inscription.html',views.Inscription,name="inscription"),
path('forgetpassword.html',views.Forgetpassword,name="forgetpassword"),
path('commandeproduit.html/<int:idProduit>',views.Commandeproduit,name="commandeproduit"),
path('profilpharmacie.html/<int:idProfil>',views.Profilpharmacie,name="profilpharmacie"),
path('pagesmontant.html/<int:idProduit>/<int:idDem>',views.Pagesmontant,name="pagesmontant"),


path('Utilisateur/dashbord.html/<int:idUser>',views.Tableaudebord,name="tableaudebord"),
path('Utilisateur/demande_achat.html/<int:idUser>',views.Demande_achat,name="demande_achat"),
path('Utilisateur/demande_achat.html/<int:idUser>/<int:idDed>',views.DemandeRefuser,name="demandeRefuser"),
path('Utilisateur/demande_achat.html/<int:idUser>/<int:idDemd>/0',views.DemandeValider,name="demandeValider"),
path('Utilisateur/reçudemande.html/<int:idDem>',views.Reçudemande,name="reçudemande"),
path('Utilisateur/produits_dispo.html/<int:idUser>',views.Produits_dispo,name="produits_dispo"),
path('Utilisateur/new_produits.html/<int:idUser>',views.New_produits,name="new_produits"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

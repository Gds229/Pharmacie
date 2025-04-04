

import codecs
from datetime import date, datetime
from email.mime import text
from django.contrib.auth.tokens import default_token_generator
from django.utils.datastructures import MultiValueDict
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
import os
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import  authenticate,login,logout
from django.contrib.auth.password_validation import validate_password

from Phamacie import settings
from PhamacieApp.models import Demande, Phamaciens, Produit
def Home(request):
    phamacie=Phamaciens.objects.all()
    return render(request,'index.html',{'phamacie':phamacie})

def Commandeproduit(request,idProduit):
    produit=Produit.objects.filter(id=idProduit)
    produits=Produit.objects.get(id=idProduit) 
    pr=produits.getprix()
    messages=""
    if request.method=="POST":
        nom=request.POST.get('nom')
        prenom=request.POST.get('prenom')
        tel=request.POST.get('tel')
        qte=request.POST.get('qte')
        position=request.POST.get('position')
        t=Demande(
            nom=nom,
            prenom=prenom,
            tel=tel,
            quantité=qte,
            position=position,
            date_demd=datetime.now(),
            produit_id=idProduit,
            #phamaciens_id=int(phamacies)
        )
        t.phamaciens=t.produit.phamaciens
        t.save(),
        if t:
                messages="Commande envoyé"
                quantite=int(qte)  
                montant=int(pr)*quantite
                demande=Demande.objects.filter(id=t.id)
                return render(request,'pagesmontant.html',{'demande':demande,'produit':produit,'messages':messages,'quantite':quantite,'montant':montant})     
        else:
            messages="Commande non envoyé"
    return render(request,'commandeproduit.html',{'produit':produit,'messages':messages})

def Pagesmontant(request,idProduit,idDem):
    produit=Produit.objects.filter(id=idProduit)
    demande=Demande.objects.filter(id=idDem)
    produits=Produit.objects.get(id=idProduit)
    demandes=Demande.objects.get(id=idDem)
    quantite=demande.getqte()
    montant=int(produits.grtprix())*int(quantite)
    return render(request,'pagesmontant.html',{'produit':produit,'quantite':quantite,'montant':montant})

def Profilpharmacie (request,idProfil):
    profil=Phamaciens.objects.filter(id=idProfil)
    return render(request,'profilphamacie.html',{'profil':profil}) 

def Produits(request):
    produits=Produit.objects.all()
    phamacie=Phamaciens.objects.all()
    produitall=Produit.objects.all()
    return render(request,'produits.html',{'produits':produits,'phamacie':phamacie,'produitall':produitall})

def Phamacie(request):
    phamacie=Phamaciens.objects.all()
    return render(request,'phamacie.html',{'phamacie':phamacie})

def Compte(request):
    messages=''
    if request.method=='POST':
        username=request.POST.get('name')
        password=request.POST.get('pass')
        user=User.objects.filter(username=username).first()
        if user:
            auth_user=authenticate(username=user.username,password=password) 
            if auth_user:
                login(request,auth_user)
                #return redirect('tableaudebord')  
                produitT=Produit.objects.count()
                if produitT==0:
                    produitT=1
                produits=Produit.objects.filter(phamaciens_id=auth_user.id).count()
                produitsPoucentage=((produits*100)/produitT)
                demandeT=Demande.objects.count()
                if demandeT==0:
                    demandeT=1
                demandes=Demande.objects.filter(decisions=0,phamaciens_id=auth_user.id).count()
                demandesPoucentage=((demandes*100)/demandeT)
                demande_valider=Demande.objects.filter(decisions=1,phamaciens_id=auth_user.id).count()
                demandesValiderPoucentage=((demande_valider*100)/demandeT)
                demande_refuser=Demande.objects.filter(decisions=2,phamaciens_id=auth_user.id).count()
                demandesRefuserPoucentage=((demande_refuser*100)/demandeT)
                phamacie=Phamaciens.objects.filter(id=auth_user.id)
                #les fonctions du diagramme en batôn
                #   demandesPremierMois=Demande.objects.filter(date_demd__year=2025,date_demd__month=2).count()
                return render(request,'Utilisateur/dashbord.html',{'phamacie':phamacie,'produits':produits,'demandes':demandes,'demande_valider':demande_valider,'demande_refuser':demande_refuser,'produitsPoucentage':produitsPoucentage,'demandesPoucentage':demandesPoucentage,'demandesValiderPoucentage':demandesValiderPoucentage,'demandesRefuserPoucentage':demandesRefuserPoucentage})
            else:
                messages='Erreur d\'authentification'
                return render(request,'compte.html',{'messages':messages})
        else:
            messages='L\'utilisateur n\' existe pas'
            return render(request,'compte.html',{'messages':messages})
    else:
        messages='Les données ne sont pas prise.Veuillez remplir les champs'
        return render(request,'compte.html',{'messages':messages})
def DemandeValider(request,idUser,idDemd):
    demande=Demande.objects.filter(phamaciens_id=idUser,decisions=0)
    demandeIdentifier=Demande.objects.filter(phamaciens_id=idDemd ).first()
    if demandeIdentifier.decisions=='0':
        demandeIdentifier.decisions='1'
        demandeIdentifier.save(),
        if demandeIdentifier.decisions=='1':
            email='gbadessiaime5@gmail.com'
            current_site=request.META['HTTP_HOST']
            html_text=render_to_string("email_décision.html",{"domaine":f"http://{current_site}"})
            send_mail(
                     'Décision de la pharmacie ', 
                     'Le(La) pharmacien(ne) a accepté votre demande.Merci',
                     'settings.EMAIL_HOST_USER',
                     [email],
                     fail_silently=False,
                     
            )
    return render(request,'Utilisateur/demande_achat.html',{'demande':demande}) 

def DemandeRefuser(request,idUser,idDed):
    demande=Demande.objects.filter(phamaciens_id=idUser,decisions=0)
    demandeIdentifier=Demande.objects.filter(phamaciens_id=idDed).first()
    if demandeIdentifier.decisions=='0':
        demandeIdentifier.decisions='2'
        demandeIdentifier.save(),
        if demandeIdentifier.decisions=='2':
            email='gbadessiaime5@gmail.com'
            current_site=request.META['HTTP_HOST']
            html_text=render_to_string("email_décision.html",{"domaine":f"http://{current_site}"})
            send_mail(
                     'Décision de la pharmacie',
                     'Le(La) pharmacien(ne) a réjeté votre demande.Merci',
                     'settings.EMAIL_HOST_USER', 
                     [email],
                     fail_silently=False,
            )
            
    return render(request,'Utilisateur/demande_achat.html',{'demande':demande})

def Reçudemande (request,idDem):
    demande=Demande.objects.get(id=idDem)
    return render(request,'Utilisateur/reçudemande.html',{'demande':demande})

def Inscription(request):
      message=""
      #postes=Postes.objects.all()
      if request.method=='POST':
         nom=request.POST.get('nom')
         prenom=request.POST.get('prenom')
         email=request.POST.get('email')
         nomPhamacies=request.POST.get('nomPhamaciens')
         tel=request.POST.get('tel')
         photoprofil=request.FILES.get('photoprofil')
         sexe=request.POST.get('sexe')
         datenaissance=request.POST.get('datenaissance')
         motdepasse=request.POST.get('motdepasse')
         Cmotdepasse=request.POST.get('Cmotdepasse')
         descrp=request.POST.get('descrip')
         

         #Vérifier si le tel et email existe déja
         if Phamaciens.objects.filter(tel=tel).exists():
            message = "Ce numéro de téléphone est déjà enregistré veillez saisir un autre."
            return render(request,  'Promotion/inscription.html', {'messagesTelExistant':message})
         else:
             if Phamaciens.objects.filter(email=email).exists():
               message = "Ce mail est déjà enregistré veillez saisir un autre."
               return render(request, 'Promotion/inscription.html', {'messagesEmailExistant':message})
             else:
                if Phamaciens.objects.filter(motdepasse=motdepasse).exists():
                  message = "Ce mot de passe existe déjà"
                  return render(request, 'Promotion/inscription.html', {'messagesEmailExistant':message})
                else:
                   if str(motdepasse)==str(Cmotdepasse):
                    #""" Création d'une instance du personnel """
                    u=Phamaciens(
                     nom=nom,
                     prenom=prenom,
                     sexe=sexe,
                     nomphamacie=nomPhamacies,
                     nomPhamaciens=nom+' '+prenom,
                     datenaissance=datenaissance,
                     tel=tel,
                     email=email,
                     code='',
                     image=photoprofil,
                     motdepasse=motdepasse,
                     Cmotdepasse=Cmotdepasse,
                     descrp=descrp,    
                     )
                    r=User(
                        username=nomPhamacies,
                        email=email,
                     )
                    r.password=motdepasse
                    r.set_password(r.password)
                     #""" Enregistrement dans la base de donnée """
                    u.save(),
                    r.save(),
                    if u:
                     #Enregistrer les images
                     photoprofile=request.FILES['photoprofil']
                     destination =  os.path.join(settings.MEDIA_ROOT, 'images')
                     file_path = os.path.join(destination, photoprofile.name)
                     with open(file_path, 'wb') as destination:
                        for chunk in photoprofile.chunks():
                         destination.write(chunk)
                     if chunk:
                        return render(request,'compte.html')
                    else:
                     message="Echec" 
                   else:
                    message = "le mot de passe et la confirmation ne sont identiques"
                    return render(request, 'inscription.html', {'messagesEmailExistant':message})
      return render(request,'inscription.html',{'messagevalide':message})

def Forgetpassword(request):
    messages=''
    try:
        if request.method=='POST':
            email=request.POST.get('email')
            print(email)
            user=User.objects.filter(email=email).first()
            if user:
                token=default_token_generator.make_token(user)
                uid=urlsafe_base64_encode(force_bytes(user.id))
                current_site=request.META['HTTP_HOST']
                html_text=render_to_string("email.html",{"token":token,"uid":uid,"domaine":f"http://{current_site}"})
                send_mail(
                        'Mot de passe oublié',
                        'PHAMA-COUFFO',
                        'settings.EMAIL_HOST_USER', 
                        'aimegbadessi@gmail.com',
                        [email],
                        fail_silently=False,
                        html_message=html_text
                    )
                if send_mail:
                    messages='E-mail envoyé avec succès'
                else:
                    messages='Erreur lors de l\'envoi de l\'e-mail et n\'est pas envoyé'
            else:
                messages='Le mail n\'existe pas'
    except Exception as e:
            # Vous pouvez personnaliser le message d'erreur ou la gestion d'exception
            messages=f"Une erreur s'est produite : vérifier votre connexion et votre mail. {str(e)}"
            return render(request,'forgetpassword.html',{'messages':messages})
    return render(request,'forgetpassword.html',{'messages':messages}) 

def Updatepassword(request,token,uid):
    messages=""
    try:
       user_id=urlsafe_base64_decode(uid)
       decode_uid=codecs.decode(user_id,'utf-8')
       user=User.objects.get(id=decode_uid)
    except:
        return HttpResponseForbidden("Vous n'avez pas la permission de modifier ce mot de passe. Utilisateur introuvable.")
    check_token=default_token_generator.check_token(user,token)
    if not check_token:
        return HttpResponseForbidden("Vous n'avez pas la permission de modifier ce mot de passe. Votre token est invalid ou.")
    
    error=False
    success=False
    messages=""
    if request.method == 'POST':
        password=request.POST.get('motdepasse')
        Cpassword=request.POST.get('Cmotdepasse')
        print(password,Cpassword)
        if password==Cpassword:
            try:
                validate_password(password,user)
                user.set_password(password)
                user.save()
                messages="Votre mot de passe à été modifié avec succès"
            except ValidationError :
                messages="Votre mail est invalide"
        else:
            messages="les eux mot de passe ne sont pas identiques"
    return render(request,'forgetpassword.html',{'messages':messages}) 

def Tableaudebord(request,idUser):
    produitT=Produit.objects.count()
    if produitT==0:
        produitT=1
    produits=Produit.objects.filter(phamaciens_id=idUser).count()
    produitsPoucentage=((produits*100)/produitT)
    demandeT=Demande.objects.count()
    if demandeT==0:
        demandeT=1
    demandes=Demande.objects.filter(decisions=0,phamaciens_id=idUser).count()
    demandesPoucentage=((demandes*100)/demandeT)
    demande_valider=Demande.objects.filter(decisions=1,phamaciens_id=idUser).count()
    demandesValiderPoucentage=((demande_valider*100)/demandeT)
    demande_refuser=Demande.objects.filter(decisions=2,phamaciens_id=idUser).count()
    demandesRefuserPoucentage=((demande_refuser*100)/demandeT)
    phamacie=Phamaciens.objects.filter(id=idUser)
    return render(request,'Utilisateur/dashbord.html',{'phamacie':phamacie,'produits':produits,'demandes':demandes,'demande_valider':demande_valider,'demande_refuser':demande_refuser,'produitsPoucentage':produitsPoucentage,'demandesPoucentage':demandesPoucentage,'demandesValiderPoucentage':demandesValiderPoucentage,'demandesRefuserPoucentage':demandesRefuserPoucentage})

def Demande_achat(request,idUser):
   demande=Demande.objects.filter(phamaciens_id=idUser)
   return render(request,'Utilisateur/demande_achat.html',{'demande':demande})

def Produits_dispo(request,idUser):
   produits=Produit.objects.filter(phamaciens_id=idUser)
   return render(request,'Utilisateur/produits_dispo.html',{'produits':produits})

def New_produits(request,idUser):
    messages=""
    if request.method == 'POST':
      nom=request.POST.get('nomproduit')
      poids=request.POST.get('poidsproduit')
      etat=request.POST.get('etat')
      couleur=request.POST.get('couleur')
      prix=request.POST.get('prixproduit')
      nbcpm=request.POST.get('nbrcprproduit')
      imageproduit=request.FILES.get('imageproduit')
      if Produit.objects.filter(nom=nom,poids=poids,etat=etat,phamaciens_id=idUser).exists():
          messages="Ce comprimé existe déjà dans votre phamacie"
      else:
        v=Produit(
            nom=nom,
            poids=poids,
            etat=etat,
            couleur=couleur,
            prix=prix,
            nbr_comprime=nbcpm,
            image=imageproduit,
            date_enreg=date.today(),
            phamaciens_id=idUser,
        )
        v.save(),
        if v:
            #Enregistrer les images
            images=request.FILES['imageproduit']
            destinations = os.path.join(settings.MEDIA_ROOT, 'images/produits/')
            file_paths = os.path.join(destinations, images.name)
            with open(file_paths, 'wb') as destinations:
                for chunks in images.chunks():
                    destinations.write(chunks)
            if chunks:
                messages="Enregistrer avec succès"
        else:
            messages="Erreur d'enregistrement "
    produits=Produit.objects.filter(phamaciens_id=idUser,date_enreg=date.today())
    return render(request,'Utilisateur/new_produits.html',{'messages':messages,'produits':produits})

def Deconnexion(request):
    logout(request)
    return redirect('compte')

def Recupdf(request):
    #générer le pdf 
    #enregister le pdf dans la base de données
    return

def RecuTelecharger(request):
    #Téléharger les réçus 
    return

def Listerecu(request):
    #Afficher la listes des réçus de chaque Pharmacie
    return

# Create your views here.

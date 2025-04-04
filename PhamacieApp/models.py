import random
import string
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.db import models
from django.forms import ValidationError
class Phamaciens(models.Model):
    nom=models.CharField(max_length=100,default='')
    prenom = models.CharField(max_length=100,default='')
    sexe = models.CharField(max_length=15,default='')
    nomphamacie = models.CharField(max_length=100,default='')
    descrp=models.CharField(max_length=1000,default='Pas de description')
    datenaissance=models.CharField(max_length=15,default='00/00/0000')
    tel = models.CharField(max_length=50,default='')
    email = models.CharField(max_length=150,default='')
    nomPhamaciens=models.CharField(max_length=100,default='')
    motdepasse=models.CharField(max_length=100,default='')
    Cmotdepasse=models.CharField(max_length=100,default='')
    status = models.CharField(default='phamacien',max_length=30)
    code = models.CharField(max_length=6, default='')
    image = models.ImageField(upload_to='images/', blank=True, null=True)# Spécifiez le dossier de téléchargement des images
    
    def __init__(self, *args, **kwargs):
        photoprofil = kwargs.pop('photoprofil', None)
        super().__init__(*args, **kwargs)
        if photoprofil:
            self.image = photoprofil



    def generate_code(self):
        characters = string.ascii_letters + string.digits  # Lettres et chiffres
        code = ''.join(random.choice(characters) for _ in range(6))  # Générer une chaîne aléatoire de 6 caractères
        return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()  # Générer un code aléatoire s'il n'est pas déjà défini
        super().save(*args, **kwargs)


    def __str__(self):
        return f" {self.code} {self.nom} {self.prenom}"
    
    def clean(self):
        super().clean()
        if not self.nom.isalpha() or not self.prenom.isalpha():
            raise ValidationError("Le nom et le prénom ne doivent contenir que des lettres.")

class Produit(models.Model):
    nom=models.CharField(max_length=100,default='')
    poids=models.CharField(max_length=30,default='')
    etat=models.CharField(max_length=50,default='')
    couleur=models.CharField(max_length=50,default='')
    prix=models.CharField(max_length=50,default='')
    nbr_comprime=models.CharField(max_length=10,default='')
    image=models.ImageField(upload_to='images/produits/', blank=False, null=True)# Spécifiez le dossier de téléchargement des images
    date_enreg=models.CharField(max_length=100)
    phamaciens=models.ForeignKey(Phamaciens, related_name='produit', on_delete=models.CASCADE)
    
    def getprix (self):
        return self.prix
    
    def __init__(self, *args, **kwargs):
        images = kwargs.pop('image', None)
        super().__init__(*args, **kwargs)
        if images:
            self.image = images
    
class Demande(models.Model):
    nom = models.CharField(max_length=100,default='')
    prenom = models.CharField(max_length=100,default='')
    tel = models.CharField(max_length=50,default='')
    quantité = models.CharField(max_length=50,default='')
    position = models.CharField(max_length=200,default='')
    date_demd=models.DateTimeField()
    payer=models.BooleanField(default=0)
    img_qr=models.ImageField(upload_to='images/qr/', blank=False, null=True)
    decisions=models.CharField(max_length=100,default='0')
    produit=models.ForeignKey(Produit, related_name='demande', on_delete=models.CASCADE)
    phamaciens=models.ForeignKey(Phamaciens, related_name='demande', on_delete=models.CASCADE)
    
    def getqte(self):
        return self.quantité
    
    def getallprice(self):
        return int(self.quantité)*int(self.produit.prix)
    
    def save(self,*args, **kwargs):
        img=qrcode.make(self.id)
        canvas=Image.new('RGB',(290,290),'white')
        draw=ImageDraw.Draw(canvas)
        canvas.paste(img)
        fname=f'qr-code{self.nom}{self.id}'+'.png'
        buffer=BytesIO()
        canvas.save(buffer,'PNG')
        self.img_qr.save(fname,File(buffer),save=False)
        canvas.close()
        super().save(*args, **kwargs)
        
# Create your models here.

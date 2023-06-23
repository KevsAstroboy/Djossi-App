from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Client(models.Model):

    nom_client = models.CharField(max_length=50, null=False)
    prenom_client = models.CharField(max_length=50, null=False)
    username = models.CharField(max_length=10, null=False)
    password = models.CharField(max_length=100, null=False)
    date_naissance = models.DateField(null=True)
    phone_number = models.CharField(max_length=20, null=False)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    commune = models.CharField(max_length=50, null=False)
    ville = models.CharField(max_length=50, null=False)
    photo_client = models.FileField(upload_to='avatar')
    numero_cni = models.CharField(max_length=50, null=False)
    
    # def save(self, *args, **kwargs):
    #     self.password = make_password(self.password)
    #     super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nom_client


class Service(models.Model):
    nom_service = models.CharField(max_length=50, null=False)
    description_service = models.CharField(max_length=1000,null=True)

    def __str__(self) -> str:
        return self.nom_service

class Prestataire(models.Model):

    nom_prestataire = models.CharField(max_length=50, null=False)
    prenom_prestataire = models.CharField(max_length=50, null=False)
    date_naissance = models.DateField(null=True)
    username = models.CharField(max_length=10, null=False, unique= True)
    biographie = models.CharField(max_length=1000,null=False)
    phone_number = models.CharField(max_length=20, null=False,unique=True)
    photo_prestataire = models.FileField(upload_to='avatar')
    numero_cni = models.CharField(max_length=50, null=False,unique=True)
    photo_piece_recto = models.FileField(upload_to='pieces_identite')
    photo_piece_verso = models.FileField(upload_to='pieces_identite')
    services = models.ManyToManyField(Service)
    is_active = models.BooleanField(default=False)
    password = models.CharField(max_length=100,null=False)

    # def save(self, *args, **kwargs):
        
    #     self.is_active = False  # Modifier la valeur de is_active
    #     super().save(*args, **kwargs)  # Appeler la méthode save() de la classe parente

    def __str__(self) -> str:
        return self.username

class Reservation(models.Model):

    STATUS_CHOICES = (
    ('canceled', _('Annulé')),
    ('in_progress', _('En cours')),
    ('finished', _('Terminé')),
    ('requested', _('Demandé')),
    )
    date_reservation = models.DateField()
    heure_reservation =  models.TimeField()
    status_reservation = models.CharField(max_length=20, choices=STATUS_CHOICES)
    client = models.ForeignKey(Client,on_delete=models.CASCADE,null=False)
    prestataire = models.ForeignKey(Prestataire,on_delete=models.CASCADE,null=False)

    def __str__(self) -> str:
        return self.status_reservation


class Avis(models.Model):

    note = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    commentaire = models.CharField(max_length=1000,null=False)
    client = models.ForeignKey(Client,on_delete=models.CASCADE,null=False)
    prestataire = models.ForeignKey(Prestataire,on_delete=models.CASCADE,null=False)
    


class AdressePrestataire(models.Model):

    commune = models.CharField(max_length=50, null=False)
    cite = models.CharField(max_length=50, null=True)
    numero_residence = models.CharField(max_length=30, null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    ville = models.CharField(max_length=50, null=False)
    quartier = models.CharField(max_length=50, null=False)
    prestataire = models.ForeignKey(Prestataire,on_delete=models.CASCADE,null=False)



class OperateurPaiement(models.Model):
     
    nom_operateur = models.CharField(max_length=20, null=False)
    deep_link = models.CharField(max_length=100)


class Paiement(models.Model):
    STATUS_PAIEMENT = (
    ('canceled', _('Annulé')),
    ('paid', _('Payé')),
    )
    MODE_PAIEMENT = (
    ('cash', _('Espèces')),
    ('e_pay', _('Paiement Electronique')),
    )
    date_paiement = models.DateField()
    status_paiement = models.CharField(max_length=20, choices=STATUS_PAIEMENT)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT)
    operateur_paiement = models.ForeignKey(OperateurPaiement, on_delete=models.SET_NULL, null=True)
    reservation = models.OneToOneField(Reservation,on_delete=models.CASCADE,null=False)













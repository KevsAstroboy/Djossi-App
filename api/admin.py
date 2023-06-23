from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Client)
admin.site.register(Service)
admin.site.register(Prestataire)
admin.site.register(Reservation)
admin.site.register(Avis)
admin.site.register(AdressePrestataire)
admin.site.register(OperateurPaiement)
admin.site.register(Paiement)



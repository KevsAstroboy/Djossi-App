from rest_framework import serializers
from .models import Client, Prestataire, Service, Reservation, Avis, OperateurPaiement


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['id','nom_client','prenom_client','username','phone_number','commune','ville','numero_cni','password','photo_client']

class ClientLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['username','password']

class PrestataireRegisterSerializer(serializers.ModelSerializer):
    photo_prestataire = serializers.FileField(required=True)
    photo_piece_recto = serializers.FileField(required=True) 
    photo_piece_verso = serializers.FileField(required=True) 
    class Meta:
        model = Prestataire
        fields = ['id','nom_prestataire','prenom_prestataire','username','phone_number','numero_cni','password','photo_prestataire','photo_piece_recto','photo_piece_verso','services','biographie','date_naissance']
        depth = 1

class PrestataireLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prestataire
        fields = ['phone_number','password']
        depth = 1

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ['id','nom_service','description_service']
    

class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = '__all__'
        depth = 1

class AvisSerializer(serializers.ModelSerializer):

    client = ClientSerializer()

    class Meta:
        model = Avis
        fields = ['id','note','commentaire','client']

class OperateurPaiementSerializer(serializers.ModelSerializer):

        class Meta:
            model = OperateurPaiement
            fields = '__all__'

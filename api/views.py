from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import ClientSerializer,  PrestataireRegisterSerializer, ClientLoginSerializer, PrestataireLoginSerializer, ReservationSerializer, AvisSerializer, OperateurPaiementSerializer
from .models import Client, Service, Prestataire, AdressePrestataire, Reservation, Avis, OperateurPaiement, Paiement
from rest_framework import status
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.db.models import Max



class ClientRegisterView(APIView):

    serializer_class = ClientSerializer

    def post(self, request, *args, **kwargs):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()
            return Response({"hasError": False, "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"hasError": True, "data": "Veuillez bien renseigner tous les champs"}, status=status.HTTP_400_BAD_REQUEST)


class ClientLoginAPIView(APIView):

    serializer_class = ClientLoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Vérifier si le nom d'utilisateur et le mot de passe sont présents
        if not username or not password:
            return Response({"hasError": True,'data': 'Veuillez fournir le nom d\'utilisateur et le mot de passe.'}, status=status.HTTP_400_BAD_REQUEST)

        

        try:
            # Rechercher l'utilisateur dans votre modèle personnalisé
            user = Client.objects.get(username=username)
        except Client.DoesNotExist:
            # L'utilisateur n'existe pas
            return Response({"hasError": True,'data': 'Nom d\'utilisateur ou mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si le mot de passe est correct en utilisant la fonction check_password
        if not check_password(password, user.password):
            # Le mot de passe est incorrect
            return Response({"hasError": True,'data': 'Nom d\'utilisateur ou mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            
        # L'utilisateur est authentifié avec succès
        userJson  = {
                        'id': str(user.id),
                        'nom_client': str(user.nom_client),
                        'prenom_client': str(user.prenom_client),
                        'photo_client': str(user.photo_client),
                        'username': str(user.username),
                        'phone_number': str(user.phone_number),
                        'commune': str(user.commune),
                        'ville': str(user.ville),
                    }
        return Response({"hasError": False,'data': userJson}, status=status.HTTP_200_OK)


class PrestataireRegisterView(APIView):

    serializer_class = PrestataireRegisterSerializer


    def get_queryset(self):
            prestataires = Prestataire.objects.all()
            return prestataires    


    def get(self, request, *args , **kwargs ):
                prestataires = self.get_queryset()
                serializer = PrestataireRegisterSerializer(prestataires,many=True)
                return Response(serializer.data) 
        

    def post(self, request, *args, **kwargs):
        services_data = request.data.get('services', [])
        ville = request.data.get('ville')
        commune = request.data.get('commune')
        quartier = request.data.get('quartier')
        if not services_data:
            return Response({"hasError": True, 'data': 'Vous n\'avez pas sélectionné de service'}, status=status.HTTP_400_BAD_REQUEST)

        if not ville or not commune or not quartier:
            return Response({"hasError": True,'data': 'Veuillez bien renseigner les champs concernant vos coordonnées géographique.'}, status=status.HTTP_400_BAD_REQUEST)
        # Vérification des services
        service_ids = []
        services_instances = []
        for service_id in services_data:
            try:
                service = Service.objects.get(id=service_id)
                service_ids.append(service.id)
            except Service.DoesNotExist:
                return Response({"hasError": True, 'data': 'Ce service n\'existe pas '}, status=status.HTTP_400_BAD_REQUEST)
        
        # Modification des services dans la copie mutable de request.data
        mutable_data = request.data.copy()
        mutable_data['services'] = service_ids

        serializer = PrestataireRegisterSerializer(data=mutable_data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()
            serializer.instance.is_active = False
            serializer.save()
            adresse_prestataire = AdressePrestataire(commune=commune, quartier=quartier, ville=ville, cite=request.data.get('cite'), numero_residence=request.data.get('numero_residence'), prestataire= Prestataire.objects.get(id=serializer.instance.id))
            adresse_prestataire.save()
            for service_id in service_ids:
                service = Service.objects.get(id=service_id)
                services_instances.append(service)
            serializer.validated_data['services'] = services_instances
            serializer.save()
            return Response({"hasError": False, "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"hasError": True, "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
class PrestataireLoginView(APIView):

    serializer_class = PrestataireLoginSerializer
    
    def post(self, request, *args, **kwargs):
        
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        # Vérifier si le numéro de téléphone et le mot de passe sont présents
        if not phone_number or not password:
            return Response({"hasError": True, 'data': 'Veuillez fournir un numéro de téléphone et un mot de passe.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Rechercher le prestataire dans votre modèle personnalisé
            prestataire = Prestataire.objects.get(phone_number=phone_number)
        except Prestataire.DoesNotExist:
            # Le prestataire n'existe pas
            return Response({"hasError": True, 'data': 'Numéro de téléphone ou mot de passe incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)
        
       
        # Vérifier si le mot de passe est correct en utilisant la fonction check_password
        if not check_password(password, prestataire.password):
            # Le mot de passe est incorrect
            return Response({"hasError": True, 'data': 'Numéro de téléphone ou mot de passe incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not prestataire.is_active:
            return Response({"hasError": True, 'data': 'Votre compte est inactif. Veuillez patienter pour la vérification.'}, status=status.HTTP_401_UNAUTHORIZED)

        adresses = prestataire.adresseprestataire_set.all()

        adresses_list = []
        for adresse in adresses:
            adresse_data = {
                'id': str(adresse.id),
                'commune': str(adresse.commune),
                'ville': str(adresse.ville),
                'quartier': str(adresse.quartier),
                'numero_residence': str(adresse.numero_residence),
                'longitude': str(adresse.longitude),
                'latitude': str(adresse.latitude)
            }
            adresses_list.append(adresse_data)
            
            # # Faire quelque chose avec les valeurs des champs
            # print(commune, quartier, ville, numero_residence)

        userJson = {
            'id': str(prestataire.id),
            'nom_prestataire': str(prestataire.nom_prestataire),
            'prenom_prestataire': str(prestataire.prenom_prestataire),
            'biographie': str(prestataire.biographie),
            'photo_prestataire': str(prestataire.photo_prestataire),
            'adresses': adresses_list,
            'phone_number': str(prestataire.phone_number),
        }

        return Response({"hasError": False, 'data': userJson}, status=status.HTTP_200_OK)



class UpdatePrestatairePhoneNumberView(APIView):
    def put(self, request, prest_id):
        try:
            prestataire = Prestataire.objects.get(id=prest_id)
        except Prestataire.DoesNotExist:
            return Response({"hasError": True, "message": "Prestataire not found."}, status=status.HTTP_404_NOT_FOUND)

        old_phone_number = request.data.get("old_phone_number")
        new_phone_number = request.data.get("new_phone_number")

        if not old_phone_number or not new_phone_number:
            return Response({"hasError": True, "message": "Old and new phone numbers are required."}, status=status.HTTP_400_BAD_REQUEST)

        if prestataire.phone_number != old_phone_number:
            return Response({"hasError": True, "message": "Invalid old phone number."}, status=status.HTTP_400_BAD_REQUEST)

        if Prestataire.objects.exclude(id=prest_id).filter(phone_number=new_phone_number).exists():
            return Response({"hasError": True, "message": "Phone number already exists for another Prestataire."}, status=status.HTTP_400_BAD_REQUEST)

        prestataire.phone_number = new_phone_number
        prestataire.save()

        return Response({"hasError": False, "message": "Phone number updated successfully."}, status=status.HTTP_200_OK)


class ReservationView(APIView):

        serializer_class = ReservationSerializer
        def get(self, request, user_id, prest_id):

            if not user_id or not prest_id:
                return Response({"hasError": True, 'data': 'Impossible de faire une demande de service.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
              client = Client.objects.get(id=user_id)

            except Client.DoesNotExist:
                return Response({"hasError": True, 'data': 'Utilisateur ou prestataire n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
              prestataire = Prestataire.objects.get(id=prest_id)
              if  prestataire.is_active == False:
                return Response({"hasError": True, 'data': 'Prestataire n\'est pas encore verifié.'}, status=status.HTTP_400_BAD_REQUEST)

            except Prestataire.DoesNotExist:
                return Response({"hasError": True, 'data': 'Utilisateur ou prestataire n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

            date_actuelle = datetime.now().date()
            heure_actuelle = datetime.now().time()
            status_reservation = 'requested'

            reservation = Reservation(date_reservation = date_actuelle, heure_reservation = heure_actuelle, status_reservation = status_reservation, client = client, prestataire = prestataire)
            reservation.save()

            reservation_json = {
                'id':str(reservation.id),
                'client':{
                    'id': str(reservation.client.id),
                    'nom_client': str(reservation.client.nom_client),
                    'prenom_client': str(reservation.client.prenom_client)
                },
                'prestataire':{
                    'id': str(reservation.prestataire.id),
                    'phone_number': str(reservation.prestataire.phone_number),
                    'nom_prestataire': str(reservation.prestataire.nom_prestataire),
                    'prenom_prestataire': str(reservation.prestataire.prenom_prestataire)
                },
                'date_reservation': str(reservation.date_reservation),
                'heure_reservation': str(reservation.heure_reservation),
                'status_reservation': str(reservation.get_status_reservation_display()),

            }
            return Response({"hasError": False, 'data': reservation_json}, status=status.HTTP_200_OK)


class ReservationGetByPrestataireView(APIView):

    serializer_class = ReservationSerializer

    def get(self, request, prest_id):

        if not  prest_id:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        try:

            prestataire = Prestataire.objects.get(id=prest_id)
        except Prestataire.DoesNotExist:
                return Response({"hasError": True, 'data': 'Prestataire n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)
        reservations = Reservation.objects.filter(prestataire=prestataire)
        reservations_list = []
        for reservation in reservations:
            reservation_data = {
                'id': str(reservation.id),
                'date_reservation': str(reservation.date_reservation),
                'heure_reservation': str(reservation.heure_reservation),
                'status_reservation': str(reservation.get_status_reservation_display()),
                'client': {
                    'id': str(reservation.client.id),
                    'nom_client': str(reservation.client.nom_client),
                    'prenom_client': str(reservation.client.prenom_client),
                    'photo_client': str(reservation.client.photo_client)

                },
            }
            reservations_list.append(reservation_data)
        return Response({"hasError": False, 'data': reservations_list}, status=status.HTTP_200_OK)


# class ReservationGetByUserView(APIView):

#         serializer_class = ReservationSerializer
          


#         def get(self, request, user_id):

#             if not user_id:
#                 return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#               client = Client.objects.get(id=user_id)

#             except Client.DoesNotExist:
#                 return Response({"hasError": True, 'data': 'Utilisateur n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)


#             reservations = Reservation.objects.filter(client=client)
#             reservations_list = []
#             for reservation in reservations:
#                 try:
#                     status_paiement = Paiement.objects.get(reservation=reservation).status_paiement.get_status_paiement_display()
#                 except Paiement.DoesNotExist:
#                     status_paiement = 'Annulé'
#                 reservation_data = {
#                     'id': str(reservation.id),
#                     'status_reservation': str(reservation.get_status_reservation_display()),
#                     'status_paiement': str(status_paiement),
#                     'prestataire':{
#                         'id': str(reservation.prestataire.id),
#                         'nom_prestataire': str(reservation.prestataire.nom_prestataire),
#                         'prenom_prestataire': str(reservation.prestataire.prenom_prestataire),
#                         'photo_prestataire': str(reservation.prestataire.photo_prestataire)
#                     },
#                 }
#                 reservations_list.append(reservation_data)
#             return Response({"hasError": False, 'data': reservations_list}, status=status.HTTP_200_OK)


class ReservationGetByUserView(APIView):
    serializer_class = ReservationSerializer

    def get(self, request, user_id):
        if not user_id:
            return Response({"hasError": True, 'data': 'Requête échouée.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(id=user_id)
        except Client.DoesNotExist:
            return Response({"hasError": True, 'data': "L'utilisateur n'existe pas."}, status=status.HTTP_400_BAD_REQUEST)

        reservations = Reservation.objects.filter(client=client).order_by('-date_reservation')

        reservations_list = []
        for reservation in reservations:
            try:
                status_paiement = Paiement.objects.get(reservation=reservation).status_paiement
                # print(status_paiement)
            except Paiement.DoesNotExist:
                status_paiement = 'Annulé'

            reservation_data = {
                'id': str(reservation.id),
                'status_reservation': str(reservation.get_status_reservation_display()),
                'status_paiement': str(status_paiement),
                'prestataire': {
                    'id': str(reservation.prestataire.id),
                    'nom_prestataire': str(reservation.prestataire.nom_prestataire),
                    'prenom_prestataire': str(reservation.prestataire.prenom_prestataire),
                    'photo_prestataire': str(reservation.prestataire.photo_prestataire)
                },
            }
            reservations_list.append(reservation_data)

        return Response({"hasError": False, 'data': reservations_list}, status=status.HTTP_200_OK)




class ReservationAcceptedView(APIView):

    def get(self, request, reservation_id):

        if not reservation_id:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
              reservation = Reservation.objects.get(id=reservation_id)

        except Reservation.DoesNotExist:
                return Response({"hasError": True, 'data': 'Réservation n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)
        

        reservation.status_reservation = 'in_progress'
        reservation.save()

        return Response({"hasError": False, 'data': 'La demande de service a été accepté.'}, status=status.HTTP_200_OK)

    def post(self, request, reservation_id):

        if not reservation_id:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
              reservation = Reservation.objects.get(id=reservation_id)

        except Reservation.DoesNotExist:
                return Response({"hasError": True, 'data': 'Réservation n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

        reservation.status_reservation = 'canceled'
        reservation.save()

        return Response({"hasError": False, 'data': 'La demande de service a été annulé.'}, status=status.HTTP_200_OK)

class ReservationFinishedView(APIView):

    def get(self, request, reservation_id):

        if not reservation_id:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
              reservation = Reservation.objects.get(id=reservation_id)

        except Reservation.DoesNotExist:
                return Response({"hasError": True, 'data': 'Réservation n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)
        if not reservation.get_status_reservation_display() == 'En cours':
                return Response({"hasError": True, 'data': 'La reservation n\'a pas été accepté.'}, status=status.HTTP_400_BAD_REQUEST)
        reservation.status_reservation = 'finished'
        reservation.save()

        return Response({"hasError": False, 'data': 'La prestation de service est terminé.'}, status=status.HTTP_200_OK)

class AvisView(APIView):

    serializer_class = AvisSerializer

    def post(self, request, user_id, prest_id):
        
        if not user_id or not prest_id:
                return Response({"hasError": True, 'data': 'Impossible de donner un avis.'}, status=status.HTTP_400_BAD_REQUEST)
        note = request.data.get('note')
        commentaire = request.data.get('commentaire')
        if not note and not commentaire:
                return Response({"hasError": True, 'data': 'Veuillez renseigner l\'un des champs.'}, status=status.HTTP_400_BAD_REQUEST)
        if int(note) < 0 or int(note) > 5:
            return Response({"hasError": True, 'data': 'La valeur de la note n\'est pas prise en compte.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            client = Client.objects.get(id=user_id)

        except Client.DoesNotExist:
            return Response({"hasError": True, 'data': 'Utilisateur ou prestataire n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prestataire = Prestataire.objects.get(id=prest_id)
            if  prestataire.is_active == False:
                return Response({"hasError": True, 'data': 'Prestataire n\'est pas encore verifié.'}, status=status.HTTP_400_BAD_REQUEST)
        except Prestataire.DoesNotExist:
            return Response({"hasError": True, 'data': 'Utilisateur ou prestataire n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

        avis = Avis(note=note, commentaire=commentaire, client=client, prestataire=prestataire)
        avis.save()
        return Response({"hasError": False, 'data': 'Vos avis ont bien été envoyé.'}, status=status.HTTP_200_OK)

    def get(self, request, prest_id):

        if not prest_id:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            prestataire = Prestataire.objects.get(id=prest_id)
        except Prestataire.DoesNotExist:
                return Response({"hasError": True, 'data': 'Prestataire n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)
        avis = Avis.objects.filter(prestataire=prestataire)
        if avis.exists():
            avis_list = []
            for avi in avis:
                    avis_data = {
                        'id': str(avi.id),
                        'note': str(avi.note),
                        'commentaire': str(avi.commentaire),
                        'client':{
                            'id': str(avi.client.id),
                            'prenom_client': str(avi.client.prenom_client),
                            'photo_client': str(avi.client.photo_client)
                        },
                    }
                    avis_list.append(avis_data)
            return Response({"hasError": False, 'data': avis_list}, status=status.HTTP_200_OK)

        else:
            # Le prestataire n'a pas d'avis
            return Response({"hasError": True, 'data': 'Ce prestataire n\'a pas d\'avis.'}, status=status.HTTP_400_BAD_REQUEST)
    
class PaiementView(APIView):

        def get(self, request, reservation_id, operateur_id=None):

            if not reservation_id:
                return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
              reservation = Reservation.objects.get(id=reservation_id)
            except Reservation.DoesNotExist:
                return Response({"hasError": True, 'data': 'Réservation n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)
            if not reservation.get_status_reservation_display() == 'Terminé':
                return Response({"hasError": True, 'data': 'La prestation n\'est pas encore terminée.'}, status=status.HTTP_400_BAD_REQUEST)
            date_paiement = datetime.now().date()
            status_paiement = 'paid'
            if operateur_id:
              try:
                mode_paiement = 'e_pay'
                operateur_paiement = OperateurPaiement.objects.get(id=operateur_id)
                paiement = Paiement(date_paiement=date_paiement, status_paiement=status_paiement,mode_paiement=mode_paiement,operateur_paiement=operateur_paiement,reservation=reservation)
                paiement.save()
                return Response({"hasError": False, 'data': 'Votre paiement a été effectué avec succès'}, status=status.HTTP_200_OK)
              except OperateurPaiement.DoesNotExist:
                return Response({"hasError": True, 'data': 'Cet opérateur n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)
            mode_paiement = 'cash'
            paiement = Paiement(date_paiement=date_paiement, status_paiement=status_paiement,mode_paiement=mode_paiement,reservation=reservation) 
            paiement.save()
            return Response({"hasError": False, 'data': 'Votre paiement a été effectué avec succès'}, status=status.HTTP_200_OK)
            

          
class OperateurPaiementView(APIView):

    serializer_class = OperateurPaiementSerializer


    def get_queryset(self):
            operateurs_paiement = OperateurPaiement.objects.all()
            return operateurs_paiement    


    def get(self, request, *args , **kwargs ):
                operateurs_paiement = self.get_queryset()
                serializer = OperateurPaiementSerializer(operateurs_paiement,many=True)
                return Response(serializer.data)              
        
        
class GetPrestataireByUserDetailsForMecanicianView(APIView):

    def get(self, request, commune, ville, optional=None):
        if not commune or not ville:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not optional:
            adresses_list = AdressePrestataire.objects.filter(prestataire__services=1, commune__iexact=commune, ville__iexact=ville)
        else:
            adresses_list = AdressePrestataire.objects.filter( Q(quartier__icontains=optional) | Q(numero_residence__icontains=optional) | Q(cite__icontains=optional) ,prestataire__services=1, commune__iexact=commune, ville__iexact=ville)

        if not adresses_list:
            return Response({"hasError": True, 'data': "Aucun mécanicien n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            prestataires = []
            for adresse in adresses_list:
                if adresse.prestataire.is_active == True:
                    avis_list = Avis.objects.filter(prestataire=adresse.prestataire)
                    note = 0
                    for avis in avis_list:
                        note += avis.note
                    nombre_avis = len(avis_list)
                    moyenne_note = note / len(avis_list) if len(avis_list) > 0 else 0
        
                    prestataire_data = {
                        'id': str(adresse.prestataire.id),
                        'nom_prestataire': str(adresse.prestataire.nom_prestataire),
                        'prenom_prestataire': str(adresse.prestataire.prenom_prestataire),
                        'service': 'Mécanicien',
                        'photo_prestataire': str(adresse.prestataire.photo_prestataire),
                        'biographie': str(adresse.prestataire.biographie),
                        'phone_number': str(adresse.prestataire.phone_number),
                        'moyenne_note': moyenne_note,
                        'avis': nombre_avis
                    }
                    prestataires.append(prestataire_data)

            if not prestataires:
                return Response({"hasError": True, 'data': "Aucun mécanicien n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)

            prestataires.sort(key=lambda x: x['moyenne_note'], reverse=True)

            return Response({"hasError": False, 'data': prestataires}, status=status.HTTP_200_OK)
                    


class GetPrestataireByUserDetailsForElectricianView(APIView):

    def get(self, request, commune, ville, optional=None):
        if not commune or not ville:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not optional:
            adresses_list = AdressePrestataire.objects.filter(prestataire__services=2, commune__iexact=commune, ville__iexact=ville)
        else:
            adresses_list = AdressePrestataire.objects.filter( Q(quartier__icontains=optional) | Q(numero_residence__icontains=optional) | Q(cite__icontains=optional) ,prestataire__services=1, commune__iexact=commune, ville__iexact=ville)

        if not adresses_list:
            return Response({"hasError": False, 'data': "Aucun élecricien n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            prestataires = []
            for adresse in adresses_list:
                if adresse.prestataire.is_active == True:
                    avis_list = Avis.objects.filter(prestataire=adresse.prestataire)
                    note = 0
                    for avis in avis_list:
                        note += avis.note
                    nombre_avis = len(avis_list)
                    moyenne_note = note / len(avis_list) if len(avis_list) > 0 else 0
        
                    prestataire_data = {
                        'id': str(adresse.prestataire.id),
                        'nom_prestataire': str(adresse.prestataire.nom_prestataire),
                        'prenom_prestataire': str(adresse.prestataire.prenom_prestataire),
                        'service': 'Électricien',
                        'photo_prestataire': str(adresse.prestataire.photo_prestataire),
                        'biographie': str(adresse.prestataire.biographie),
                        'phone_number': str(adresse.prestataire.phone_number),
                        'moyenne_note': moyenne_note,
                        'avis': nombre_avis
                    }
                    prestataires.append(prestataire_data)

            if not prestataires:
                return Response({"hasError": False, 'data': "Aucun élecricien n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)

            prestataires.sort(key=lambda x: x['moyenne_note'], reverse=True)

            return Response({"hasError": False, 'data': prestataires}, status=status.HTTP_200_OK)
            
class GetPrestataireByUserDetailsForPlombingView(APIView):

    def get(self, request, commune, ville, optional=None):
        if not commune or not ville:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not optional:
            adresses_list = AdressePrestataire.objects.filter(prestataire__services=3, commune__iexact=commune, ville__iexact=ville)
        else:
            adresses_list = AdressePrestataire.objects.filter( Q(quartier__icontains=optional) | Q(numero_residence__icontains=optional) | Q(cite__icontains=optional) ,prestataire__services=1, commune__iexact=commune, ville__iexact=ville)

        if not adresses_list:
            return Response({"hasError": False, 'data': "Aucun plombier n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            prestataires = []
            for adresse in adresses_list:
                if adresse.prestataire.is_active == True:
                    avis_list = Avis.objects.filter(prestataire=adresse.prestataire)
                    note = 0
                    for avis in avis_list:
                        note += avis.note
                    nombre_avis = len(avis_list)
                    moyenne_note = note / len(avis_list) if len(avis_list) > 0 else 0
        
                    prestataire_data = {
                        'id': str(adresse.prestataire.id),
                        'nom_prestataire': str(adresse.prestataire.nom_prestataire),
                        'prenom_prestataire': str(adresse.prestataire.prenom_prestataire),
                        'service': 'Plomberie',
                        'photo_prestataire': str(adresse.prestataire.photo_prestataire),
                        'biographie': str(adresse.prestataire.biographie),
                        'phone_number': str(adresse.prestataire.phone_number),
                        'moyenne_note': moyenne_note,
                        'avis': nombre_avis
                    }
                    prestataires.append(prestataire_data)

            if not prestataires:
                return Response({"hasError": False, 'data': "Aucun plombier n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)

            prestataires.sort(key=lambda x: x['moyenne_note'], reverse=True)

            return Response({"hasError": False, 'data': prestataires}, status=status.HTTP_200_OK)

class GetPrestataireByUserDetailsForMakeUpView(APIView):

    def get(self, request, commune, ville, optional=None):
        if not commune or not ville:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not optional:
            adresses_list = AdressePrestataire.objects.filter(prestataire__services=4, commune__iexact=commune, ville__iexact=ville)
        else:
            adresses_list = AdressePrestataire.objects.filter( Q(quartier__icontains=optional) | Q(numero_residence__icontains=optional) | Q(cite__icontains=optional) ,prestataire__services=1, commune__iexact=commune, ville__iexact=ville)

        if not adresses_list:
            return Response({"hasError": False, 'data': "Aucun(e) maquilleuses(eurs)) n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            prestataires = []
            for adresse in adresses_list:
                if adresse.prestataire.is_active == True:
                    avis_list = Avis.objects.filter(prestataire=adresse.prestataire)
                    note = 0
                    for avis in avis_list:
                        note += avis.note
                    nombre_avis = len(avis_list)
                    moyenne_note = note / len(avis_list) if len(avis_list) > 0 else 0
        
                    prestataire_data = {
                        'id': str(adresse.prestataire.id),
                        'nom_prestataire': str(adresse.prestataire.nom_prestataire),
                        'prenom_prestataire': str(adresse.prestataire.prenom_prestataire),
                        'service': 'Maquilleuse',
                        'photo_prestataire': str(adresse.prestataire.photo_prestataire),
                        'biographie': str(adresse.prestataire.biographie),
                        'phone_number': str(adresse.prestataire.phone_number),
                        'moyenne_note': moyenne_note,
                        'avis': nombre_avis
                    }
                    prestataires.append(prestataire_data)

            if not prestataires:
                return Response({"hasError": False, 'data': "Aucun(e) maquilleuses(eurs)) n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)

            prestataires.sort(key=lambda x: x['moyenne_note'], reverse=True)

            return Response({"hasError": False, 'data': prestataires}, status=status.HTTP_200_OK)


class GetPrestataireByUserDetailsForHairDresserView(APIView):

    def get(self, request, commune, ville, optional=None):
        if not commune or not ville:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not optional:
            adresses_list = AdressePrestataire.objects.filter(prestataire__services=5, commune__iexact=commune, ville__iexact=ville)
        else:
            adresses_list = AdressePrestataire.objects.filter( Q(quartier__icontains=optional) | Q(numero_residence__icontains=optional) | Q(cite__icontains=optional) ,prestataire__services=1, commune__iexact=commune, ville__iexact=ville)

        if not adresses_list:
            return Response({"hasError": False, 'data': "Aucun coiffeur n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            prestataires = []
            for adresse in adresses_list:
                if adresse.prestataire.is_active == True:
                    avis_list = Avis.objects.filter(prestataire=adresse.prestataire)
                    note = 0
                    for avis in avis_list:
                        note += avis.note
                    nombre_avis = len(avis_list)
                    moyenne_note = note / len(avis_list) if len(avis_list) > 0 else 0
        
                    prestataire_data = {
                        'id': str(adresse.prestataire.id),
                        'nom_prestataire': str(adresse.prestataire.nom_prestataire),
                        'prenom_prestataire': str(adresse.prestataire.prenom_prestataire),
                        'service': 'Coiffeur',
                        'photo_prestataire': str(adresse.prestataire.photo_prestataire),
                        'biographie': str(adresse.prestataire.biographie),
                        'phone_number': str(adresse.prestataire.phone_number),
                        'moyenne_note': moyenne_note,
                        'avis': nombre_avis
                    }
                    prestataires.append(prestataire_data)

            if not prestataires:
                return Response({"hasError": False, 'data': "Aucun coiffeur n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)

            prestataires.sort(key=lambda x: x['moyenne_note'], reverse=True)

            return Response({"hasError": False, 'data': prestataires}, status=status.HTTP_200_OK)


class GetPrestataireByUserDetailsForFanicoView(APIView):

    def get(self, request, commune, ville, optional=None):
        if not commune or not ville:
            return Response({"hasError": True, 'data': 'Réquête echouée.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not optional:
            adresses_list = AdressePrestataire.objects.filter(prestataire__services=6, commune__iexact=commune, ville__iexact=ville)
        else:
            adresses_list = AdressePrestataire.objects.filter( Q(quartier__icontains=optional) | Q(numero_residence__icontains=optional) | Q(cite__icontains=optional) ,prestataire__services=1, commune__iexact=commune, ville__iexact=ville)

        if not adresses_list:
            return Response({"hasError": False, 'data': "Aucun fanico n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            prestataires = []
            for adresse in adresses_list:
                if adresse.prestataire.is_active == True:
                    avis_list = Avis.objects.filter(prestataire=adresse.prestataire)
                    note = 0
                    for avis in avis_list:
                        note += avis.note
                    nombre_avis = len(avis_list)
                    moyenne_note = note / len(avis_list) if len(avis_list) > 0 else 0
        
                    prestataire_data = {
                        'id': str(adresse.prestataire.id),
                        'nom_prestataire': str(adresse.prestataire.nom_prestataire),
                        'prenom_prestataire': str(adresse.prestataire.prenom_prestataire),
                        'service': 'Fanico',
                        'photo_prestataire': str(adresse.prestataire.photo_prestataire),
                        'biographie': str(adresse.prestataire.biographie),
                        'phone_number': str(adresse.prestataire.phone_number),
                        'moyenne_note': moyenne_note,
                        'avis': nombre_avis
                    }
                    prestataires.append(prestataire_data)

            if not prestataires:
                return Response({"hasError": False, 'data': "Aucun fanico n'a été trouvé dans votre zone."},
                            status=status.HTTP_400_BAD_REQUEST)

            prestataires.sort(key=lambda x: x['moyenne_note'], reverse=True)

            return Response({"hasError": False, 'data': prestataires}, status=status.HTTP_200_OK)


class CancelLastReservationView(APIView):
    def put(self, request, user_id, prestataire_id):
        try:
            # Recherche de la dernière réservation de l'utilisateur avec le prestataire donné
            reservation = Reservation.objects.filter(client__id=user_id, prestataire__id=prestataire_id).latest('id')

            # Vérification si la réservation est déjà annulée
            if reservation.status_reservation == 'canceled':
                return Response({"message": "La réservation est déjà annulée."}, status=status.HTTP_200_OK)

            # Mise à jour du statut de la réservation en "canceled"
            reservation.status_reservation = 'canceled'
            reservation.save()

            return Response({"message": "La réservation a été annulée avec succès."}, status=status.HTTP_200_OK)

        except Reservation.DoesNotExist:
            return Response({"message": "Aucune réservation trouvée pour cet utilisateur et prestataire."}, status=status.HTTP_404_NOT_FOUND)


class CheckLastReservationStatusView(APIView):
    
    def get(self, request, user_id, prestataire_id):
        try:
            # Recherche de la dernière réservation de l'utilisateur avec le prestataire donné
            reservation = Reservation.objects.filter(client__id=user_id, prestataire__id=prestataire_id).latest('id')

            # Vérification du statut de la réservation
            if reservation.status_reservation != 'in_progress':
                return Response({"message": "Le statut de la réservation n'est pas 'in_progress'."}, status=status.HTTP_400_BAD_REQUEST)

            # Le statut est 'in_progress'
            return Response({"message": "Le statut de la réservation est 'in_progress'."}, status=status.HTTP_200_OK)

        except Reservation.DoesNotExist:
            return Response({"message": "Aucune réservation trouvée pour cet utilisateur et prestataire."}, status=status.HTTP_404_NOT_FOUND)
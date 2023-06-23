from django.urls import re_path

from .views import (
ClientRegisterView,
ClientLoginAPIView,
PrestataireRegisterView,
PrestataireLoginView,
ReservationView,
ReservationGetByPrestataireView,
ReservationGetByUserView,
ReservationAcceptedView,
ReservationFinishedView,
AvisView,
PaiementView,
OperateurPaiementView,
GetPrestataireByUserDetailsForMecanicianView,
GetPrestataireByUserDetailsForElectricianView,
GetPrestataireByUserDetailsForPlombingView,
GetPrestataireByUserDetailsForHairDresserView,
GetPrestataireByUserDetailsForFanicoView,
GetPrestataireByUserDetailsForMakeUpView,
UpdatePrestatairePhoneNumberView,
CancelLastReservationView,
CheckLastReservationStatusView
)




urlpatterns = [
    re_path(r'register/', ClientRegisterView.as_view()),
    re_path(r'login/', ClientLoginAPIView.as_view()),
    re_path(r'prestataire/', PrestataireRegisterView.as_view()),
    re_path(r'login-p/', PrestataireLoginView.as_view()),
    re_path(r'update-number/(?P<prest_id>\d+)/$', UpdatePrestatairePhoneNumberView.as_view()),
    re_path(r'canceled-user-reservation/(?P<user_id>\d+)/(?P<prestataire_id>\d+)/$', CancelLastReservationView.as_view()),
    re_path(r'check-last-reservation/(?P<user_id>\d+)/(?P<prestataire_id>\d+)/$', CheckLastReservationStatusView.as_view()),
    re_path(r'reservation/(?P<user_id>\d+)/(?P<prest_id>\d+)/$', ReservationView.as_view()),
    re_path(r'reservation/(?P<prest_id>\d+)/$', ReservationGetByPrestataireView.as_view()),
    re_path(r'reservation-user/(?P<user_id>\d+)/$', ReservationGetByUserView.as_view()),
    re_path(r'reservation-accepted/(?P<reservation_id>\d+)/$', ReservationAcceptedView.as_view()),
    re_path(r'reservation-canceled/(?P<reservation_id>\d+)/$', ReservationAcceptedView.as_view()),
    re_path(r'reservation-finished/(?P<reservation_id>\d+)/$', ReservationFinishedView.as_view()),
    re_path(r'avis/(?P<user_id>\d+)/(?P<prest_id>\d+)/$', AvisView.as_view()),
    re_path(r'avis/(?P<prest_id>\d+)/$', AvisView.as_view()),
    re_path(r'paiement/(?P<reservation_id>\d+)/$', PaiementView.as_view()),
    re_path(r'paiement/(?P<reservation_id>\d+)/(?P<operateur_id>\d+)/$', PaiementView.as_view()),
    re_path(r'operateur-paiement/', OperateurPaiementView.as_view()),
    re_path(r'mecanicien-user/(?P<commune>\w+)/(?P<ville>\w+)/$', GetPrestataireByUserDetailsForMecanicianView.as_view()),
    re_path(r'mecanicien-user/(?P<commune>\w+)/(?P<ville>\w+)/(?P<optional>.*?)/$', GetPrestataireByUserDetailsForMecanicianView.as_view()),
    re_path(r'electricien-user/(?P<commune>\w+)/(?P<ville>\w+)/$', GetPrestataireByUserDetailsForElectricianView.as_view()),
    re_path(r'electricien-user/(?P<commune>\w+)/(?P<ville>\w+)/(?P<optional>.*?)/$', GetPrestataireByUserDetailsForElectricianView.as_view()),
    re_path(r'plombier-user/(?P<commune>\w+)/(?P<ville>\w+)/$', GetPrestataireByUserDetailsForPlombingView.as_view()),
    re_path(r'plombier-user/(?P<commune>\w+)/(?P<ville>\w+)/(?P<optional>.*?)/$', GetPrestataireByUserDetailsForPlombingView.as_view()),
    re_path(r'coiffeur-user/(?P<commune>\w+)/(?P<ville>\w+)/$', GetPrestataireByUserDetailsForHairDresserView.as_view()),
    re_path(r'coiffeur-user/(?P<commune>\w+)/(?P<ville>\w+)/(?P<optional>.*?)/$', GetPrestataireByUserDetailsForHairDresserView.as_view()),
    re_path(r'fanico-user/(?P<commune>\w+)/(?P<ville>\w+)/$', GetPrestataireByUserDetailsForFanicoView.as_view()),
    re_path(r'fanico-user/(?P<commune>\w+)/(?P<ville>\w+)/(?P<optional>.*?)/$', GetPrestataireByUserDetailsForFanicoView.as_view()),
    re_path(r'makeup-user/(?P<commune>\w+)/(?P<ville>\w+)/$', GetPrestataireByUserDetailsForMakeUpView.as_view()),
    re_path(r'makeup-user/(?P<commune>\w+)/(?P<ville>\w+)/(?P<optional>.*?)/$', GetPrestataireByUserDetailsForMakeUpView.as_view()),


]
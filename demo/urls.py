from django.urls import path
from . import views

urlpatterns = [
    path('', views.handle_twilio_voice_webhook),
    path('twilio-voice-webhook/<str:agent_id_path>/', views.handle_twilio_voice_webhook),
    path('initiate-call/', views.initiate_call, name='initiate_call'),
    path('csrf-token/', views.csrf_token_view, name='csrf-token'),
]

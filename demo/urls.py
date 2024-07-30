from django.urls import path
from . import views

urlpatterns = [
    path('twilio-voice-webhook/<str:agent_id_path>/', views.handle_twilio_voice_webhook),
    # WebSocket URL will be handled by Django Channels
]

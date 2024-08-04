from django.urls import path
from . import views

urlpatterns = [
    path('', views.demo_home, name='demo_home'),
    path('twilio-voice-webhook/<str:agent_id_path>/', views.handle_twilio_voice_webhook),
]

from django.urls import path
from . import views

urlpatterns = [
    path('twilio-voice-webhook/ee2ae22cd6ebaf5c245c77c6bdabfae9/', views.handle_twilio_voice_webhook),
    path('initiate-call/', views.initiate_call, name='initiate_call'),
    path('csrf-token/', views.csrf_token_view, name='csrf-token'),
    path('call-status-callback/', views.call_status_callback, name='call_status_callback'),
    path('create-agent/', views.CreateRetellAgentView.as_view(), name='create_agent'),
]
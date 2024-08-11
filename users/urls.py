from django.urls import path
from .views import RegisterView, LoginView, LogoutView, csrf_token_view

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('csrf-token/', csrf_token_view, name='csrf-token'),
]

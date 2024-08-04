from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('demo/', include('demo.urls')),
    path('', lambda request: redirect('demo/')),
]

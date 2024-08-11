from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/demo/', include('demo.urls')),  # Note the trailing slash
    path('', lambda request: redirect('api/demo/')),
]
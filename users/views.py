from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .serializers import UserSerializer, LoginSerializer

from rest_framework.views import APIView
from rest_framework import status
from django.middleware.csrf import get_token
from django.http import JsonResponse, HttpResponse
from rest_framework.authtoken.models import Token

from rest_framework.permissions import IsAuthenticated

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()
        
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        serializer = LoginSerializer(data={'username': username, 'password': password})
        if serializer.is_valid():
            # You can add additional checks or login logic here if needed
            return Response({'detail': 'Checked user details'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)

def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
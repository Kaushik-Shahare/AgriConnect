from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *

# Create your views here.
def get_tokens_for_user(user):
  refresh_token = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh_token),
      'access': str(refresh_token.access_token),
  }

class RegisterView(APIView):
    serializer_class = RegisterSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            token = get_tokens_for_user(serializer.instance)
            # token = get_tokens_for_user(user)['access']
            return Response({
                'user': serializer.data,
                'token': token,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)  
        
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # Ensure this import is present

from .models import FarmerProfile
from .serializers import FarmerProfileSerializer
from account.models import User

# Create your views here.

class ProfileView(APIView):
    serializer_class = FarmerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile = FarmerProfile.objects.get(user=request.user.id)
            serializer = self.serializer_class(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(id=request.user.id)
            profile = serializer.save(user=user)
            return Response(self.serializer_class(profile).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            profile = FarmerProfile.objects.get(user=request.user)
            serializer = self.serializer_class(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            profile = serializer.save()
            return Response(self.serializer_class(profile).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # def delete(self, request):
    #     try:
    #         profile = FarmerProfile.objects.get(user=request.user)
    #         profile.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
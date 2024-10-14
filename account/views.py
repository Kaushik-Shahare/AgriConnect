from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated  # Ensure this import is present
# from rest_framework.parsers import FormParser, MultiPartParser
from .serializers import *
import cloudinary
import cloudinary.uploader

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
        

class LoginView(APIView):
    serializer_class = LoginSerializer 
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.validated_data
            token = get_tokens_for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    # multi_part_parser = (FormParser, MultiPartParser)

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        # serializer = self.serializer_class(request.user, data=request.data, partial=True)
        # serializer.is_valid(raise_exception=True)

        # Handle Cloudinary upload if a new image is provided
        new_profile_image = request.FILES.get('new_profile_image')  
    
        if new_profile_image:
            # Store old profile image details for cleanup later
            old_profile_image_public_id = request.user.profile_image_public_id

            # Upload the new image to Cloudinary
            try:
                cloudinary_response = cloudinary.uploader.upload(new_profile_image)
                profile_image_url = cloudinary_response.get('secure_url')  
                profile_image_public_id = cloudinary_response.get('public_id')  

                # Save the URL and public ID to the user profile
                request.user.profile_image = profile_image_url
                request.user.profile_image_public_id = profile_image_public_id
                request.user.save()  

                # If the upload is successful, delete the old image from Cloudinary
                if old_profile_image_public_id:
                    cloudinary.uploader.destroy(old_profile_image_public_id)  
            
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = self.serializer_class(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
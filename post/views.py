from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import cloudinary.uploader
from .models import *
from .serializers import *

class PostView(APIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    # Fetch all posts or posts by a specific user
    def get(self, request, user_id=None, post_id=None):
    # Fetching a specific post by its ID
        if post_id:
            post = get_object_or_404(Post, id=post_id)
            serializer = self.serializer_class(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        # Fetching all posts or posts by a specific user
        if user_id is None:
            # Fetch all posts in descending order (latest to oldest)
            posts = Post.objects.all().order_by('-created_at')
        else:
            # Fetch posts by a specific user in descending order
            posts = Post.objects.filter(user_id=user_id).order_by('-created_at')
    
        serializer = self.serializer_class(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Create a new post
    def post(self, request):
        content = request.data.get("content")
        image = request.FILES.get("image")

        # Upload image to Cloudinary if it exists
        image_url = None
        image_public_id = None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get('url')
            image_public_id = upload_result.get('public_id')  # Get the public ID
            print("Uploaded image URL:", image_url)  # Print the URL for debugging

        post_data = {
            "content": content,
            "image_url": image_url,
            "image_public_id": image_public_id,  # Ensure this is set correctly
        }
    
        # Create the serializer with the request context
        serializer = self.serializer_class(data=post_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a post by ID
    # def put(self, request, post_id):
    #     post = get_object_or_404(Post, id=post_id, user=request.user)
    #     content = request.data.get("content", post.content)
    #     image = request.FILES.get("image")

    #     # Upload new image if one is provided
    #     if image:
    #         upload_result = cloudinary.uploader.upload(image)
    #         image_url = upload_result.get('url')
    #         image_public_id = upload_result.get('public_id')  # Get the new public ID
    #     else:
    #         image_url = post.image_url
    #         image_public_id = post.image_public_id  # Retain the existing public ID

    #     updated_data = {
    #         "content": content,
    #         "image_url": image_url,
    #         "image_public_id": image_public_id,  # Update with new or existing public ID
    #     }

    #     serializer = self.serializer_class(post, data=updated_data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a post by ID
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)

        # Delete the image from Cloudinary using the public ID
        if post.image_public_id:
            cloudinary.uploader.destroy(post.image_public_id)
        
        post.delete()
        return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        
class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        
        if post.likes.filter(id=user.id).exists():
            # Unlike the post if the user already liked it
            post.likes.remove(user)
            message = "Post unliked."
        else:
            # Like the post if the user hasn't already liked it
            post.likes.add(user)
            message = "Post liked."
        
        return Response({"detail": message}, status=status.HTTP_200_OK)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Add a comment
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        request.data['post'] = post.id
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a comment
    def put(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post, user=request.user)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a comment
    def delete(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post, user=request.user)
        
        comment.delete()
        return Response({"detail": "Comment deleted."}, status=status.HTTP_204_NO_CONTENT)
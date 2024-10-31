from django.urls import path
from .views import *

urlpatterns = [
    path('posts/', PostView.as_view()),  # Fetch all posts or create a new post
    path('posts/<int:user_id>/', PostView.as_view()),  # Fetch posts by user
    path('posts/detail/<int:post_id>/', PostView.as_view()),  # Fetch, update, or delete a specific post

    # Like/unlike a post
    path('posts/like/<int:post_id>/', LikePostView.as_view()),  

    # Comment-related views
    path('posts/comment/<int:post_id>/', CommentView.as_view()),  # Comment on a post
    path('posts/comment/<int:post_id>/<int:comment_id>/', CommentView.as_view()),  # Update or delete a comment

    # Like/unlike a comment
    path('posts/comment/like/<int:comment_id>/', LikeCommentView.as_view()),
]
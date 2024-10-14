from django.urls import path
from .views import PostView

urlpatterns = [
    # Fetch all posts or posts by user
    path('posts/', PostView.as_view()),  # Fetch all posts or create a new post
    path('posts/<int:user_id>/', PostView.as_view()),  # Fetch posts by user
    path('posts/detail/<int:post_id>/', PostView.as_view()),  # Fetch, update, or delete a specific post
]
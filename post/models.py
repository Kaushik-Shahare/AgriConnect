# models.py

from django.db import models
from django.conf import settings

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True, null=True)  
    image_public_id = models.CharField(max_length=255, blank=True, null=True)  



    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"
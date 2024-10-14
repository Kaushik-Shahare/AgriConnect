from django.db import models
from account.models import User
from crop.models import Crop

# Create your models here.


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmerprofile')
    farm_name = models.CharField(max_length=255, blank=True)
    farm_type = models.CharField(max_length=255, blank=True)  # e.g., Organic, Conventional
    crops_grown = models.ManyToManyField(Crop, blank=True, related_name='farmers') 
    farm_size = models.FloatField(blank=True, null=True)  # Size in acres or hectares
    experience_level = models.CharField(max_length=50, blank=True)  # e.g., Beginner, Intermediate, Expert
    # profile_picture = models.ImageField(upload_to='farmer_profiles/', null=True, blank=True)
    bio = models.TextField(blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.farm_name or self.user.email 
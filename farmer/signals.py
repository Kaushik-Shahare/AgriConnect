from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.conf import settings

from .models import FarmerProfile 


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
            FarmerProfile.objects.create(user=instance)
            # CrewProfile.objects.create(user=instance)
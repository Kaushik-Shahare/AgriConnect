from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email,  password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_new_user(self, email,  password=None, user_type=None, verified=True, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=email, user_type=user_type, verified=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


AUTH_PROVIDERS = {'email': 'email',
                #   'facebook': 'facebook',
                  'google': 'google'}

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [ 
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    ]
    email = models.EmailField(max_length=255,unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True, blank=False)  
    profile_image = models.URLField(blank=True, null=True)
    profile_image_public_id = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    verified = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))

    objects = UserManager() 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type', 'username']

    def get_full_name(self):
        return self.name or self.username  


    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

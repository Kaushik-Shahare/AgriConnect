from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('', AiAssistantView.as_view(), name='ai-assistant'),
]

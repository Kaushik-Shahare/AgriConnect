"""
URL configuration for AgriConnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

def server_running(request):
    return HttpResponse("Server is running")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/chats/', include('chats.urls')),
    path('api/farmer/', include('farmer.urls')),
    path('api/crop/', include('crop.urls')),
    path('api/post/', include('post.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/ai-assistant/', include('ai_assistant.urls')),
    path('', server_running),
]

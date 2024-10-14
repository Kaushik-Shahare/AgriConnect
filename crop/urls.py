from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('details/<int:pk>/', CropDetailsView.as_view(), name='crop-details'),
    path('list/', CropList.as_view(), name='crops-list'),
    path('list/<int:user_id>/', CropList.as_view(), name='crops-list'),
    path('farmer/crop/', CropCreate.as_view(), name='crop-create'),
    path('farmer/crop/add-quantity/<int:pk>/', AddCropQuantity.as_view(), name='crop-add'),
    path('farmer/crop/<int:pk>/', CropDetails.as_view(), name='crop-update'),

    path('dashboard/sales-analysis/<str:period>/', ProductSalesAnalysisView.as_view(), name='sales-analysis'),
    path('my-orders/', OrderedCrops.as_view(), name='orders'),
    path('buy/<int:pk>/', BuyCrop.as_view(), name='buy-crops'),
]

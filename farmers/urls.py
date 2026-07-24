from django.urls import path
from .views import (
    CropTypeListView,
    CollectionPointListView,
    ProduceListingListCreateView,
    ProduceListingDetailView,
    PhotoUploadView,
)

urlpatterns = [
    path('crops/', CropTypeListView.as_view(), name='crop-list'),
    path('collection-points/', CollectionPointListView.as_view(), name='collection-point-list'),
    path('listings/', ProduceListingListCreateView.as_view(), name='listing-list'),
    path('listings/<int:pk>/', ProduceListingDetailView.as_view(), name='listing-detail'),
    path('listings/<int:pk>/upload-photo/', PhotoUploadView.as_view(), name='listing-upload-photo'),
]

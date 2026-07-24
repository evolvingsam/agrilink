from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import CropType, CollectionPoint, ProduceListing
from .serializers import (
    CropTypeSerializer,
    CollectionPointSerializer,
    ProduceListingSerializer,
    PhotoUploadSerializer,
)
from .permissions import IsFarmerOwner


class CropTypeListView(generics.ListCreateAPIView):
    """
    GET  /api/produce/crops/         — List all crop types
    POST /api/produce/crops/         — Admin: add a new crop type
    """
    queryset = CropType.objects.all()
    serializer_class = CropTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CollectionPointListView(generics.ListCreateAPIView):
    """
    GET  /api/produce/collection-points/  — List collection points
    POST /api/produce/collection-points/  — Admin: add collection point
    """
    queryset = CollectionPoint.objects.all()
    serializer_class = CollectionPointSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'state', 'lga']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class ProduceListingListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/produce/listings/   — Browse all graded listings (buyers/dispatchers)
                                    OR the farmer's own listings if role==farmer
    POST /api/produce/listings/   — Farmer creates a new listing
    """
    serializer_class = ProduceListingSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['crop_type__name', 'collection_point__state']

    def get_queryset(self):
        user = self.request.user
        qs = ProduceListing.objects.select_related(
            'farmer', 'crop_type', 'collection_point'
        )
        if user.is_farmer:
            # Farmers only see their own listings
            return qs.filter(farmer=user)

        # Buyers / dispatchers see graded & above
        crop = self.request.query_params.get('crop')
        region = self.request.query_params.get('region')
        grade = self.request.query_params.get('grade')

        if crop:
            qs = qs.filter(crop_type__name__icontains=crop)
        if region:
            qs = qs.filter(collection_point__state__icontains=region)
        if grade:
            qs = qs.filter(quality_grade=grade)

        return qs.exclude(status__in=['pending', 'expired'])

    def get_permissions(self):
        return [permissions.IsAuthenticated()]


class ProduceListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/produce/listings/{id}/
    PUT    /api/produce/listings/{id}/  (farmer only, own listing)
    DELETE /api/produce/listings/{id}/  (farmer only, own listing)
    """
    serializer_class = ProduceListingSerializer

    def get_queryset(self):
        return ProduceListing.objects.select_related(
            'farmer', 'crop_type', 'collection_point'
        )

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsFarmerOwner()]
        return [permissions.IsAuthenticated()]


class PhotoUploadView(APIView):
    """
    POST /api/produce/listings/{id}/upload-photo/
    Upload a produce photo — triggers AI grading automatically.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        listing = get_object_or_404(ProduceListing, pk=pk)

        # Only the farmer who owns the listing can upload a photo
        if listing.farmer != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only upload photos for your own listings.')

        serializer = PhotoUploadSerializer(listing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Trigger AI grading synchronously (simple for now)
        from grading.service import run_grading
        result = run_grading(listing)

        return Response({
            'message': 'Photo uploaded. Grading complete.',
            'listing_id': listing.id,
            'grading': result,
        })

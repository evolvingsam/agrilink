from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from farmers.models import ProduceListing
from .models import GradingResult
from .serializers import GradingResultSerializer
from .service import run_grading


class AssessView(APIView):
    """
    POST /api/grading/assess/
    Manually trigger AI grading for a listing that already has a photo.
    Body: { "listing_id": <int> }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get('listing_id')
        if not listing_id:
            return Response({'error': 'listing_id is required.'}, status=400)

        listing = get_object_or_404(ProduceListing, pk=listing_id)

        # Farmers can only grade their own; admins can grade any
        if not request.user.is_staff and listing.farmer != request.user:
            return Response({'error': 'Permission denied.'}, status=403)

        result = run_grading(listing)
        return Response(result)


class GradingResultDetailView(APIView):
    """
    GET /api/grading/results/<listing_id>/
    Retrieve the grading result for a specific produce listing.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, listing_id):
        listing = get_object_or_404(ProduceListing, pk=listing_id)
        result = get_object_or_404(GradingResult, listing=listing)
        serializer = GradingResultSerializer(result)
        return Response(serializer.data)

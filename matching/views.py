from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BuyerOrder, Match
from .serializers import BuyerOrderSerializer, MatchSerializer
from .service import run_matching_cycle


class BuyerOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = BuyerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'buyer':
            return BuyerOrder.objects.filter(buyer=user)
        return BuyerOrder.objects.all()

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)


class BuyerOrderDetailView(generics.RetrieveAPIView):
    serializer_class = BuyerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BuyerOrder.objects.all()


class RunMatchingView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        matches_created = run_matching_cycle()
        return Response({'message': f'Matching cycle completed. {matches_created} matches created.'})


class OrderMatchesView(generics.ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return Match.objects.filter(order_id=order_id)

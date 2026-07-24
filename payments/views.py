from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from .service import process_mock_payment

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'farmer':
            return Payment.objects.filter(farmer=user)
        return Payment.objects.all()

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Payment.objects.all()

class TriggerPaymentView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, match_id):
        result = process_mock_payment(match_id)
        if 'error' in result:
            return Response(result, status=400)
        return Response(result)

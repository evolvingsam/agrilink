from decimal import Decimal
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BuyerOrder, Match
from .serializers import BuyerOrderSerializer, MatchSerializer
from .service import run_matching_cycle
from farmers.models import ProduceListing


class BuyerOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = BuyerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'buyer':
            return BuyerOrder.objects.filter(buyer=user).order_by('-created_at')
        return BuyerOrder.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        order = serializer.save(buyer=self.request.user)
        # For demo purposes, run the matching engine immediately when an order is placed
        # so we don't have to wait for a background cron job.
        try:
            run_matching_cycle()
            # Refresh to get the updated status after matching
            order.refresh_from_db()
        except Exception as e:
            # We don't want to fail the order creation if matching fails
            print(f"Error running matching cycle: {e}")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Re-read the saved instance to get the potentially updated status
        order = serializer.instance
        order.refresh_from_db()
        response_data = BuyerOrderSerializer(order).data
        matched = order.status == BuyerOrder.Status.WAITING_FOR_PAYMENT
        response_data['matched'] = matched
        response_data['match_message'] = (
            'A matching produce listing was found! Proceed to payment in My Orders.'
            if matched
            else 'Your order has been queued. We will notify you when a match is found.'
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class BuyerOrderDetailView(generics.RetrieveAPIView):
    serializer_class = BuyerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BuyerOrder.objects.all()


class PayOrderView(APIView):
    """
    POST /api/orders/<id>/pay/
    Deduct cost from buyer's wallet and move order to PROCESSING (demo payment).
    Cost = quantity_kg * listing's actual price_per_kg.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(BuyerOrder, pk=pk, buyer=request.user)

        if order.status != BuyerOrder.Status.WAITING_FOR_PAYMENT:
            return Response(
                {'error': f'Order is already {order.status}. Only orders awaiting payment can be paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        matches = Match.objects.filter(order=order)
        if not matches.exists():
            return Response(
                {'error': 'This order has no matches yet.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        match = matches.first()
        listing = match.listing
        
        # Buyer pays the listing's actual price for the ordered quantity
        cost = Decimal(str(order.quantity_kg)) * Decimal(str(listing.price_per_kg))
        user = request.user

        if user.wallet_balance < cost:
            return Response(
                {'error': f'Insufficient wallet balance. You need ₦{cost:,.2f} but have ₦{user.wallet_balance:,.2f}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct from buyer's wallet
        user.wallet_balance -= cost
        user.save(update_fields=['wallet_balance'])

        # Credit the farmer
        farmer = listing.farmer
        farmer.wallet_balance += cost
        farmer.save(update_fields=['wallet_balance'])
        
        # Reduce the listing quantity
        listing.quantity_kg -= order.quantity_kg
        if listing.quantity_kg <= 0:
            listing.quantity_kg = Decimal('0.00')
            listing.status = ProduceListing.Status.SOLD
        else:
            # If there's still produce left, it goes back to graded so it can be matched again
            listing.status = ProduceListing.Status.GRADED
        listing.save(update_fields=['quantity_kg', 'status'])
        
        # Create a mock payment record for history
        from payments.models import Payment
        from django.utils import timezone
        import uuid
        Payment.objects.create(
            farmer=farmer,
            match=match,
            amount_ngn=cost,
            status=Payment.Status.COMPLETED,
            provider=Payment.Provider.MOCK,
            transaction_ref=f"mock-tx-{uuid.uuid4().hex[:8]}",
            paid_at=timezone.now(),
        )

        # Advance order status to PROCESSING
        order.status = BuyerOrder.Status.PROCESSING
        order.save(update_fields=['status'])

        return Response({
            'success': True,
            'message': f'Payment of ₦{cost:,.2f} processed successfully!',
            'new_wallet_balance': float(user.wallet_balance),
            'order_status': order.status,
        })


class AcceptDeliveryView(APIView):
    """
    POST /api/orders/<id>/accept-delivery/
    Called by a dispatcher when they accept/pick up the order for delivery.
    Moves order from PROCESSING → DELIVERY_IN_PROCESS.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # Dispatchers (or admins) can accept; in a real system you'd verify assignment
        order = get_object_or_404(BuyerOrder, pk=pk)

        if order.status != BuyerOrder.Status.PROCESSING:
            return Response(
                {'error': f'Order is {order.status}. Only orders in processing can be accepted for delivery.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = BuyerOrder.Status.DELIVERY_IN_PROCESS
        order.save(update_fields=['status'])

        return Response({
            'success': True,
            'message': 'Order accepted for delivery. Status is now Delivery in Process.',
            'order_status': order.status,
        })


class CompleteDeliveryView(APIView):
    """
    POST /api/orders/<id>/complete-delivery/
    Called by a dispatcher when the order has been delivered.
    Moves order from DELIVERY_IN_PROCESS → COMPLETED.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(BuyerOrder, pk=pk)

        if order.status != BuyerOrder.Status.DELIVERY_IN_PROCESS:
            return Response(
                {'error': f'Order is {order.status}. Only orders in delivery can be completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = BuyerOrder.Status.COMPLETED
        order.save(update_fields=['status'])

        # Also mark the match as delivered
        Match.objects.filter(order=order).update(status=Match.Status.DELIVERED)

        return Response({
            'success': True,
            'message': 'Order marked as delivered and completed!',
            'order_status': order.status,
        })


class CancelOrderView(APIView):
    """
    DELETE /api/orders/<id>/cancel/
    Cancel an OPEN or WAITING_FOR_PAYMENT order (before payment). Refunds nothing.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        order = get_object_or_404(BuyerOrder, pk=pk, buyer=request.user)

        if order.status not in [BuyerOrder.Status.OPEN, BuyerOrder.Status.WAITING_FOR_PAYMENT]:
            return Response(
                {'error': 'Only unpaid orders (open or awaiting payment) can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = BuyerOrder.Status.CANCELLED
        order.save(update_fields=['status'])

        return Response({'success': True, 'message': 'Order cancelled.'})


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
        return Match.objects.filter(order_id=order_id).order_by('-created_at')

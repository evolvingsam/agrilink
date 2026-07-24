from django.urls import path
from .views import BuyerOrderListCreateView, BuyerOrderDetailView, RunMatchingView, OrderMatchesView

urlpatterns = [
    path('orders/', BuyerOrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', BuyerOrderDetailView.as_view(), name='order-detail'),
    path('matching/run/', RunMatchingView.as_view(), name='matching-run'),
    path('matching/results/<int:order_id>/', OrderMatchesView.as_view(), name='matching-results'),
]

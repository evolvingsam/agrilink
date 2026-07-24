from django.urls import path
from .views import (
    BuyerOrderListCreateView,
    BuyerOrderDetailView,
    PayOrderView,
    AcceptDeliveryView,
    CompleteDeliveryView,
    CancelOrderView,
    RunMatchingView,
    OrderMatchesView,
)

urlpatterns = [
    path('', BuyerOrderListCreateView.as_view(), name='order-list'),
    path('<int:pk>/', BuyerOrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/pay/', PayOrderView.as_view(), name='order-pay'),
    path('<int:pk>/accept-delivery/', AcceptDeliveryView.as_view(), name='order-accept-delivery'),
    path('<int:pk>/complete-delivery/', CompleteDeliveryView.as_view(), name='order-complete-delivery'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
    path('matching/run/', RunMatchingView.as_view(), name='matching-run'),
    path('matching/results/<int:order_id>/', OrderMatchesView.as_view(), name='matching-results'),
]

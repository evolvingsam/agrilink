from django.urls import path
from .views import PaymentListView, PaymentDetailView, TriggerPaymentView

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('trigger/<int:match_id>/', TriggerPaymentView.as_view(), name='payment-trigger'),
]

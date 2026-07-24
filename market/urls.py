from django.urls import path
from .views import MarketTrendView, MarketPriceListView

app_name = 'market'

urlpatterns = [
    path('trends/', MarketTrendView.as_view(), name='trends'),
    path('prices/', MarketPriceListView.as_view(), name='prices'),
]

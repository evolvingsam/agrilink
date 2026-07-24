from django.urls import path
from .views import DispatchRouteListView, DispatchRouteDetailView, GenerateRoutesView, RouteBriefingView

urlpatterns = [
    path('routes/', DispatchRouteListView.as_view(), name='route-list'),
    path('routes/<int:pk>/', DispatchRouteDetailView.as_view(), name='route-detail'),
    path('routes/<int:pk>/status/', DispatchRouteDetailView.as_view(), name='route-status'), # Re-using detail view for status update
    path('routes/<int:pk>/briefing/', RouteBriefingView.as_view(), name='route-briefing'),
    path('routes/generate/', GenerateRoutesView.as_view(), name='route-generate'),
]

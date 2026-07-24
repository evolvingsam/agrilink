from django.urls import path
from .views import AssessView, GradingResultDetailView

urlpatterns = [
    path('assess/', AssessView.as_view(), name='grading-assess'),
    path('results/<int:listing_id>/', GradingResultDetailView.as_view(), name='grading-result'),
]

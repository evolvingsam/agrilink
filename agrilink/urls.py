"""agrilink URL configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API schema + docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # App routes
    path('api/auth/', include('accounts.urls')),
    path('api/produce/', include('farmers.urls')),
    path('api/grading/', include('grading.urls')),
    path('api/assistant/', include('ai_assistant.urls')),
    path('api/orders/', include('matching.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/logistics/', include('logistics.urls')),
    path('api/market/', include('market.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

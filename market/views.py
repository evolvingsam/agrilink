from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .models import MarketPrice
from .serializers import MarketPriceSerializer, MarketTrendResponseSerializer
from .service import calculate_market_trends
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class MarketPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MarketTrendView(APIView):
    """
    Returns a summary of market trends and demand forecasting.
    """
    @extend_schema(
        parameters=[
            OpenApiParameter('region_id', OpenApiTypes.STR, description='Filter by state/region name'),
        ],
        responses=MarketTrendResponseSerializer,
    )
    def get(self, request):
        region_id = request.query_params.get('region_id')
        data = calculate_market_trends(region_id)
        
        # Validate data structure using serializer for consistent API schema
        serializer = MarketTrendResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            "status": "success",
            "data": serializer.validated_data
        })

class MarketPriceListView(ListAPIView):
    """
    Returns a filterable, paginated list of daily commodity prices.
    """
    serializer_class = MarketPriceSerializer
    pagination_class = MarketPagination

    @extend_schema(
        parameters=[
            OpenApiParameter('crop_id', OpenApiTypes.INT, description='Filter by crop ID'),
            OpenApiParameter('hub_id', OpenApiTypes.INT, description='Filter by collection point ID'),
        ]
    )
    def get_queryset(self):
        queryset = MarketPrice.objects.select_related('crop_type', 'collection_point').all()
        
        crop_id = self.request.query_params.get('crop_id')
        if crop_id:
            queryset = queryset.filter(crop_type_id=crop_id)
            
        hub_id = self.request.query_params.get('hub_id')
        if hub_id:
            queryset = queryset.filter(collection_point_id=hub_id)
            
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        # Modify default DRF pagination structure to match requested frontend format exactly
        paginated_data = response.data
        return Response({
            "status": "success",
            "data": paginated_data.get('results', []),
            "pagination": {
                "current_page": self.paginator.page.number if self.paginator.page else 1,
                "total_pages": self.paginator.page.paginator.num_pages if self.paginator.page else 1
            }
        })

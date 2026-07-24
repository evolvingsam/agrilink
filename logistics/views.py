from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DispatchRoute
from .serializers import DispatchRouteSerializer
from .service import generate_routes

class DispatchRouteListView(generics.ListAPIView):
    serializer_class = DispatchRouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'dispatcher':
            return DispatchRoute.objects.filter(dispatcher=user)
        return DispatchRoute.objects.all()

class DispatchRouteDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = DispatchRouteSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DispatchRoute.objects.all()

class GenerateRoutesView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        routes_created = generate_routes()
        return Response({'message': f'Routing completed. {routes_created} routes generated.'})

class RouteBriefingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            route = DispatchRoute.objects.get(pk=pk)
        except DispatchRoute.DoesNotExist:
            return Response({'error': 'Route not found'}, status=404)
        
        return Response({'briefing': route.briefing_text})

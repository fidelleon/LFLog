from rest_framework import permissions, viewsets

from .models import MyStation
from .serializers import MyStationSerializer


class MyStationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stations to be viewed or edited.
    """
    queryset = MyStation.objects.all()
    serializer_class = MyStationSerializer
    permission_classes = [permissions.IsAuthenticated]

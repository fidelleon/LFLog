# my_station/serializers
from rest_framework import serializers

from .models import MyStation


class MyStationSerializer(serializers.ModelSerializer):
    """
    Serializer for the MyStation model.
    """
    class Meta:
        """
        DRF Meta params for the serializer
        """
        model = MyStation
        fields = '__all__'

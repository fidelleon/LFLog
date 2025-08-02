from django.urls import include, path
from rest_framework import routers

from . import views as mystation_views

router = routers.DefaultRouter()
router.register('my_stations', mystation_views.MyStationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

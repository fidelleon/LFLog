# mysite/urls.py
from django.contrib import admin
from django.urls import include, path

from my_station import urls as my_stations_urls


urlpatterns = [
    path("chat/", include("chat.urls")),
    path("admin/", admin.site.urls),
    path("stations/", include(my_stations_urls)),
]

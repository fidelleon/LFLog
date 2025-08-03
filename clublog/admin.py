from django.contrib import admin
from . import models


admin.site.register(models.ClubLogEntity)
admin.site.register(models.ClubLogPrefix)
admin.site.register(models.ClubLogZoneException)
admin.site.register(models.ClubLogException)
admin.site.register(models.ClubLogInvalidOperation)

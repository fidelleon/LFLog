# my_station/models
#
# Holds user station records
#
from django.contrib.gis.db import models


class MyStation(models.Model):
    """
    Holds information about the user's station(s)
    """
    # Good to have:
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # Model fields
    description = models.TextField(blank=False, null=False)
    # TODO: add callsign field validation
    callsign = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    street = models.CharField(max_length=255, blank=True, null=False, default='')
    city = models.CharField(max_length=255, blank=True, null=False, default='')
    state = models.CharField(max_length=255, blank=True, null=False, default='')
    zipcode = models.CharField(max_length=255, blank=True, null=False, default='', verbose_name='Zip')
    email = models.EmailField(max_length=255, blank=True, null=False, default='')
    # TODO: add locator field validation - must be done on save
    locator = models.CharField(max_length=10, blank=False, null=False)
    latitude = models.FloatField(blank=False, null=False, default=0)
    longitude = models.FloatField(blank=False, null=False, default=0)
    cq_zone = models.PositiveIntegerField(blank=False, null=False, default=0, verbose_name='CQ Zone')
    itu_zone = models.PositiveIntegerField(blank=False, null=False, default=0, verbose_name='ITU Zone')
    # TODO: country depends upon ARRL DXCC data
    country = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self) -> str:
        """
        Combines description and callsign

        :return:
        """
        return self.description + ' - ' + self.callsign

    def save(self, *args, **kwargs):
        """
        To be overriden and be able to do checks

        :param args:
        :param kwargs:
        :return:
        """
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'My Station'
        verbose_name_plural = 'My Stations'

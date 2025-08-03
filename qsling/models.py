import csv
import datetime
import io

import requests
from django.db import models, transaction
from django.utils import timezone


class LoTWUser(models.Model):
    """
    This will store the LoTW users records
    """
    callsign = models.CharField(max_length=50, blank=False, null=False, db_index=True)
    date_from = models.DateTimeField(blank=False, null=False)

    @staticmethod
    @transaction.atomic
    def update_tables() -> int:
        """
        Clear the table
        Get the records from Internet
        Populate table
        Profit!

        :return: number of created records
        """
        LoTWUser.objects.all().delete()
        lotw_users = 'https://lotw.arrl.org/lotw-user-activity.csv'
        lotw_csv = requests.get(lotw_users)
        lotw_csv.raise_for_status()
        csvio = io.StringIO(lotw_csv.text)
        batch_list = []
        for row in csv.reader(csvio):
            batch_list.append(
                LoTWUser(
                    callsign=row[0],
                    date_from=datetime.datetime.fromisoformat((row[1] + ' ' + row[2] + 'Z'))
                )
            )
        LoTWUser.objects.bulk_create(batch_list)
        return len(batch_list)

    def __str__(self) -> str:
        """
        Just show its callsign, okay?
        :return:
        """
        return self.callsign

    class Meta:
        verbose_name_plural = "LoTW Users"
        verbose_name = "LoTW User"


class eQSLUser(models.Model):
    """
    This will store the eQSL.cc users records
    """
    callsign = models.CharField(max_length=50, blank=False, null=False, db_index=True)
    date_from = models.DateTimeField(blank=False, null=False, default=timezone.now)

    @staticmethod
    @transaction.atomic
    def update_tables() -> int:
        """
        Clear the table
        Get the records from Internet
        Populate table
        Profit!

        :return: number of created records
        """
        eQSLUser.objects.all().delete()
        eqsl_users = 'https://www.eqsl.cc/qslcard/DownloadedFiles/AGMemberList.txt'
        eqsl_csv = requests.get(eqsl_users)
        eqsl_csv.raise_for_status()
        csvio = io.StringIO(eqsl_csv.text)
        batch_list = []
        for row in csv.reader(csvio):
            batch_list.append(
                eQSLUser(
                    callsign=row[0],
                )
            )
        eQSLUser.objects.bulk_create(batch_list)
        return len(batch_list)

    def __str__(self) -> str:
        """
        Just show its callsign, okay?
        :return:
        """
        return self.callsign

    class Meta:
        verbose_name_plural = "eQSL Users"
        verbose_name = "eQSL User"

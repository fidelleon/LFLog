import datetime
import gzip
import io
import os
from zoneinfo import ZoneInfo

import requests
import xmltodict
from django.db import models, transaction


def update_tables() -> None:
    """
    Clear the tables
    Get the records from Internet
    Populate table
    Profit!

    :return: nada
    """
    clublog_api_key = os.environ['CLUBLOG_API_KEY']
    clublog_xml = f"https://cdn.clublog.org/cty.php?api={clublog_api_key}"
    answer = requests.get(clublog_xml)
    answer.raise_for_status()
    ungzipped = gzip.GzipFile(fileobj=io.BytesIO(answer.content))
    clublog_data = xmltodict.parse(ungzipped.read().decode('utf8'))

    # Each models knows how to deal with its records
    entities = clublog_data['clublog']['entities']['entity']
    ClubLogEntity.update_table(entities)

    prefixes = clublog_data['clublog']['prefixes']['prefix']
    ClubLogPrefix.update_table(prefixes)

    zone_exceptions = clublog_data['clublog']['zone_exceptions']['zone_exception']
    ClubLogZoneException.update_table(zone_exceptions)

    exceptions = clublog_data['clublog']['exceptions']['exception']
    ClubLogException.update_table(exceptions)

    invalid_operations = clublog_data['clublog']['invalid_operations']['invalid']
    ClubLogInvalidOperation.update_table(invalid_operations)


class ClubLogEntity(models.Model):
    """
    Received from ClubLog API
    """
    adif = models.IntegerField(blank=False, null=False, db_index=True, primary_key=True)
    name = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    prefix = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    deleted = models.BooleanField(blank=False, null=False, default=False, db_index=True)
    cqz = models.IntegerField(blank=False, null=False, db_index=True)
    cont = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    long = models.FloatField(blank=False, null=False)
    lat = models.FloatField(blank=False, null=False)
    start = models.DateTimeField(blank=False, null=False,
                                 default=datetime.datetime(1900, 1, 1, tzinfo=ZoneInfo('UTC')))
    end = models.DateTimeField(blank=False, null=False,
                               default=datetime.datetime(2100, 1, 1, tzinfo=ZoneInfo('UTC')))

    whitelisted = models.BooleanField(blank=False, null=False, default=True)
    whitelist_start = models.DateTimeField(blank=True, null=True)
    whitelist_end = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        """
        Name and ADIF code
        :return:
        """
        return f'{self.name} ({self.adif})'

    @staticmethod
    @transaction.atomic
    def update_table(entities: list) -> int:
        """
        Gets the list of entities and adds them to the database

        :param entities:
        :return:
        """
        ClubLogEntity.objects.all().delete()
        batch_list = []
        for entity in entities:
            ent = ClubLogEntity()
            ent.adif = int(entity['adif'])
            ent.name = entity['name']
            ent.prefix = entity['prefix']
            ent.deleted = entity['deleted'] == 'true'
            ent.cqz = int(entity['cqz'])
            ent.cont = entity['cont']
            ent.long = float(entity['long'])
            ent.lat = float(entity['lat'])
            start = entity.get('start')
            ent.start = datetime.datetime.fromisoformat(start) if start else datetime.datetime(1900, 1, 1,
                                                                                               tzinfo=ZoneInfo('UTC'))
            end = entity.get('end')
            ent.end = datetime.datetime.fromisoformat(end) if end else datetime.datetime(2100, 1, 1,
                                                                                         tzinfo=ZoneInfo('UTC'))
            ent.whitelisted = entity.get('whitelisted', True)
            whitelist_start = entity.get('whitelist_start')
            ent.whitelist_start = datetime.datetime.fromisoformat(
                whitelist_start) if whitelist_start else datetime.datetime(1900, 1, 1, tzinfo=ZoneInfo('UTC'))
            whitelist_end = entity.get('whitelist_end')
            ent.whitelist_end = datetime.datetime.fromisoformat(whitelist_end) if whitelist_end else datetime.datetime(
                2100,
                1, 1,
                tzinfo=ZoneInfo(
                    'UTC'))
            batch_list.append(ent)
        ClubLogEntity.objects.bulk_create(batch_list)
        return len(batch_list)

    class Meta:
        verbose_name_plural = 'ClubLog Entities'
        verbose_name = 'ClubLog Entity'
        ordering = ('adif',)


class ClubLogPrefix(models.Model):
    """
    Received from ClubLog API
    """
    record = models.IntegerField(blank=False, null=False, db_index=True, primary_key=True)
    call = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    entity = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    adif = models.IntegerField(blank=False, null=False, db_index=True)
    cqz = models.IntegerField(blank=False, null=False, db_index=True)
    cont = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    long = models.FloatField(blank=False, null=False)
    lat = models.FloatField(blank=False, null=False)
    start = models.DateTimeField(blank=False, null=False,
                                 default=datetime.datetime(1900, 1, 1, tzinfo=ZoneInfo('UTC')))
    end = models.DateTimeField(blank=False, null=False,
                               default=datetime.datetime(2100, 1, 1, tzinfo=ZoneInfo('UTC')))

    def __str__(self) -> str:
        """
        Call and record
        :return:
        """
        return f'{self.call} ({self.record})'

    @staticmethod
    @transaction.atomic
    def update_table(prefixes: list) -> int:
        """
        Gets the list of prefixes and adds them to the database

        :param prefixes: list
        :return:
        """
        ClubLogPrefix.objects.all().delete()
        batch_list = []
        for prefix in prefixes:
            pfx = ClubLogPrefix()
            pfx.record = int(prefix['@record'])
            pfx.call = prefix['call']
            pfx.entity = prefix['entity']
            pfx.adif = int(prefix['adif'])
            pfx.cqz = int(prefix['cqz'])
            pfx.cont = prefix['cont']
            pfx.long = float(prefix.get('long', 0))
            pfx.lat = float(prefix.get('lat', 0))
            start = prefix.get('start')
            pfx.start = datetime.datetime.fromisoformat(start) if start else datetime.datetime(1900, 1, 1,
                                                                                               tzinfo=ZoneInfo('UTC'))
            end = prefix.get('end')
            pfx.end = datetime.datetime.fromisoformat(end) if end else datetime.datetime(2100, 1, 1,
                                                                                         tzinfo=ZoneInfo('UTC'))
            batch_list.append(pfx)
        ClubLogPrefix.objects.bulk_create(batch_list)
        return len(batch_list)

    class Meta:
        verbose_name_plural = 'ClubLog Prefixes'
        verbose_name = 'ClubLog Prefix'
        ordering = ('call',)


class ClubLogZoneException(models.Model):
    """
    Received from ClubLog API
    """
    record = models.IntegerField(blank=False, null=False, db_index=True, primary_key=True)
    call = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    zone = models.IntegerField(blank=False, null=False, db_index=True)
    start = models.DateTimeField(blank=False, null=False,
                                 default=datetime.datetime(1900, 1, 1, tzinfo=ZoneInfo('UTC')))
    end = models.DateTimeField(blank=False, null=False,
                               default=datetime.datetime(2100, 1, 1, tzinfo=ZoneInfo('UTC')))

    def __str__(self) -> str:
        """
        Call and record
        :return:
        """
        return f'{self.call} ({self.record})'

    @staticmethod
    @transaction.atomic
    def update_table(zone_exceptions: list) -> int:
        """
        Gets the list of zone exceptions and adds them to the database

        :param zone_exceptions: list
        :return:
        """
        ClubLogZoneException.objects.all().delete()
        batch_list = []
        for prefix in zone_exceptions:
            exc = ClubLogZoneException()
            exc.record = int(prefix['@record'])
            exc.call = prefix['call']
            exc.zone = int(prefix['zone'])
            start = prefix.get('start')
            exc.start = datetime.datetime.fromisoformat(start) if start else datetime.datetime(1900, 1, 1,
                                                                                               tzinfo=ZoneInfo('UTC'))
            end = prefix.get('end')
            exc.end = datetime.datetime.fromisoformat(end) if end else datetime.datetime(2100, 1, 1,
                                                                                         tzinfo=ZoneInfo('UTC'))
            batch_list.append(exc)
        ClubLogZoneException.objects.bulk_create(batch_list)
        return len(batch_list)

    class Meta:
        verbose_name_plural = 'ClubLog Zone Exceptions'
        verbose_name = 'ClubLog Zone Exception'
        ordering = ('call',)


class ClubLogException(models.Model):
    """
    Received from ClubLog API
    """
    record = models.IntegerField(blank=False, null=False, db_index=True, primary_key=True)
    call = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    entity = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    adif = models.IntegerField(blank=False, null=False, db_index=True)
    cqz = models.IntegerField(blank=False, null=False, db_index=True)
    cont = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    long = models.FloatField(blank=False, null=False)
    lat = models.FloatField(blank=False, null=False)
    start = models.DateTimeField(blank=False, null=False,
                                 default=datetime.datetime(1900, 1, 1, tzinfo=ZoneInfo('UTC')))
    end = models.DateTimeField(blank=False, null=False,
                               default=datetime.datetime(2100, 1, 1, tzinfo=ZoneInfo('UTC')))

    def __str__(self) -> str:
        """
        Call and record
        :return:
        """
        return f'{self.call} ({self.record})'

    @staticmethod
    @transaction.atomic
    def update_table(exceptions: list) -> int:
        """
        Gets the list of prefixes and adds them to the database

        :param exceptions: list
        :return:
        """
        ClubLogException.objects.all().delete()
        batch_list = []
        for exc in exceptions:
            clexc = ClubLogException()
            clexc.record = int(exc['@record'])
            clexc.call = exc['call']
            clexc.entity = exc['entity']
            clexc.adif = int(exc['adif'])
            clexc.cqz = int(exc.get('cqz', 0))
            clexc.cont = exc.get('cont', '')
            clexc.long = float(exc.get('long', 0))
            clexc.lat = float(exc.get('lat', 0))
            start = exc.get('start')
            clexc.start = datetime.datetime.fromisoformat(start) if start else datetime.datetime(1900, 1, 1,
                                                                                                 tzinfo=ZoneInfo('UTC'))
            end = exc.get('end')
            clexc.end = datetime.datetime.fromisoformat(end) if end else datetime.datetime(2100, 1, 1,
                                                                                           tzinfo=ZoneInfo('UTC'))
            batch_list.append(clexc)
        ClubLogException.objects.bulk_create(batch_list)
        return len(batch_list)

    class Meta:
        verbose_name_plural = 'ClubLog Exceptions'
        verbose_name = 'ClubLog Exception'
        ordering = ('call',)


class ClubLogInvalidOperation(models.Model):
    """
    Received from ClubLog API
    """
    record = models.IntegerField(blank=False, null=False, db_index=True, primary_key=True)
    call = models.CharField(blank=False, null=False, max_length=255, db_index=True)
    start = models.DateTimeField(blank=False, null=False,
                                 default=datetime.datetime(1900, 1, 1, tzinfo=ZoneInfo('UTC')))
    end = models.DateTimeField(blank=False, null=False,
                               default=datetime.datetime(2100, 1, 1, tzinfo=ZoneInfo('UTC')))

    def __str__(self) -> str:
        """
        Call and record
        :return:
        """
        return f'{self.call} ({self.record})'

    @staticmethod
    @transaction.atomic
    def update_table(invalid_records: list) -> int:
        """
        Gets the list of invalid records and adds them to the database

        :param invalid_records: list
        :return:
        """
        ClubLogInvalidOperation.objects.all().delete()
        batch_list = []
        for invalid in invalid_records:
            inv = ClubLogInvalidOperation()
            inv.record = int(invalid['@record'])
            inv.call = invalid['call']
            start = invalid.get('start')
            inv.start = datetime.datetime.fromisoformat(start) if start else datetime.datetime(1900, 1, 1,
                                                                                               tzinfo=ZoneInfo('UTC'))
            end = invalid.get('end')
            inv.end = datetime.datetime.fromisoformat(end) if end else datetime.datetime(2100, 1, 1,
                                                                                         tzinfo=ZoneInfo('UTC'))
            batch_list.append(inv)
        ClubLogInvalidOperation.objects.bulk_create(batch_list)
        return len(batch_list)

    class Meta:
        verbose_name_plural = 'ClubLog Zone Invalid Operations'
        verbose_name = 'ClubLog Zone Invalid Operation'
        ordering = ('call',)

# coding=utf8


from django.db import models
from django.utils import timezone

from django_echarts.datasets.managers import AxisValuesQuerySet


class Device(models.Model):
    mac = models.CharField(max_length=50, unique=True, verbose_name="MAC地址", )
    name = models.CharField(max_length=50, default='-', verbose_name="设备名称")
    device_type = models.CharField(max_length=50, verbose_name="设备类型")
    latitude = models.FloatField(null=True, blank=True, verbose_name="经度")
    longitude = models.FloatField(null=True, blank=True, verbose_name="纬度")
    address = models.CharField(max_length=50, null=True, blank=True, verbose_name="Install Address")
    battery_life = models.IntegerField(verbose_name='电量(%)', default=100)
    online = models.NullBooleanField(default=None, verbose_name="在线状态")
    parent_gateway_mac = models.CharField(max_length=50, blank=True, null=True)
    parent_rtu_mac = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.mac


class DataRecord(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    record_time = models.DateTimeField(default=timezone.now)
    val1 = models.IntegerField()
    val2 = models.IntegerField()

    def __str__(self):
        return 'Data Record {0}'.format(self.device.mac)


class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    author = models.CharField(max_length=50)
    post_time = models.DateTimeField(default=timezone.now)
    read_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class TemperatureRecord(models.Model):
    high = models.FloatField()
    low = models.FloatField()
    create_time = models.DateTimeField(default=timezone.now)

    objects = models.Manager.from_queryset(AxisValuesQuerySet)()

    def __str__(self):
        return 'Temperature Record'


class MalfunctionData(models.Model):
    city = models.CharField(db_column='city', max_length=6, blank=True, null=True)
    profession = models.CharField(db_column='profession', max_length=20, blank=True, null=True)
    department = models.CharField(db_column='department', max_length=200, blank=True, null=True)
    malfunctionCity = models.CharField(db_column='malfunctionCity', max_length=6, blank=True, null=True)
    receiptNumber = models.CharField(db_column='receiptNumber', primary_key=True, max_length=20)
    receiptSerialNumber = models.CharField(db_column='receiptSerialNumber', max_length=20)
    receiptStatus = models.CharField(db_column='receiptStatus', max_length=10, blank=True, null=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200, blank=True, null=True)
    distributeTime = models.DateTimeField(db_column='distributeTime')
    processTime = models.IntegerField(db_column='processTime', blank=True, null=True)
    hangTime = models.IntegerField(db_column='hangTime')
    malfunctionSource = models.CharField(db_column='malfunctionSource', max_length=50, blank=True, null=True)
    isTimeOut = models.CharField(db_column='isTimeOut', max_length=2, blank=True, null=True)
    dutyDepartment = models.CharField(db_column='dutyDepartment', max_length=200, blank=True, null=True)
    conclusion = models.CharField(max_length=1024, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    reasonClassification = models.CharField(db_column='reasonClassification', max_length=50, blank=True, null=True)
    malfunctionJudgment = models.CharField(db_column='malfunctionJudgment', max_length=50, blank=True, null=True)
    malfunctionReason = models.CharField(db_column='malfunctionReason', max_length=50, blank=True, null=True)
    originProfession = models.CharField(db_column='originProfession', max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'report_malfunction_data'


class District(models.Model):
    id = models.IntegerField(primary_key=True)
    district = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'report_district'


class City(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'report_city'


class DistrictCity(models.Model):
    district = models.ForeignKey('District', models.DO_NOTHING, blank=True, null=False)
    city = models.ForeignKey('City', models.DO_NOTHING, blank=True, null=False)

    class Meta:
        managed = False
        db_table = 'report_district_city'

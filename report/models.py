# coding=utf8
from django.db import models


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
        # managed = False
        db_table = 'report_malfunction_data'


class District(models.Model):
    district = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_district'


class City(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_city'


class DistrictCity(models.Model):
    district = models.ForeignKey('District', models.DO_NOTHING, blank=True, null=False)
    city = models.ForeignKey('City', models.DO_NOTHING, blank=True, null=False)

    class Meta:
        # managed = False
        db_table = 'report_district_city'


class StatisticsAmount(models.Model):
    yearNum = models.SmallIntegerField(blank=True, null=True)
    quarterNum = models.IntegerField(blank=True, null=True)
    monthNum = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    profession = models.CharField(max_length=10, blank=True, null=True)
    statisticsType = models.CharField(max_length=20, blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_amount'


class StatisticsInTimeRate(models.Model):
    yearNum = models.SmallIntegerField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    monthNum = models.IntegerField(blank=True, null=True)
    quarterNum = models.IntegerField(blank=True, null=True)
    statisticsType = models.IntegerField(blank=True, null=True)
    result = models.FloatField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_in_time_rate'


class StatisticsDealTime(models.Model):
    yearNum = models.SmallIntegerField(db_column='yearNum', blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    monthNum = models.IntegerField(db_column='monthNum', blank=True, null=True)
    quarterNum = models.IntegerField(db_column='quarterNum', blank=True, null=True)
    statisticsType = models.IntegerField(db_column='statisticsType', blank=True, null=True)
    result = models.FloatField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_deal_time'


class StatisticsOver48Rate(models.Model):
    yearNum = models.SmallIntegerField(db_column='yearNum', blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    monthNum = models.IntegerField(db_column='monthNum', blank=True, null=True)
    quarterNum = models.IntegerField(db_column='quarterNum', blank=True, null=True)
    statisticsType = models.IntegerField(db_column='statisticsType', blank=True, null=True)
    result = models.FloatField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_over48_rate'


class StatisticsSpecificDealTime(models.Model):
    yearNum = models.SmallIntegerField(db_column='yearNum', blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    monthNum = models.IntegerField(db_column='monthNum', blank=True, null=True)
    quarterNum = models.IntegerField(db_column='quarterNum', blank=True, null=True)
    statisticsType = models.IntegerField(db_column='statisticsType', blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    reason = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_specific_deal_time'


class StatisticsReason(models.Model):
    yearNum = models.SmallIntegerField(db_column='yearNum', blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    monthNum = models.IntegerField(db_column='monthNum', blank=True, null=True)
    quarterNum = models.IntegerField(db_column='quarterNum', blank=True, null=True)
    statisticsType = models.IntegerField(db_column='statisticsType', blank=True, null=True)
    reason = models.CharField(max_length=20, blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_reason'

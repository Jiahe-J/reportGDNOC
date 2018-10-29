# coding=utf8
from django.db import models


class MalfunctionData(models.Model):
    city = models.CharField(db_column='city', max_length=6, blank=True, null=True, db_index=True)
    ne = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    profession = models.CharField(db_column='profession', max_length=20, blank=True, null=True, db_index=True)
    department = models.CharField(db_column='department', max_length=200, blank=True, null=True)
    malfunctionCity = models.CharField(db_column='malfunctionCity', max_length=6, blank=True, null=True)
    receiptNumber = models.CharField(db_column='receiptNumber', primary_key=True, max_length=20)
    receiptSerialNumber = models.CharField(db_column='receiptSerialNumber', max_length=20)
    receiptStatus = models.CharField(db_column='receiptStatus', max_length=10, blank=True, null=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200, blank=True, null=True)
    distributeTime = models.DateTimeField(db_column='distributeTime', db_index=True)
    processTime = models.IntegerField(db_column='processTime', blank=True, null=True)
    hangTime = models.IntegerField(db_column='hangTime')
    malfunctionSource = models.CharField(db_column='malfunctionSource', max_length=50, blank=True, null=True, db_index=True)
    isTimeOut = models.CharField(db_column='isTimeOut', max_length=2, blank=True, null=True, db_index=True)
    dutyDepartment = models.CharField(db_column='dutyDepartment', max_length=200, blank=True, null=True)
    conclusion = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    type = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    reasonClassification = models.CharField(db_column='reasonClassification', max_length=50, blank=True, null=True)
    malfunctionJudgment = models.CharField(db_column='malfunctionJudgment', max_length=50, blank=True, null=True)
    malfunctionReason = models.CharField(db_column='malfunctionReason', max_length=50, blank=True, null=True)
    originProfession = models.CharField(db_column='originProfession', max_length=20, blank=True, null=True)
    district = models.ForeignKey('District', models.DO_NOTHING, blank=True, null=True)
    # 0-未分类，1-配置，2-其它，3-设备，4-线路，5-动环及配套
    sortedReason = models.IntegerField(db_column='sortedReason', default=0)

    class Meta:
        # managed = False
        db_table = 'report_malfunction_data'


class District(models.Model):
    district = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'report_district'


class City(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'report_city'


class DistrictCity(models.Model):
    district = models.ForeignKey('District', models.DO_NOTHING, blank=True, null=False)
    city = models.ForeignKey('City', models.DO_NOTHING, blank=True, null=False)

    class Meta:
        db_table = 'report_district_city'


class StatisticsQuarterlyAmount(models.Model):
    area = models.CharField(max_length=6, blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    beginDate = models.DateField(db_column='beginDate', blank=True, null=True)
    endDate = models.DateField(db_column='endDate', blank=True, null=True)
    transmission = models.IntegerField(blank=True, null=True)
    dynamics = models.IntegerField(blank=True, null=True)
    exchange = models.IntegerField(blank=True, null=True)
    AN = models.IntegerField(blank=True, null=True)
    wireless = models.IntegerField(blank=True, null=True)
    sum = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'report_statistics_quarterly_amount'


class StatisticsQuarterlyQuality(models.Model):
    area = models.CharField(max_length=6, blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    IntimeRate = models.FloatField(db_column='IntimeRate', blank=True, null=True)
    Over48Rate = models.FloatField(db_column='Over48Rate', blank=True, null=True)
    AverageTime = models.FloatField(db_column='AverageTime', blank=True, null=True)
    SignRate = models.FloatField(db_column='SignRate', blank=True, null=True)
    beginDate = models.DateField(db_column='beginDate', blank=True, null=True)
    endDate = models.DateField(db_column='endDate', blank=True, null=True)

    class Meta:
        db_table = 'report_statistics_quarterly_quality'


class StatisticsQuarterlySpecificDealTime(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)
    beginDate = models.DateField()
    endDate = models.DateField()
    amount = models.FloatField(blank=True, null=True)
    reason = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'report_statistics_quarterly_specific_deal_time'


class StatisticsQuarterlyReason(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)
    reason = models.CharField(max_length=20, blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    beginDate = models.DateField()
    endDate = models.DateField()

    class Meta:
        # managed = False
        db_table = 'report_statistics_quarterly_reason'


class StatisticsQuarterlySpecificDealtimeAmount(models.Model):
    area = models.CharField(max_length=6, blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    line_time = models.FloatField(db_column='line_time', default=0)
    line_amount = models.IntegerField(db_column='line_amount', default=0)
    equipment_time = models.FloatField(db_column='equipment_time', default=0)
    equipment_amount = models.IntegerField(db_column='equipment_amount', default=0)
    environment_time = models.FloatField(db_column='environment_time', default=0)
    environment_amount = models.IntegerField(db_column='environment_amount', default=0)
    power_time = models.FloatField(db_column='power_time', default=0)
    power_amount = models.IntegerField(db_column='power_amount', default=0)
    other_time = models.FloatField(db_column='other_time', default=0)
    other_amount = models.IntegerField(db_column='other_amount', default=0)
    beginDate = models.DateField(db_column='beginDate', blank=True, null=True)
    endDate = models.DateField(db_column='endDate', blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_quarterly_specific_dealtime_amount'


class StatisticsMonthlyQuality(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)
    signRate = models.FloatField(db_column='signRate', blank=True, null=True)
    autoRate = models.FloatField(db_column='autoRate', blank=True, null=True)
    dealRate = models.FloatField(db_column='dealRate', blank=True, null=True)
    yearNum = models.SmallIntegerField(db_column='yearNum', blank=True, null=True)
    monthNum = models.IntegerField(db_column='monthNum', blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_monthly_quality'


class MalfunctionLongtime(models.Model):
    receiptNumber = models.CharField(db_column='receiptNumber', primary_key=True, max_length=20)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(db_column='city', max_length=50, blank=True, null=True, db_index=True)
    processTime = models.IntegerField(db_column='processTime', blank=True, null=True)
    errorPosition = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'report_malfunction_longtime'


class MalfunctionOnTrack(models.Model):
    receiptNumber = models.CharField(db_column='receiptNumber', primary_key=True, max_length=20)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200, blank=True, null=True)
    receiptStatus = models.CharField(db_column='receiptStatus', max_length=10, blank=True, null=True)
    city = models.CharField(db_column='city', max_length=50, blank=True, null=True, db_index=True)
    createTime = models.DateTimeField(db_column='createTime', db_index=True, null=True)

    class Meta:
        db_table = 'report_malfunction_track'


class StatisticsTop10Ne(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)
    profession = models.CharField(max_length=20)
    ne = models.CharField(max_length=200, blank=True, null=True)
    index = models.IntegerField()
    amount = models.IntegerField()
    yearNum = models.SmallIntegerField(db_column='yearNum')
    monthNum = models.IntegerField(db_column='monthNum')

    class Meta:
        # managed = False
        db_table = 'report_statistics_monthly_top10ne'


class StatisticsMonthlyAmount(models.Model):
    city = models.CharField(max_length=10, blank=True, null=True)
    amount = models.IntegerField()
    yearNum = models.SmallIntegerField(db_column='yearNum')
    monthNum = models.IntegerField(db_column='monthNum')

    class Meta:
        # managed = False
        db_table = 'report_statistics_monthly_amount'


class StatisticsMonthlyReason(models.Model):
    district = models.CharField(max_length=10, blank=True, null=True)
    yearNum = models.SmallIntegerField(db_column='yearNum', blank=True, null=True)
    monthNum = models.IntegerField(db_column='monthNum', blank=True, null=True)
    reason = models.CharField(max_length=20, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_monthly_reason'


class StatisticsMonthlyWorst10Department(models.Model):
    department = models.CharField(max_length=150)
    totalAmount = models.IntegerField(db_column='totalAmount', blank=True, null=True)
    intimeAmount = models.IntegerField(db_column='intimeAmount', blank=True, null=True)
    overtimeAmount = models.IntegerField(db_column='overtimeAmount', blank=True, null=True)
    intimeRate = models.FloatField(db_column='intimeRate')
    yearNum = models.SmallIntegerField(db_column='yearNum', blank=True, null=True)
    monthNum = models.IntegerField(db_column='monthNum', blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'report_statistics_monthly_worst10department'

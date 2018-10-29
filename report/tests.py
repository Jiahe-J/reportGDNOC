# Create your tests here.
import os

import sys

import datetime

# /Users/silenthz/Desktop/故障单样例数据.xls
# 2018-01-11 10:48:42

#  获取当前文件的路径，以及路径的父级文件夹名
import xlrd

pwd = os.path.dirname(os.path.realpath(__file__))
# 将项目目录加入setting
sys.path.append(pwd + "../")
# manage.py中
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataEcharts.settings")

import django

django.setup()

from utils.data_parser import parse_malfunction_data_xlsx
from report.models import MalfunctionData, MalfunctionLongtime, MalfunctionOnTrack

# MalfunctionData.objects.all().delete()
#
starttime = datetime.datetime.now()
# parse_malfunction_data_xlsx('/Users/silenthz/Desktop/数据可视化项目/数据清单/清单.xlsx', 0)
f = open('/Users/silenthz/Desktop/周报数据清单/遗留跟踪单.xls', 'rb')
file_contents = f.read()
workbook = xlrd.open_workbook(file_contents=file_contents)
sheet = workbook.sheet_by_index(0)
field_list = []

for field in sheet.row(0):
    field_list.append(field.value)
for i in range(1, sheet.nrows):
    title = sheet.row(i)[field_list.index('故障标题')].value
    category = sheet.row(i)[field_list.index('故障种类')].value
    receiptStatus = sheet.row(i)[field_list.index('故障状态')].value
    city = sheet.row(i)[field_list.index('故障地市')].value
    createTime = sheet.row(i)[field_list.index('建单时间')].value
    receiptNumber = sheet.row(i)[field_list.index('故障单号')].value
    if category.__contains__('业务单'):
        pass
    elif city == '省公司' and category.__contains__("IPRAN"):
        pass
    else:
        item = MalfunctionOnTrack.objects.get_or_create(receiptNumber=receiptNumber)
        item[0].title = title
        item[0].category = category
        item[0].receiptStatus = receiptStatus
        item[0].city = city
        item[0].createTime = createTime
        item[0].save()

endtime = datetime.datetime.now()
print((endtime - starttime).seconds)

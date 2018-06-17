# Create your tests here.
from utils.data_parser import parse_malfunction_data, delete_former_data
import datetime
from report.models import MalfunctionData

# /Users/silenthz/Desktop/故障单样例数据.xls
# 2018-01-11 10:48:42

starttime = datetime.datetime.now()
delete_former_data(2018, 1)
parse_malfunction_data('/Users/silenthz/Desktop/数据可视化项目/故障处理明细[20180424154921]_1.xls', 1)
parse_malfunction_data('/Users/silenthz/Desktop/数据可视化项目/故障处理明细[20180424154921]_2.xls', 1)
# MalfunctionData.objects.filter(distributeTime__gte='2017-06-01 00:00').delete()


endtime = datetime.datetime.now()
print((endtime - starttime).seconds)

# Create your tests here.
from utils.data_parser import parse_malfunction_data_xlsx, delete_former_data
import datetime
from report.models import MalfunctionData

# /Users/silenthz/Desktop/故障单样例数据.xls
# 2018-01-11 10:48:42

starttime = datetime.datetime.now()
delete_former_data(2018, 1)
parse_malfunction_data_xlsx('/Users/silenthz/Desktop/数据可视化项目/数据清单/清单.xlsx', 0)


endtime = datetime.datetime.now()
print((endtime - starttime).seconds)

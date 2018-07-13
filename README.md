# DataVisualization
###### Django with Echarts Data Visualization
切换至项目目录：
>cd DataEcharts

在新建虚拟环境下,Python3.6
更新pip:
>pip install --upgrade pip

安装依赖包：
>pip install -r requirements.txt

修改settings.py中的数据库连接配置（电脑预先安装好MySQL 5.7.2）

同步数据库表：
删除report/migrations/0001_initial.py

>python manage.py makemigrations

>python manage.py migrate

使用doc/sql下的文件导入地市数据

修改test.py中的文件路径，报表数据在群里下载

导入数据：
>python manage.py test

启动Django服务器：
>python manage.py runserver

浏览网页:
>访问 <http://127.0.0.1:8000/>
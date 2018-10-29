import re


def fetch_4G(title):
    if title.__contains__("—eNodeB—"):
        pattern = re.compile(r'(.*基站断站：?|.*小区退服：|【VIP站点】)?(.*?)—eNodeB—(.*)')
        res = re.search(pattern, title)
        if res:
            ne = res.group(2)
            return ne
    elif title.__contains__("—BTS—"):
        pattern = re.compile(r'(.*基站断站：|.*小区退服：|【VIP站点】)?(.*?)—BTS—(.*)')
        res = re.search(pattern, title)
        if res:
            ne = res.group(2)
            return ne
    elif title.__contains__("RCU"):
        pattern = re.compile(r'(.*RCU故障：)?(.*)')
        res = re.search(pattern, title)
        if res:
            ne = res.group(2)
            return ne
    else:
        return ""


# 直放站故障
def fetch_RPT(title):
    pass
    pattern = re.compile(r'(.*：)?(.*)(—RPT—)(.*)')
    ne = re.search(pattern, title)
    if ne:
        return ne.group(2)
    else:
        return ""


def fetch_CDMA(title):
    pattern = re.compile(r'(.*：)?(.*?)(—\w*—)(.*)')
    ne = re.search(pattern, title)
    if ne:
        return ne.group(2)
    else:
        pattern = re.compile(r'(.*：)?(.*)')
        ne = re.search(pattern, title)
        if ne:
            return ne.group(2)
        return ''


# 传输专业故障
"""
category___contains=  本地传输 本地光缆
qs = MalfunctionData.objects.filter(originProfession='传输', malfunctionSource='集中告警系统报故障')
"""


def fetch_TransmissionNetwork(title):
    if title.__contains__("Ne="):
        pattern = re.compile(r'(.*Ne=|.*: )(.*?)(/|管理盘通信中断|[A-Z]*?_COMMU_BREAK|【.*|$)', re.I)
        ne = re.search(pattern, title)
        if ne:
            return ne.group(2).strip()
        else:
            return ''
    elif title.__contains__("板卡故障"):
        pattern = re.compile(r'(.*: )(.*?)/')
        ne = re.search(pattern, title)
        if ne:
            return ne.group(2).strip()
        else:
            return ''

    else:
        pattern = re.compile(r'(.*光缆段=|.*段落=)(.*)')
        ne = re.search(pattern, title)
        if ne:
            return ne.group(2)
        return ''


# 光网络专业故障
"""
qs = MalfunctionData.objects.filter(originProfession='光网络', malfunctionSource='集中告警系统报故障')
"""


def fetch_OpticalNetwork(title):
    pattern = re.compile(r'(.*Ne=)(.*?)(【.*|$)')
    ne = re.search(pattern, title)
    if ne:
        return ne.group(2)
    return ''


# 交换专业故障
"""
qs = MalfunctionData.objects.filter(Q(category__contains='交换接入网') | Q(category__contains='AG'), malfunctionSource='集中告警系统报故障')
"""


def fetch_SwitchNetwork(title):
    if title.__contains__('Ne=') and not title.__contains__('网元号'):
        pattern = re.compile(r'(.*Ne=)(.*?)/')
        ne = re.search(pattern, title)
        if ne:
            return ne.group(2)
        return ''
    elif title.__contains__('Office='):
        pattern = re.compile(r'(.*Office=)(.*?)/')
        ne = re.search(pattern, title)
        if ne:
            return ne.group(2)
        return ''
    elif title.__contains__('板卡故障'):
        pattern = re.compile(r'(.*?:)(.*?):.*')
        ne = re.search(pattern, title)
        if ne:
            return ne.group(2)
        return ''


# 动力故障
def fetch_Dynamic(title):
    if title.__contains__("广东电信动环综合网管"):
        pattern = re.compile(r'(.*/Station=)(.*?)/System=')
    elif title.__contains__("广州科技动力网管"):
        pattern = re.compile(r'(.*Station=)(.*?)(.TT)')
    elif title.__contains__('Station='):
        if title.__contains__('Ne=') or title.__contains__('Group=') or title.__contains__('Equipment=') or title.__contains__('Observation='):
            pattern = re.compile(r'(.*Station=|.*Office=)(.*?)/')
        elif title.__contains__('采集设备'):
            if title.__contains__('《采集设备》《采集设备》'):
                pattern = re.compile(r'(.*Station=)(.*?《采集设备》)《采集设备》:')
            else:
                pattern = re.compile(r'(.*Station=)(.*?采集设备.*?)(通信状态|与)')

        else:
            #                            1        3     4      5      6 7        8
            pattern = re.compile(r'(.*Station=)((.*?)-(.*?):|(.*?)\s|(.*)温度|(.*?):)|((.*)与)')
            rs = re.search(pattern, title)
            if rs.group(3) and rs.group(4):
                repeat_str = rs.group(4)
                ne = rs.group(2)[:int(-len(repeat_str) / 2 - 1)]
                return ne
            for i in range(0, 9):
                if rs.group(9 - i):
                    # print(i, rs.group(i))
                    return rs.group(9 - i)
    elif title.__contains__('市电停电'):
        pattern = re.compile(r'(.*市电停电: )(.*)')
    else:
        pattern = re.compile(r'(.*/Office=)(.*?/)')
    ne = re.search(pattern, title)
    if ne:
        return ne.group(2)
    else:
        return ''


def fetch_DataNetwork(title):
    pattern = re.compile(r'(.*Ne=)(.*?)(/|SW断网故障|$)')
    ne = re.search(pattern, title)
    if ne:
        return ne.group(2)
    else:
        return ''


# /PowerSystem=广州科技动力网管/Station=沙溪IDC一期(-1F、1F、3F)/Ne=IDC/Group=动环监控/TT-CC=998-120线路检测(一层高压2系统)

# /Ems=东莞爱默生电源专业网管/Station=石鼓七D-综合机房环境综合机房环境:综合机房1号温度::温度过高
# /Ems=江门爱默生电源/Station=恩平江洲局(C类)-《采集设备》OCE-10通信状态异常
# /Ems=东莞爱默生电源专业网管/Station=城区端局A-《采集设备》《采集设备》:三楼4#NetSure801系统屏通信状态::异常

# /Ems=茂名温创动力网管/Station=采集设备-主机105(信宜接入网)与中心通讯状态告警 group8
# /Ems=中山艾默生电源专业网管/Station=小榄九洲基接入点_环境 温度温度过高  group5
# /Ems=东莞爱默生电源专业网管/Station=樟洋C-MDF架MDF架:MDF告警：配线架强电告警::告警 group3\4
# /Ems=江门爱默生电源/Station=台山环市北-电力室环境量二楼温度过高   group6
# /Ems=东莞爱默生电源专业网管/Station=复制服务器(IDCSS):::与中心通讯状态告警

# title = '小区退服：电白茂港南海局_F21—eNodeB—B(3条告警(含网管压缩次数)，派单实际压缩3条告警)'
# # fetch_Dynamic(title)
#
# pattern = re.compile(r'(.*基站断站：?|.*小区退服：|【VIP站点】)?(.*?)—eNodeB—(.*)')
# ne = re.search(pattern, title)
# print(ne.groups())


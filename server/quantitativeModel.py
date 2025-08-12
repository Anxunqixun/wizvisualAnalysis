from os import times_result

import fromServerRemoteMysqlGetInfo as datasources#导入数据获取文件
import datetime
import config as configpy
def processData(d):
    QuantificationData=[]#原始待量化数据
    for a in d:#从getData中获取数据
        c,cn=0,[]
        if a["attachInfo"]:
            for m in a["attachInfo"]:
                # print(m["name"],m["size"])
                cn.append([m["name"],m["size"]])
                c+=m["size"]
        # print(a["name"],a["path"],a["creatDate"],a["wordCount"],a["phoCounut"],len(a["attachInfo"]),c,cn)
        QuantificationData.append([a["name"],a["path"],a["creatDate"],a["wordCount"],a["phoCounut"],len(a["attachInfo"]),c,cn])
    return QuantificationData
def getData():
    db_config = configpy.db_config
    wiz_config = configpy.wiz_config
    # db_config = {
    #     'host': '110.x0.xx.x3',
    #     'database': 'wizksent',
    #     'user': 'root',
    #     'password': 'aI9DCyNpEKWe9pn5',
    #     'port': 330x
    # }
    # wiz_config = {
    #     'server': 'http://110.x0.x.x3:xxxx',
    #     'author': 'xx@xxxx',
    #     'username': 'xx@xxxx',
    #     'password': 'xxxx',
    # }
    wiz = datasources.WizServer(db_config, wiz_config)
    # wiz.show()
    wiz.connectDatabase()
    wiz.sizeCorrect()  # 修正录音数据大小异常
    return processData(wiz.returnInfo())#处理数据为量化参数
def getTimeBonusEnhanced(dt):
    """
    :param dt: datetime.datetime对象
    :param time_rules: 时间规则列表，格式示例:
        [
            ((23, 0), (3, 0), 1.2),  # 23:00-03:00 → 1.2
            ((8, 0), (9, 0), 1.1)     # 08:00-09:00 → 1.1
        ]
    :return: 加成系数
    """
    if not isinstance(dt, datetime.datetime):
        return 1.0
    time_rules = configpy.time_rules

    # time_rules = [
    #         ((22, 0), (3, 0), 1.2),
    #         ((8, 0), (9, 0), 1.1)
    #     ]

    hour, minute = dt.hour, dt.minute

    for (start_h, start_m), (end_h, end_m), bonus in time_rules:
        # 处理跨天时间段 (如23:00-03:00)
        if start_h > end_h:
            if (hour > start_h or hour < end_h) or \
                    (hour == start_h and minute >= start_m) or \
                    (hour == end_h and minute < end_m):
                return bonus
        else:
            if (hour > start_h and hour < end_h) or \
                    (hour == start_h and minute >= start_m) or \
                    (hour == end_h and minute < end_m):
                return bonus

    return 1.0
def getPathValueEnhanced(path):
    config = configpy.getPathValueEnhancedconfig
    # config={
    #     "/My Journals/": 1.2,
    #     "/一轮/": 1.1,
    #     "/My Notes/": 1.4
    # }
    if path in config:
        return config[path]
    matched_paths = [p for p in config.keys() if path.startswith(p)]
    if matched_paths:
        longest_match = max(matched_paths, key=len)
        return config[longest_match]
    return 1
def quantification(d):
    #d=[name,path,creatDate,wordCount,phoCounut,attachCount,attachSize,attachSizeInfo]
    #量化参数： name,path,creatDate,wordCount,phoCounut,attachCount,attachSize,attachSizeInfo
    out = []
    for a in d:
        print(a)
        pde = getPathValueEnhanced(a[1]) + getTimeBonusEnhanced(a[2]) - 1  # 路径和日期总加成
        config = configpy.quantificationconfig
        # config = {  # 参数映射值
        #     "word": 0.01,
        #     "pho": 2,
        #     "attach": 3,
        # }
        wordMark = round(config['word'] * a[3], 5)
        phoMark = config['pho'] * a[4]
        attachMark = config['attach'] * a[5]
        allMark = round((wordMark + phoMark + attachMark) * pde, 3)
        out.append([a[0], wordMark, phoMark, attachMark, allMark])
        print(f"wordMark: {wordMark} phoMark: {phoMark} attachMark: {attachMark} allMark: {allMark}")
    # print(out)
    return out
def getQMData():
    QuantificationData=getData()#获取数据
    return quantification(QuantificationData)#处理量化数据
if __name__ == '__main__':
    print(getQMData())
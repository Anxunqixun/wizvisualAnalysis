time_rules = [ # 时间段加成列表
    ((22, 0), (3, 0), 1.2), # 22:00-3:00 加成为1.2倍分数
    ((8, 0), (9, 0), 1.1)
]
getPathValueEnhancedconfig={ # 路径加成字典
    "/My Journals/": 1.2, # 只要是路径为/My Journals/都是1.2倍分数加成
    "/My Notes/": 1.4
}
quantificationconfig = { # 参考值分值参数
    "word": 0.01, # 一个字的分数
    "pho": 2, # 一个图片的分数
    "attach": 3, #一个附件的分数
}
db_config = {
    'host': '110.40.44.43', # 主机地址
    'database': 'wizksent', # 固定名称
    'user': 'root', # 固定用户
    'password': 'aI9DCyNpEKWe9pn5', # 固定root密码
    'port': 3301 # 你开发的端口
}
wiz_config = {
    'server': 'http://110.40.44.43:9251', # web端地址
    'author': '2113365920@qq.com', # 筛选的作者
    'username': '2113365920@qq.com', #web登录用户名
    'password': '111111', # web登录密码
}
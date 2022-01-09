import pyswan

# 梁山108好汉！
print(pyswan.digitize("梁山一百零八好汉！"))

# 今天是周7
print(pyswan.digitize("今天是周日"))

# TODO
pyswan.digitize("明天是劳动节")

# [{'dim': 'time', 'body': '12点30分', 'start': 0, 'end': 0, 'value': '2022-01-06 12:30:51 +08:00'}]
print(pyswan.parse('十二点三十分', dim=['time', 'number']))

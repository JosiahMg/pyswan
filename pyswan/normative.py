"""
预处理句子, 去除多余的空格 tab等
如:
过年 -> 春节
大年初一 -> 春节

"""
from pyswan.constants import normative_tab
import regex as re
from pyswan.message import Message


def normative(message):
    """
    标准化句子
    :param target: 待归一化的句子
    :return: target
    """
    for key, value in normative_tab.items():
        pattern = re.compile(key)
        match = pattern.finditer(message.target)
        for m in match:
            message.insert(start=m.start(), end=m.end(), body=m.group(), value=value, pattern=pattern)
        message.target = pattern.sub(value, message.target)
    return message


if __name__ == '__main__':
    from pprint import pprint

    target = ' 今天是51劳动节  '
    message = Message(target)
    message = normative(message)
    pprint(message.target)




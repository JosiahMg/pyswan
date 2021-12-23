"""
预处理句子, 去除多余的空格 tab等
如:
过年 -> 春节
大年初一 -> 春节

"""
from pyswan.constants import normative_tab
import regex as re


def normative(target):
    """
    标准化句子
    :param target: 待归一化的句子
    :return: target
    """
    for key, value in normative_tab.items():
        pattern = re.compile(key)
        target = pattern.sub(value, target)
    return target


if __name__ == '__main__':
    from pprint import pprint

    target = ' 今天是51劳动节以及51劳动节  '
    target = normative(target)
    pprint(target)




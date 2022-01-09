from pyswan.numeral import ExtractNumeral
from pyswan.gen_time import GenDatetime
from pyswan.gen_number import GenNumber

def digitize(target):
    return ExtractNumeral.digitize(target).target


def parse(target, dim):
    """
    :param target: input data
    :param dim:
    :return:
    """
    supported = ['time', 'number']
    to_support = ['temperature', 'ordinal', 'distance', 'volume', 'amount-of-money', 'duration', 'email', 'url', 'phone-number']
    if not isinstance(dim, list):
        print('dim must be of type list')
        return []

    if len(dim) == 0:
        return []


    # 数字化处理 中文数字 -> 阿拉伯数字
    message = ExtractNumeral.digitize(target)
    for d in dim:
        if d not in supported:
            continue
        if d == 'time':
            message = GenDatetime().parse(message)
        if d == 'number':
            message = GenNumber().parse(message)

    res = message.get_extracts(filter=['pattern'])
    return res


if __name__ == '__main__':
    from pprint import pprint

    pprint(digitize('梁山一百零八好汉'))
    pprint(parse('现在是十二月13日12点50分', dim=['time', 'number']))




from pyswan.numeral import ExtractNumeral
from pyswan.extract_time import GenDatetime
from pyswan.extract_number import GenNumber
from pyswan.extract_math_equation import GenMathEquation
from pyswan.extract_cpca import GenPlace


def digitize(target):
    return ExtractNumeral.digitize(target).target


def parse(target, dim):
    """
    :param target: input data
    :param dim:
    :return:
    """
    supported = ['time', 'number', 'equation', 'place']
    to_support = ['temperature', 'ordinal', 'distance', 'volume',
                  'amount-of-money', 'duration', 'email', 'url', 'phone-number']
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
        if d == 'equation':
            message = GenMathEquation().parse(message)
        if d == 'place':
            message = GenPlace().parse(message)

    res = message.get_extracts(filter=['pattern'])
    return res


if __name__ == '__main__':
    from pprint import pprint

    pprint(digitize('梁山一百零八好汉'))
    pprint(parse('现在是十二月13日12点50分', dim=['time', 'number']))
    pprint(parse('六加十三除以2再乘八等于多少', dim=['equation']))
    pprint(parse('徐汇区虹漕路461号五十八号楼五楼', dim=['place']))

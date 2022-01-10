"""
提取目标中的数学公式
"""
import regex as re
from pyswan.message import Message
from pyswan.numeral import ExtractNumeral


class GenMathEquation:
    def __init__(self):
        self.replace_tab = {
            '+': r'(?<=\d+)(加|加上|再加|再加上|在加|在加上)(?=\d+)',
            '-': r'(?<=\d+)(减|减去|减上|再减|再减去|再减上|在减|在减去|在减上)(?=\d+)',
            '*': r'(?<=\d+)(乘|乘以|乘上|再乘|再乘去|再乘以|在乘|在乘上|在乘上)(?=\d+)',
            '/': r'(?<=\d+)(除|除以|除上|再除|再除以|再除上|在除|在除以|在除上)(?=\d+)',
            '.': r'(?<=\d+)(点)(?=\d+(?!分))',
        }

    def replace_operator(self, message):   # 匹配运算符并替换
        for key, pattern in self.replace_tab.items():
            pattern = re.compile(pattern)
            match = pattern.finditer(message.target)
            for m in match:
                message.insert(start=m.start(), end=m.end(), body=m.group(), value=key, pattern=pattern)
                message.target = pattern.sub(key, message.target, 1)
        return message

    def parse(self, message):
        message = self.replace_operator(message)
        pattern = re.compile(r'(?<![+-/*])\d+[\d+\-*/.]*\d+(?![+-/*])')  # 匹配数学公式
        outputs = pattern.finditer(message.target)
        for output in outputs:
            ele = {}
            ele['type'] = 'equation'
            ele['start'] = output.start()
            ele['end'] = output.end()
            ele['value'] = output.group()
            message.extracts.append(ele)
        return message


if __name__ == '__main__':
    num_target = ExtractNumeral.digitize('一加上20乘以三除6加八-8点3等于多少')
    print(GenMathEquation().parse(num_target).get_extracts())
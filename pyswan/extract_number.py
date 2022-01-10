"""
提取目标中的数字
"""
import regex as re
from pyswan.message import Message
from pyswan.numeral import ExtractNumeral


class GenNumber:
    def __init__(self):
        self.pattern = re.compile(r'\d+')

    def parse(self, message):
        outputs = self.pattern.finditer(message.target)
        for output in outputs:
            ele = {}
            ele['type'] = 'number'
            ele['start'] = output.start()
            ele['end'] = output.end()
            ele['value'] = output.group()
            message.extracts.append(ele)
        return message


if __name__ == '__main__':
    num_target = ExtractNumeral.digitize('梁山一百零八好汉')
    print(GenNumber().parse(num_target).get_extracts())
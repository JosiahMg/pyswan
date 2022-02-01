import regex as re
from pyswan.constants import zh2arab_tab
from pyswan.message import Message


class ExtractNumeral:
    """
    将中文中的数字转换成阿拉伯数字， 如:
    两百零三万五千九 -> 2035900
    周日 -> 周7
    """
    @staticmethod
    def simple_zh2arab(message):
        '''
        简单的替换中文的数字为阿拉伯数字,如:
        十二万八千零五 -> 十2万8千05
        :param target: 待转换的输入
        :return:
        '''
        # 处理普通的数字
        pattern = re.compile("[零一二两三四五六七八九]")
        match = pattern.finditer(message.target)
        for m in match:
            value = str(zh2arab_tab.get(m.group()))
            message.insert(start=m.start(), end=m.end(),
                           body=m.group(), value=value, pattern=pattern)
            message.target = pattern.sub(value, message.target, 1)

        # 处理周末 周日 周天
        pattern = re.compile("(?<=(周|星期))[末日天]")
        match = pattern.finditer(message.target)
        for m in match:
            value = str(zh2arab_tab.get(m.group()))
            message.insert(start=m.span()[0], end=m.end(
            ), body=m.group(), value=value, pattern=pattern)
            message.target = pattern.sub(value, message.target, 1)

        return message

    @staticmethod
    def __single_hundreds_digit_arab(message):
        '''
        处理如: 1百2 -> 120
        :param target:
        :return:
        '''
        pattern = re.compile("[1-9]百[1-9](?!十)")
        match = pattern.finditer(message.target)
        for m in match:
            group = m.group()
            s = group.split("百")
            s = list(filter(None, s))
            num = 0
            if len(s) == 2:
                num += int(s[0]) * 100 + int(s[1]) * 10
            message.insert(start=m.span()[0], end=m.end(
            ), body=m.group(), value=str(num), pattern=pattern)
            message.target = pattern.sub(str(num), message.target, 1)

        return message

    @staticmethod
    def __single_thousands_digit_arab(message):
        '''
        处理如: 1千2 -> 1200
        :param target:
        :return:
        '''
        pattern = re.compile("[1-9]千[1-9](?!(百|十))")
        match = pattern.finditer(message.target)
        for m in match:
            group = m.group()
            s = group.split("千")
            s = list(filter(None, s))
            num = 0
            if len(s) == 2:
                num += int(s[0]) * 1000 + int(s[1]) * 100
            message.insert(start=m.start(), end=m.end(),
                           body=m.group(), value=str(num), pattern=pattern)
            message.target = pattern.sub(str(num), message.target, 1)

        return message

    @staticmethod
    def __single_ten_thousands_digit_arab(message):
        pattern = re.compile("[1-9]万[1-9](?!(千|百|十))")
        match = pattern.finditer(message.target)
        for m in match:
            group = m.group()
            s = group.split("万")
            s = list(filter(None, s))
            num = 0
            if len(s) == 2:
                num += int(s[0]) * 10000 + int(s[1]) * 1000
            message.insert(start=m.start(), end=m.end(),
                           body=m.group(), value=str(num), pattern=pattern)
            message.target = pattern.sub(str(num), message.target, 1)

        return message

    @staticmethod
    def __tens_digit_arab(message):
        '''
        需要simple_zh2arab处理后的数据
        处理十位数,如  十2 -> 12  3十5 -> 35
        :param target: 待转换的输入
        :return:
        '''
        pattern = re.compile("0?[0-9]?十[0-9]?")
        match = pattern.finditer(message.target)
        for m in match:
            group = m.group()
            s = group.split("十")
            num = 0
            if s[0] == '':
                num += 10
            else:
                num += int(s[0])*10
            if s[1]:
                num += int(s[1])
            message.insert(start=m.start(), end=m.end(),
                           body=m.group(), value=str(num), pattern=pattern)
            message.target = pattern.sub(str(num), message.target, 1)

        return message

    @staticmethod
    def __hundreds_digit_arab(message):
        '''
        需要simple_zh2arab和tens_digit_arab处理后的数据
        处理百位数,如  2百25
        :param target: 待转换的输入
        :return:
        '''
        pattern = re.compile("0?[1-9]百[0-9]?[0-9]?")
        match = pattern.finditer(message.target)
        for m in match:
            group = m.group()
            s = group.split("百")
            s = list(filter(None, s))
            num = 0
            if len(s) == 1:
                hundred = int(s[0])
                num += hundred * 100
            elif len(s) == 2:
                hundred = int(s[0])
                num += hundred * 100
                num += int(s[1])
            message.insert(start=m.start(), end=m.end(),
                           body=m.group(), value=str(num), pattern=pattern)
            message.target = pattern.sub(str(num), message.target, 1)

        return message

    @staticmethod
    def __thousands_digit_arab(message):
        pattern = re.compile("0?[1-9]千[0-9]?[0-9]?[0-9]?")
        match = pattern.finditer(message.target)
        for m in match:
            group = m.group()
            s = group.split("千")
            s = list(filter(None, s))
            num = 0
            if len(s) == 1:
                thousand = int(s[0])
                num += thousand * 1000
            elif len(s) == 2:
                thousand = int(s[0])
                num += thousand * 1000
                num += int(s[1])
            message.insert(start=m.start(), end=m.end(),
                           body=m.group(), value=str(num), pattern=pattern)
            message.target = pattern.sub(str(num), message.target, 1)
        return message

    @staticmethod
    def __ten_thousands_digit_arab(message):
        """
        thousands_digit_arab执行之后
        :param target:
        :return:
        """
        pattern = re.compile("[0-9]+万[0-9]?[0-9]?[0-9]?[0-9]?")
        match = pattern.finditer(message.target)
        for m in match:
            group = m.group()
            s = group.split("万")
            s = list(filter(None, s))
            num = 0
            if len(s) == 1:
                tenthousand = int(s[0])
                num += tenthousand * 10000
            elif len(s) == 2:
                tenthousand = int(s[0])
                num += tenthousand * 10000
                num += int(s[1])
            message.insert(start=m.start(), end=m.end(),
                           body=m.group(), value=str(num), pattern=pattern)
            message.target = pattern.sub(str(num), message.target, 1)
        return message

    @classmethod
    def digitize(cls, target):
        message = Message(target)
        message = cls.simple_zh2arab(message)  # 处理如"十二万八千零五 -> 十2万8千05"

        message = cls.__single_ten_thousands_digit_arab(message)  # 处理如"2万3"
        message = cls.__single_thousands_digit_arab(message)  # 处理如"2千3"
        message = cls.__single_hundreds_digit_arab(message)   # 处理如"2百3"

        message = cls.__tens_digit_arab(message)  # 处理如"2十3"
        message = cls.__hundreds_digit_arab(message)  # 处理 "5百35"
        message = cls.__thousands_digit_arab(message)  # 处理 "1千456"
        message = cls.__ten_thousands_digit_arab(message)  # 处理 "7万2337"
        return message


if __name__ == '__main__':
    res = ExtractNumeral.digitize('梁山一百零八好汉')
    print(res.target)

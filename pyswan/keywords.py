"""
粗略提取句子中有关时间的关键字
"""
import regex as re


class ExtractTimeKeywords:
    def __init__(self):
        self.pattern = self.read_regex_file()

    @staticmethod
    def read_regex_file():
        pattern_tab = []
        with open('dt_keywords_regex.txt', encoding='utf-8') as f:
            for line in f.readlines():
                pattern_tab.append(line.strip())

        pattern_str = "|".join(pattern_tab)

        return re.compile(pattern_str)

    def extract_time_keywords(self, target):
        keywords = []
        match = self.pattern.finditer(target)
        for m in match:
            keywords.append(m.group())
        return keywords


if __name__ == '__main__':
    extracter = ExtractTimeKeywords()
    print(extracter.extract_time_keywords('今天晚上有时间吗？10年之后我不认识你'))
    print(extracter.extract_time_keywords('21世纪'))
    print(extracter.extract_time_keywords('春节了'))
    print(extracter.extract_time_keywords('新年快乐'))





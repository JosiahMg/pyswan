"""
根据提取的时间关键字生成时间 format datetime (string)
  - timepoint: 时间点   21年2月8日  今天  明天   今天和明天
  - timespan: 时间区间, 如未来3天  持续2年  从今天到明天
  - timescale: 时间单位, 如 2分钟  3年
"""
import regex as re
import arrow
import pickle
import os
from pyswan.numeral import ExtractNumeral
from pyswan.normative import normative


class ExtractDatetime:
    def __init__(self, time_keyword):
        # 用于存放 年月日时分秒
        self.arrow_time = arrow.now()
        # 用于标记是否已经填充了年月日时分秒  0: 否   1: 是
        self.flag_datetime = [0, 0, 0, 0, 0, 0]
        self.target = time_keyword
        self.patterns = []
        self.generate_time()

    def __check_flag_datetime(self, params):
        """
        如果self.flag_datetime对应的参数全部为1 则返回 true 否则返回 false
        :param params:
        :return:
        """
        lookups = {"year": 0, "month": 1, "day": 2, "hour": 3, "minute": 4, "second": 5}
        if isinstance(params, list):
            for value in params:
                if self.flag_datetime[lookups[value]] == 0:
                    return False
        else:
            if self.flag_datetime[lookups[params]] == 0:
                return False

        return True

    def __set_flag_datetime(self, params):
        '''
        用于设置 self.flag_datetime 的值
        :param params:
        :return:
        '''
        lookups = {"year": 0, "month": 1, "day": 2, "hour": 3, "minute": 4, "second": 5}
        if isinstance(params, list):
            for value in params:
                self.flag_datetime[lookups[value]] = 1
        else:
            self.flag_datetime[lookups[params]] = 1

    def __gen_ymd_fixed_time(self):
        """
        处理是给定的规定的年月日
        如: 2021-2-13  2021.2.13  2021/2/13
        """
        if self.__check_flag_datetime(['year', 'month', 'day']):
            return

        # 2021-12-21
        rule = r"(?<!\d)[0-9]?[0-9]?[0-9]{2}-(10|11|12|[1-9])-([1-9]|[0-3][0-9])(?!\d)"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            tmp_target = match.group()
            self.patterns.append({'pattern': pattern, 'match': tmp_target})
            tmp_parser = tmp_target.split("-")
            self.arrow_time = self.arrow_time.replace(year=int(tmp_parser[0]))
            self.arrow_time = self.arrow_time.replace(month=int(tmp_parser[1]))
            self.arrow_time = self.arrow_time.replace(day=int(tmp_parser[2]))
            self.__set_flag_datetime(['year', 'month', 'day'])

        # 2021/12/21
        rule = r"(?<!\d)[0-9]?[0-9]?[0-9]{2}/(10|11|12|[1-9])/([0-3][0-9]|[1-9])(?!\d)"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            tmp_target = match.group()
            self.patterns.append({'pattern': pattern, 'match': tmp_target})
            tmp_parser = tmp_target.split("/")
            self.arrow_time = self.arrow_time.replace(year=int(tmp_parser[0]))
            self.arrow_time = self.arrow_time.replace(month=int(tmp_parser[1]))
            self.arrow_time = self.arrow_time.replace(day=int(tmp_parser[2]))
            self.__set_flag_datetime(['year', 'month', 'day'])

        # 2021.12.21
        rule = r"(?<!\d)[0-9]?[0-9]?[0-9]{2}\.(10|11|12|[1-9])\.([0-3][0-9]|[1-9])(?!\d)"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            tmp_target = match.group()
            self.patterns.append({'pattern': pattern, 'match': tmp_target})
            tmp_parser = tmp_target.split(".")
            self.arrow_time = self.arrow_time.replace(year=int(tmp_parser[0]))
            self.arrow_time = self.arrow_time.replace(month=int(tmp_parser[1]))
            self.arrow_time = self.arrow_time.replace(day=int(tmp_parser[2]))
            self.__set_flag_datetime(['year', 'month', 'day'])

    def __gen_md_fixed_time(self):

        if self.__check_flag_datetime(['month', 'day']):
            return
        # 处理缺少日字的 如: 3月2
        rule = r"(?<!\d)(10|11|12|[1-9])(月|\.|-)([0-3][0-9]|[1-9])(?![\d日])"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            match_str = match.group()
            self.patterns.append({'pattern': pattern, 'match': match_str})
            p = re.compile(r"(月|\.|-)")
            m = p.search(match_str)
            if match is not None:
                split_index = m.start()
                month = match_str[0: split_index]
                day = match_str[split_index + 1:]
                self.arrow_time = self.arrow_time.replace(month=int(month))
                self.arrow_time = self.arrow_time.replace(day=int(day))
                self.__set_flag_datetime(['month', 'day'])

    def __gen_ymd_relative_time(self):
        """
        处理是给定可以确定的相对日子
        :param target:
        :return:
        """
        if self.__check_flag_datetime(['year', 'month', 'day']):
            return

        relative_dt = {
            r'大前年': {"arrow_params": {"years": -3}, "flag_params": ["year"]},
            r'前年': {"arrow_params": {"years": -2}, "flag_params": ["year"]},
            r'去年': {"arrow_params": {"years": -1}, "flag_params": ["year"]},
            r'今年': {"arrow_params": {"years": 0}, "flag_params": ["year"]},
            r'明年': {"arrow_params": {"years": +1}, "flag_params": ["year"]},
            r'后年': {"arrow_params": {"years": +2}, "flag_params": ["year"]},
            r'大后年': {"arrow_params": {"years": +3}, "flag_params": ["year"]},
            r'上上个?月': {"arrow_params": {"months": -2}, "flag_params": ["year", "month"]},
            r'上个?月': {"arrow_params": {"months": -1}, "flag_params": ["year", "month"]},
            r"(本|这个)月": {"arrow_params": {"months": 0}, "flag_params": ["year", "month"]},
            r'下个?月': {"arrow_params": {"months": +1}, "flag_params": ["year", "month"]},
            r'下下个?月': {"arrow_params": {"months": +2}, "flag_params": ["year", "month"]},
            r'大前天': {"arrow_params": {"days": -3}, "flag_params": ["year", "month", "day"]},
            r'前天': {"arrow_params": {"days": -2}, "flag_params": ["year", "month", "day"]},
            r'昨天': {"arrow_params": {"days": -1}, "flag_params": ["year", "month", "day"]},
            r'今天': {"arrow_params": {"days": 0}, "flag_params": ["year", "month", "day"]},
            r'明天': {"arrow_params": {"days": +1}, "flag_params": ["year", "month", "day"]},
            r'后天': {"arrow_params": {"days": +2}, "flag_params": ["year", "month", "day"]},
            r'大后天': {"arrow_params": {"days": +3}, "flag_params": ["year", "month", "day"]},
            r'上上(周|星期)(?![1-7])': {"arrow_params": {"weeks": -2}, "flag_params": ["year", "month", "day"]},
            r'上(周|星期)(?![1-7])': {"arrow_params": {"weeks": -1}, "flag_params": ["year", "month", "day"]},
            r'(这|本)(周|星期)(?![1-7])': {"arrow_params": {"weeks": 0}, "flag_params": ["year", "month", "day"]},
            r'下(周|星期)(?![1-7])': {"arrow_params": {"weeks": +1}, "flag_params": ["year", "month", "day"]},
            r'下下(周|星期)(?![1-7])': {"arrow_params": {"weeks": +2}, "flag_params": ["year", "month", "day"]},
        }
        for rule, value in relative_dt.items():
            pattern = re.compile(rule)
            match = pattern.search(self.target)
            if match is not None:
                self.patterns.append({'pattern': pattern, 'match': match.group()})
                self.arrow_time = self.arrow_time.shift(**value['arrow_params'])
                self.__set_flag_datetime(value['flag_params'])

    def __gen_ymd_fixed_relative_time(self):
        """
        处理非固定的时间, 如 两年前  五年前  三天后  两小时之后  三分钟之后   50秒之后 etc
        :return: 
        """
        if self.__check_flag_datetime(["year", "month", "day", "hour", "minute", "second"]):
            return
        # -------------------- 秒 ------------------------
        pattern = re.compile(r'\d+(?=秒钟?(以前|前|之前))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(seconds=-int(match.group()))
            self.__set_flag_datetime(["year", "month", "day", "hour", "minute", "second"])

        if self.__check_flag_datetime(["year", "month", "day", "hour", "minute", "second"]):
            return
        pattern = re.compile(r'\d+(?=秒钟?(以后|后|之后|过后))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(seconds=int(match.group()))
            self.__set_flag_datetime(["year", "month", "day", "hour", "minute", "second"])

        if self.__check_flag_datetime(["year", "month", "day", "hour", "minute", "second"]):
            return
        # -------------------- 分 ------------------------
        pattern = re.compile(r'\d+(?=分钟(以前|前|之前))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(minutes=-int(match.group()))
            self.__set_flag_datetime(["year", "month", "day", "hour", "minute", "second"])

        if self.__check_flag_datetime(["year", "month", "day", "hour", "minute", "second"]):
            return
        pattern = re.compile(r'\d+(?=分钟(以后|后|之后|过后))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(minutes=int(match.group()))
            self.__set_flag_datetime(["year", "month", "day", "hour", "minute", "second"])

        if self.__check_flag_datetime(["year", "month", "day", "hour", "minute"]):
            return
        # -------------------- 时 ------------------------
        pattern = re.compile(r'\d+(?=个?小时(以前|前|之前))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(hours=-int(match.group()))
            self.__set_flag_datetime(["year", "month", "day", 'hour', "minute"])

        if self.__check_flag_datetime(["year", "month", "day", "hour", "minute"]):
            return
        pattern = re.compile(r'\d+(?=个?小时(以后|后|之后|过后))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(hours=int(match.group()))
            self.__set_flag_datetime(["year", "month", "day", 'hour', "minute"])

        # -------------------- 天 ------------------------
        if self.__check_flag_datetime(["year", "month", "day"]):
            return
        pattern = re.compile(r'\d+(?=天(以后|后|之后|过后))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(days=int(match.group()))
            self.__set_flag_datetime(["year", "month", "day"])

        if self.__check_flag_datetime(["year", "month", "day"]):
            return
        pattern = re.compile(r'\d+(?=天(以前|前|之前))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(days=-int(match.group()))
            self.__set_flag_datetime(["year", "month", "day"])

        # -------------------- 月 ------------------------
        if self.__check_flag_datetime(["year", "month", "day"]):
            return
        pattern = re.compile(r'\d+(?=个月(以后|后|之后|过后))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(months=int(match.group()))
            self.__set_flag_datetime(["year", "month", "day"])

        if self.__check_flag_datetime(["year", "month", "day"]):
            return
        pattern = re.compile(r'\d+(?=个月(以前|前|之前))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(months=-int(match.group()))
            self.__set_flag_datetime(["year", "month", "day"])

        # -------------------- 年 ------------------------
        if self.__check_flag_datetime(["year", "month", "day"]):
            return
        pattern = re.compile(r'\d+(?=年(以后|后|之后|过后))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(years=int(match.group()))
            self.__set_flag_datetime(["year", "month", "day"])

        if self.__check_flag_datetime(["year", "month", "day"]):
            return
        pattern = re.compile(r'\d+(?=年(以前|前|之前))')
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.shift(years=-int(match.group()))
            self.__set_flag_datetime(["year", "month", "day"])

    def __gen_year_fixed_time(self):
        """
        处理固定的年如: 2012年  1000年 etc.
        """
        if self.__check_flag_datetime('year'):
            return

        rule = r"\d+(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time.replace(year=int(match.group()))
            self.__set_flag_datetime('year')

    def __gen_month_fixed_time(self):
        """
        处理固定的月如: 12月 1月 etc.
        """
        if self.__check_flag_datetime('month'):
            return
        rule = r"(10|11|12|[1-9])(?=月)"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(month=int(match.group()))
            self.__set_flag_datetime('month')

    def __gen_day_fixed_time(self):
        """
        处理固定的日如 3日/号
        """
        if self.__check_flag_datetime('day'):
            return
        rule = r"((?<!\d))([0-3][0-9]|[1-9])(?=(日|号))"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(day=int(match.group()))
            self.__set_flag_datetime('day')

    def __gen_hms_fixed_time(self):
        """
        处理如： 晚上12:12:12 晚上12:12
        """
        if self.__check_flag_datetime(['hour', 'minute', 'second']):
            return
        rule = u"(晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后)([0-2]?[0-9])点钟?[0-5]?[0-9]分[0-5]?[0-9]秒"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            # --------- hour ---------
            rule_hour = '([0-2]?[0-9])(?=点钟?)'
            pattern = re.compile(rule_hour)
            match = pattern.search(self.target)
            target = match.group()
            if 0 <= int(target) <= 11:
                target = int(target) + 12
            self.arrow_time = self.arrow_time.replace(hour=target)
            # --------- minute ---------
            rule_minute = '[0-5]?[0-9](?=分)'
            pattern = re.compile(rule_minute)
            match = pattern.search(self.target)
            target = match.group()
            self.arrow_time = self.arrow_time.replace(minute=int(target))
            # --------- second ---------
            rule_second = '[0-5]?[0-9](?=秒)'
            pattern = re.compile(rule_second)
            match = pattern.search(self.target)
            target = match.group()
            self.arrow_time = self.arrow_time.replace(second=int(target))
            self.__set_flag_datetime(['hour', 'minute', 'second'])

        if self.__check_flag_datetime(['hour', 'minute']):
            return
        rule = u"(晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后)([0-2]?[0-9])点钟?[0-5]?[0-9]分"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            # --------- hour ---------
            rule_hour = '([0-2]?[0-9])(?=点钟?)'
            pattern = re.compile(rule_hour)
            match = pattern.search(self.target)
            target = match.group()
            if 0 <= int(target) <= 11:
                target = int(target) + 12
            self.arrow_time = self.arrow_time.replace(hour=target)
            # --------- minute ---------
            rule_minute = '[0-5]?[0-9](?=分)'
            pattern = re.compile(rule_minute)
            match = pattern.search(self.target)
            target = match.group()
            self.arrow_time = self.arrow_time.replace(minute=int(target))
            self.__set_flag_datetime(['hour', 'minute'])

        if self.__check_flag_datetime(['hour']):
            return
        rule = u"(晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后)([0-2]?[0-9])点钟?"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            # --------- hour ---------
            rule_hour = '([0-2]?[0-9])(?=点钟?)'
            pattern = re.compile(rule_hour)
            match = pattern.search(self.target)
            target = match.group()
            if 0 <= int(target) <= 11:
                target = int(target) + 12
            self.arrow_time = self.arrow_time.replace(hour=target)
            self.__set_flag_datetime(['hour'])

        if self.__check_flag_datetime(['hour', 'minute', 'second']):
            return
        rule = u"(晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后)(?<!(周|星期))([0-2]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            rule = '([0-2]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]'
            pattern = re.compile(rule)
            match = pattern.search(self.target)
            tmp_target = match.group()
            tmp_parser = tmp_target.split(":")
            if 0 <= int(tmp_parser[0]) <= 11:
                tmp_parser[0] = int(tmp_parser[0]) + 12
            self.arrow_time = self.arrow_time.replace(hour=tmp_parser[0])
            self.arrow_time = self.arrow_time.replace(minute=int(tmp_parser[1]))
            self.arrow_time = self.arrow_time.replace(second=int(tmp_parser[2]))
            self.__set_flag_datetime(['hour', 'minute', 'second'])

        if self.__check_flag_datetime(['hour', 'minute']):
            return
        rule = u"(晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后)(?<!(周|星期))([0-2]?[0-9]):[0-5]?[0-9]"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            rule = '([0-2]?[0-9]):[0-5]?[0-9]'
            pattern = re.compile(rule)
            match = pattern.search(self.target)
            tmp_target = match.group()
            tmp_parser = tmp_target.split(":")
            if 0 <= int(tmp_parser[0]) <= 11:
                tmp_parser[0] = int(tmp_parser[0]) + 12
            self.arrow_time = self.arrow_time.replace(hour=tmp_parser[0])
            self.arrow_time = self.arrow_time.replace(minute=int(tmp_parser[1]))
            self.arrow_time = self.arrow_time.replace(second=int(tmp_parser[2]))
            self.__set_flag_datetime(['hour', 'minute'])

        # 处理如： 12:12:12 12:12
        if self.__check_flag_datetime(['hour', 'minute', 'second']):
            return
        rule = u"(?<!(周|星期|晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后))([0-2]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            tmp_target = match.group()
            self.patterns.append({'pattern': pattern, 'match': tmp_target})
            tmp_parser = tmp_target.split(":")
            self.arrow_time = self.arrow_time.replace(hour=int(tmp_parser[0]))
            self.arrow_time = self.arrow_time.replace(minute=int(tmp_parser[1]))
            self.arrow_time = self.arrow_time.replace(second=int(tmp_parser[2]))
            self.__set_flag_datetime(['hour', 'minute', 'second'])

        if self.__check_flag_datetime(['hour', 'minute']):
            return
        rule = u"(?<!(周|星期|晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后))([0-2]?[0-9]):[0-5]?[0-9]"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            tmp_target = match.group()
            self.patterns.append({'pattern': pattern, 'match': tmp_target})
            tmp_parser = tmp_target.split(":")
            self.arrow_time = self.arrow_time.replace(hour=int(tmp_parser[0]))
            self.arrow_time = self.arrow_time.replace(minute=int(tmp_parser[1]))
            self.__set_flag_datetime(['hour', 'minute'])

    def __gen_hour_fixed_time(self):
        """
        处理小时是固定的，如 12点  12时
        :param target:
        :return:
        """
        if self.__check_flag_datetime('hour'):
            return
        rule = r"(?<!(周|星期))([0-2]?[0-9])(?=(点钟?|时))"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(hour=int(match.group()))
            self.__set_flag_datetime('hour')

        # 周三12点
        rule = r"(?<=(周|星期)[1-7])([0-2]?[0-9])(?=(点钟?|时))"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(hour=int(match.group()))
            self.__set_flag_datetime('hour')

    def __gen_minute_fixed_time(self):
        # 10分    2点10分   排除 2小时10
        if self.__check_flag_datetime('minute'):
            return
        rule = r"([0-9]+(?=分(?!钟)))|((?<=((?<!小)[点时]))[0-5]?[0-9](?!刻))"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(minute=int(match.group()))
            self.__set_flag_datetime('minute')

        # 点 1刻
        rule = r"(?<=[点时])[1一]刻(?!钟)"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(minute=15)
            self.__set_flag_datetime('minute')

        # 点半
        rule = u"(?<=[点时])半"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(minute=30)
            self.__set_flag_datetime('minute')

        # 点三刻
        rule = u"(?<=[点时])[3三]刻(?!钟)"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(minute=45)
            self.__set_flag_datetime('minute')

    def __gen_second_fixed_time(self):
        if self.__check_flag_datetime('second'):
            return
        rule = r"([0-9]+(?=秒))|((?<=分)[0-5]?[0-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.target)
        if match is not None:
            self.patterns.append({'pattern': pattern, 'match': match.group()})
            self.arrow_time = self.arrow_time.replace(second=int(match.group()))
            self.__set_flag_datetime('second')

    def __correct_datetime(self):
        if self.__check_flag_datetime('second'):
            self.arrow_time.replace(second=0)

        if self.__check_flag_datetime('minute'):
            self.arrow_time.replace(minute=0)

        if self.__check_flag_datetime('hour'):
            self.arrow_time.replace(hour=0)

        if not self.__check_flag_datetime('day'):
            self.arrow_time = self.arrow_time.replace(day=1)

        if not self.__check_flag_datetime('month'):
            self.arrow_time.replace(month=1)

        # if not self.__check_flag_datetime('year'):
        #     self.arrow_time.replace(year=0)

    def generate_time(self):
        self.__gen_ymd_fixed_time()
        self.__gen_md_fixed_time()
        self.__gen_ymd_relative_time()
        self.__gen_ymd_fixed_relative_time()
        self.__gen_year_fixed_time()
        self.__gen_month_fixed_time()
        self.__gen_day_fixed_time()
        self.__gen_hms_fixed_time()
        self.__gen_hour_fixed_time()
        self.__gen_minute_fixed_time()
        self.__gen_second_fixed_time()
        # self.__correct_datetime()

    def get_datetime(self):
        return self.arrow_time.format('YYYY-MM-DD HH:mm:ss')

    def get_patterns(self):
        return self.patterns


class GenDatetime:
    def __init__(self):
        self.pattern = self.load_keywords_pattern()

    # 加载提取时间关键信息的正则表达式
    def load_keywords_pattern(self):
        fpath = os.path.join(os.path.dirname(__file__), 'dt_keywords_regex.pkl')
        try:
            with open(fpath, 'rb') as f:
                pattern = pickle.load(f)
        except:
            with open(os.path.join(os.path.dirname(__file__), 'dt_keywords_regex.txt'), 'r', encoding="utf-8") as f:
                content = f.read()
            p = re.compile(content)
            with open(fpath, 'wb') as f:
                pickle.dump(p, f)
            with open(fpath, 'rb') as f:
                pattern = pickle.load(f)
        return pattern

    def extract_datetime_keywords(self, message):
        startline = -1
        endline = -1
        nums = 0
        time_keywords = []
        match = self.pattern.finditer(message.target)
        for m in match:
            message.insert(start=m.start(), end=m.end(), body=m.group(), value=None, pattern=self.pattern)
            startline = m.start()
            if startline == endline:
                nums -= 1
                time_keywords[nums] = time_keywords[nums] + m.group()
            else:
                time_keywords.append(m.group())
            endline = m.end()
            nums += 1
        message.time_keywords = time_keywords
        return message

    def parse(self, message):
        # # 中文数字 -> 阿拉伯数字
        # num_target = ExtractNumeral.digitize(target)
        # 去除句子中的空格 tab 多义词归一化
        norm_target = normative(message)
        # 提取时间相关的关键字
        message_time_kws = self.extract_datetime_keywords(norm_target)
        dt_kws = message_time_kws.time_keywords
        if len(dt_kws):
            for dt_kw in dt_kws:
                ele = {}
                ele['type'] = 'time'
                ele['body'] = dt_kw
                extrator = ExtractDatetime(dt_kw)
                ele['value'] = extrator.get_datetime()
                ele['pattern'] = extrator.get_patterns()
                message_time_kws.extracts.append(ele)
        return message_time_kws


if __name__ == '__main__':
    test_samples = [
        '现在是几点',  # OK
        '三年',
        '未来三天的天气预报',  # 三天
        '现在是10点50分',    # OK
        '六十秒之前',  # OK
        '六十一秒以后',  # OK
        '10秒钟过后',  # OK
        '八分钟之前',    # OK
        '一百分钟以前',   # OK
        '3分钟之后',    # OK
        '三天后是几号',   # OK
        '三天前是几号',   # OK
        '5天以后是几号',  # OK
        '两小时之后是几点',  # OK
        '一年之后',  # OK
        '三十年过后',  # OK
        '100年过后',   # OK
        '后天上午八点',  # OK
        '去年是哪年',  # OK
        '明天下午三点',  # OK
        '下午三点',  # OK
        '现在是一月13日12点50分',  # OK
    ]
    for sample in test_samples:
        message = ExtractNumeral.digitize(sample)
        res_mess = GenDatetime().parse(message)
        print(sample)
        print(res_mess.get_extracts(filter=['pattern']))

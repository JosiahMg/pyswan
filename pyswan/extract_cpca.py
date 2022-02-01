"""
CPCA: china province city area
提取中国省市区/县信息
"""

from pyswan.cpca import transform


class GenPlace:
    @staticmethod
    def parse(message):
        df_message = transform([message.target])
        for d in df_message.index:
            ele = {}
            ele['type'] = 'place'
            ele['province'] = df_message.loc[d]['province']
            ele['city'] = df_message.loc[d]['city']
            ele['area'] = df_message.loc[d]['area']
            ele['code'] = df_message.loc[d]['adcode']
            ele['address'] = df_message.loc[d]['address']
            message.extracts.append(ele)
        return message

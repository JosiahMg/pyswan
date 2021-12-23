from pyswan.numeral import ExtractNumeral
from pyswan.gen_time import GenDatetime

digitize = ExtractNumeral.digitize
parse = GenDatetime().parse

__all__ = [
    "digitize",
    "parse"
]
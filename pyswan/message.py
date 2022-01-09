

class Message:
    def __init__(self, target):
        self.origin = target  # origin input
        self.target = target  # current output
        self.history = []     # store history

        self.time_keywords = []  # extracte datetime

        self.extracts = []

    def insert(self, **kwargs):
        element = {}
        for pro, info in kwargs.items():
            element[pro] = info
        self.history.append(element)


    def merge(self):
        pass

    # 过滤掉self.extracts中的filter属性
    def get_extracts(self, filter=['pattern']):
        res = []
        for extract in self.extracts:
            tmp = {}
            for key, value in extract.items():
                if key not in filter:
                    tmp[key] = value
            res.append(tmp)
        return res




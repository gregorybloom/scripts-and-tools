
class TotalTracker(object):
    def __init__(self):
        self.publicVar = 0
        self._protectedVar = 0
        self.__privateVar = 0
    def __del__(self):

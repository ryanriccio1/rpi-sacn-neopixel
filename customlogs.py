from datetime import datetime
from enum import Enum


class Log(object):
    class LogLevel(Enum):
        NONE = 0
        LEVEL1 = 1
        LEVEL2 = 2
        LEVEL3 = 3
        LEVEL4 = 4

        def __lt__(self, other):
            if self.__class__ is other.__class__:
                return self.value < other.value
            return NotImplementedError

        def __le__(self, other):
            if self.__class__ is other.__class__:
                return self.value <= other.value
            return NotImplementedError

    log_level = LogLevel.NONE

    @staticmethod
    def write_log(message, level):
        if Log.LogLevel.NONE < level <= Log.log_level:
            print(message)
            with open(f"[{datetime.now().strftime('%m-%d-%Y')}]-log.log", 'a') as log_file:
                time_of_event = datetime.now()
                log_file.write(f"[{time_of_event}][{level}]: {message}\n")

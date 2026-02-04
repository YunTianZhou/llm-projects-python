from tool import *


class Logger:
    def __init__(self):
        self.record = []
        self.log = []

    def log_public(self, message):
        print(message)
        self.record.append(message)
        self.log.append(message)

    def log_private(self, message):
        print(message)
        self.log.append(message)

    def extend(self, other):
        self.record.extend(other.record)
        self.log.extend(other.log)

    def save(self):
        with write_file(f"history/{get_date_time()}.txt") as f:
            f.write("\n".join(self.log))

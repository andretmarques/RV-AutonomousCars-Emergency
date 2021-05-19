from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Timer

@dataclass
class CAM:
    id: int
    x: int
    y: int
    time: datetime
    ttl: int

@dataclass
class DENM:
    id: int
    state: bool
    time: datetime
    ttl: int
      
@dataclass
class LOCM:
    id: int
    time: datetime
    x: int
    y: int
    timestamp: datetime
    val: timedelta

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


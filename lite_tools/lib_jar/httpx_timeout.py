# -*- coding: utf-8 -*-
# @Author  : Lodge
"""
      ┏┛ ┻━━━━━┛ ┻┓
      ┃　　　　　　 ┃
      ┃　　　━　　　┃
      ┃　┳┛　  ┗┳　┃
      ┃　　　　　　 ┃
      ┃　　　┻　　　┃
      ┃　　　　　　 ┃
      ┗━┓　　　┏━━━┛
        ┃　　　┃   神兽保佑
        ┃　　　┃   代码无BUG！
        ┃　　　┗━━━━━━━━━┓
        ┃　　　　　　　    ┣┓
        ┃　　　　         ┏┛
        ┗━┓ ┓ ┏━━━┳ ┓ ┏━┛
          ┃ ┫ ┫   ┃ ┫ ┫
          ┗━┻━┛   ┗━┻━┛
"""
import sys
import time
import signal
import threading
from functools import wraps
from asyncio import iscoroutinefunction

from loguru import logger


lock = threading.Lock()


class HttpXTimeOutError(Exception):
    pass


log = None


def x_timeout(seconds, error_message='HttpX Timed Out'):
    global log
    if sys.platform == "win32":
        lock.acquire()
        if not log:
            log = True
            logger.warning(f"注意: [x_timeout] 仅在linux/unix环境起作用")
        lock.release()

    def decorated(func):
        def _handle_timeout(signum, frame):
            raise HttpXTimeOutError(error_message)

        @wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                return await func(*args, **kwargs)
            except KeyboardInterrupt:
                exit(0)
            finally:
                signal.alarm(0)

        return async_wrapper if iscoroutinefunction(func) else wrapper

    return decorated


class Ticker(threading.Thread):
    """
    这里的不知道怎么用
    A very simple thread that merely blocks for :attr:`interval` and sets a
    :class:`threading.Event` when the :attr:`interval` has elapsed. It then waits
    for the caller to unset this event before looping again.

    Example use::

    t = Ticker(1.0) # make a ticker
    t.start() # start the ticker in a new thread
    try:
      while t.evt.wait(): # hang out til the time has elapsed
        t.evt.clear() # tell the ticker to loop again
        print time.time(), "FIRING!"
    except:
      t.stop() # tell the thread to stop
      t.join() # wait til the thread actually dies

    """
    # SIGALRM based timing proved to be unreliable on various python installs,
    # so we use a simple thread that blocks on sleep and sets a threading.Event
    # when the timer expires, it does this forever.
    def __init__(self, interval):
        super(Ticker, self).__init__()
        self.interval = interval
        self.evt = threading.Event()
        self.evt.clear()
        self.should_run = threading.Event()
        self.should_run.set()

    def stop(self):
        """Stop the this thread. You probably want to call :meth:`join` immediately
        afterwards
        """
        self.should_run.clear()

    def consume(self):
        was_set = self.evt.is_set()
        if was_set:
            self.evt.clear()
        return was_set

    def run(self):
        """The internal main method of this thread. Block for :attr:`interval`
        seconds before setting :attr:`Ticker.evt`

        .. warning::
          Do not call this directly!  Instead call :meth:`start`.
        """
        while self.should_run.is_set():
            time.sleep(self.interval)
            self.evt.set()

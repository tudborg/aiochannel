import asyncio
from .errors import *

if hasattr(asyncio, 'ensure_future'):
    ensure_future = getattr(asyncio, 'ensure_future')
else:
    ensure_future = getattr(asyncio, 'async')


class Channel(object):
    def __init__(self, maxsize=0, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._queue = asyncio.Queue(maxsize, loop=self._loop)
        self._close = asyncio.Event(loop=self._loop)
        self._pending_gets = []
        self._pending_puts = []

    @property
    def maxsize(self):
        return self._queue.maxsize

    def empty(self):
        return self._queue.empty()

    def full(self):
        return self._queue.full()

    def qsize(self):
        return self._queue.qsize()

    def close(self):
        if not self._close.is_set():
            self._close.set()
            for future in self._pending_gets:
                future.cancel()
            for future in self._pending_puts:
                future.cancel()

    def is_closed(self):
        return self._close.is_set()

    def get_nowait(self):
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty as e:
            raise ChannelEmpty(str(e))

    def put_nowait(self, item):
        try:
            return self._queue.put_nowait(item)
        except asyncio.QueueFull as e:
            raise ChannelFull(str(e))

    def __str__(self):
        return repr(self)

    def __repr__(self):
        t = type(self)
        return "<{}.{} at 0x{:02x} maxsize={} qsize={}>".format(
            t.__module__, t.__name__,
            id(self),
            self.maxsize,
            self.qsize()
        )

    @asyncio.coroutine
    def get(self):
        """ Block wait for a channel item, throws ChannelClosed
            when channel is closed and empty"""
        while True:
            if self._close.is_set() and self._queue.empty():
                raise ChannelClosed("channel is closed")
            else:
                if self._close.is_set():
                    # if close is set, we only do nowait gets
                    item = self._queue.get_nowait()
                    self._queue.task_done()
                    return item
                else:
                    # else we are okay with blocking gets
                    get_future = ensure_future(self._queue.get(), loop=self._loop)
                    self._pending_gets.append(get_future)
                    try:
                        item = yield from get_future
                    except asyncio.CancelledError:
                        # get was cancelled, most likely bc channel was closed
                        pass
                    else:
                        self._queue.task_done()
                        return item
                    finally:
                        # no matter what, remove the future from the pending list
                        self._pending_gets.remove(get_future)

    @asyncio.coroutine
    def put(self, item):
        if self._close.is_set():
            raise ChannelClosed("channel is closed")
        else:
            put_future = ensure_future(self._queue.put(item), loop=self._loop)
            self._pending_puts.append(put_future)
            try:
                yield from put_future
            except asyncio.CancelledError:
                raise ChannelClosed("channel is closed")
            finally:
                self._pending_puts.remove(put_future)

    @asyncio.coroutine
    def join(self, timeout=None):
        done, pending = yield from asyncio.wait(
            (self._close.wait(), self._queue.join()),
            loop=self._loop, timeout=timeout,
            return_when=asyncio.FIRST_EXCEPTION
        )
        # if pending, then timeout was reached, cancel pending tasks
        # and raise TimeoutError
        if len(pending) > 0:
            for p in pending:
                p.cancel()
            raise asyncio.TimeoutError()

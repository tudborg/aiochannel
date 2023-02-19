from .errors import ChannelClosed, ChannelFull, ChannelEmpty
from collections import deque
from asyncio import AbstractEventLoop, Event, Future, get_event_loop
from typing import Any, Deque, Generic, Iterator, TypeVar, Optional

T = TypeVar("T", bound=Any)


#
# Most of the Channel implementation is taken directly from the asyncio.Queue implementation.
# The first Channel implementation simply wrapped a closed Event and a Queue, and exposed
# The same-ish API as Queue, but having access to the internals is way easier to deal with.
#
class Channel(Generic[T]):
    """
        A Channel is a closable queue. A Channel is considered "finished" when
        it is closed and drained (unlike a queue which is "finished" when the queue
        is empty)
    """

    _getters: Deque[Future]
    _putters: Deque[Future]
    _maxsize: int
    _loop: AbstractEventLoop
    _finished: Event
    _close: Event
    _queue: Deque[T]

    def __init__(
        self, maxsize: int = 0, *, loop: Optional[AbstractEventLoop] = None
    ) -> None:
        self._loop = loop or get_event_loop()

        if not isinstance(maxsize, int) or maxsize < 0:
            raise TypeError("maxsize must be an integer >= 0 (default is 0)")
        self._maxsize = maxsize

        # Futures.
        self._getters = deque()
        self._putters = deque()

        # "finished" means channel is closed and drained
        self._finished = Event()
        self._close = Event()

        self._init()

    def _init(self) -> None:
        self._queue = deque()

    def _get(self) -> T:
        return self._queue.popleft()

    def _put(self, item: T) -> None:
        self._queue.append(item)

    def _wakeup_next(self, waiters: Deque[Future]) -> None:
        # Wake up the next waiter (if any) that isn't cancelled.
        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                break

    def __repr__(self) -> str:
        return '<{} at {:#x} maxsize={!r} qsize={!r}>'.format(
            type(self).__name__, id(self), self._maxsize, self.qsize())

    def __str__(self) -> str:
        return '<{} maxsize={!r} qsize={!r}>'.format(
            type(self).__name__, self._maxsize, self.qsize())

    def qsize(self) -> int:
        """Number of items in the channel buffer."""
        return len(self._queue)

    @property
    def maxsize(self) -> int:
        """Number of items allowed in the channel buffer."""
        return self._maxsize

    def empty(self) -> bool:
        """Return True if the channel is empty, False otherwise."""
        return not self._queue

    def full(self) -> bool:
        """Return True if there are maxsize items in the channel.
        Note: if the Channel was initialized with maxsize=0 (the default),
        then full() is never True.
        """
        if self._maxsize <= 0:
            return False
        else:
            return self.qsize() >= self._maxsize

    async def put(self, item: T) -> None:
        """Put an item into the channel.
        If the channel is full, wait until a free
        slot is available before adding item.
        If the channel is closed or closing, raise ChannelClosed.
        This method is a coroutine.
        """
        while self.full() and not self._close.is_set():
            putter: Future = self._loop.create_future()
            self._putters.append(putter)
            try:
                await putter
            except ChannelClosed:
                raise
            except BaseException:
                putter.cancel()  # Just in case putter is not done yet.
                if not self.full() and not putter.cancelled():
                    # We were woken up by get_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._putters)
                raise
        return self.put_nowait(item)

    def put_nowait(self, item: T) -> None:
        """Put an item into the channel without blocking.
        If no free slot is immediately available, raise ChannelFull.
        """
        if self.full():
            raise ChannelFull
        if self._close.is_set():
            raise ChannelClosed
        self._put(item)
        self._wakeup_next(self._getters)

    async def get(self) -> T:
        """Remove and return an item from the channel.
        If channel is empty, wait until an item is available.
        This method is a coroutine.
        """
        while self.empty() and not self._close.is_set():
            getter: Future = self._loop.create_future()
            self._getters.append(getter)
            try:
                await getter
            except ChannelClosed:
                raise
            except BaseException:
                getter.cancel()  # Just in case getter is not done yet.
                if not self.empty() and not getter.cancelled():
                    # We were woken up by put_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._getters)
                raise
        return self.get_nowait()

    def get_nowait(self) -> T:
        """Remove and return an item from the channel.
        Return an item if one is immediately available, else raise ChannelEmpty.
        """
        if self.empty():
            if self._close.is_set():
                raise ChannelClosed
            else:
                raise ChannelEmpty
        item = self._get()
        if self.empty() and self._close.is_set():
            # if empty _after_ we retrieved an item AND marked for closing,
            # set the finished flag
            self._finished.set()
        self._wakeup_next(self._putters)
        return item

    async def join(self) -> None:
        """Block until channel is closed and channel is drained
        """
        await self._finished.wait()

    def close(self) -> None:
        """Marks the channel is closed and throw a ChannelClosed in all pending putters"""
        self._close.set()
        # cancel putters
        for putter in self._putters:
            if not putter.cancelled():
                putter.set_exception(ChannelClosed())
        # cancel getters that can't ever return (as no more items can be added)
        while len(self._getters) > self.qsize():
            getter = self._getters.pop()
            if not getter.cancelled():
                getter.set_exception(ChannelClosed())

        # the remaining getters can now be woken up:
        while self._getters:
            self._wakeup_next(self._getters)

        # if channel is already empty, mark finished:
        if self.empty():
            # already empty, mark as finished
            self._finished.set()

    def closed(self) -> bool:
        """Returns True if the Channel is marked as closed"""
        return self._close.is_set()

    def __aiter__(self) -> "Channel":
        """Returns an async iterator (self)"""
        return self

    async def __anext__(self) -> T:
        try:
            data = await self.get()
        except ChannelClosed:
            raise StopAsyncIteration
        else:
            return data

    def __iter__(self) -> Iterator[T]:
        return iter(self._queue)

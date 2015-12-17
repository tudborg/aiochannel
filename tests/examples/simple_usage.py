import unittest
import asyncio
from aiochannel import Channel, ChannelClosed
from time import time


NUMBER = 10000


class SimpleUsageTest(unittest.TestCase):
    def test_simple(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def producer(out):
            for i in range(NUMBER):
                yield from out.put(i)
            out.close()

        @asyncio.coroutine
        def consumer(inp):
            s = 0
            while not inp.closed():
                try:
                    item = yield from inp.get()
                except ChannelClosed:
                    break
                else:
                    s += item
            out.close()
            return s

        @asyncio.coroutine
        def pump(inp, out):
            while not inp.closed() and not out.closed():
                try:
                    item = yield from inp.get()
                except ChannelClosed:
                    break
                else:
                    yield from out.put(item)
            out.close()

        # NOTE that 1 is a HORRIBLE maxsize for real-world use.
        #      Try to change it to something like 1000 and you
        #      will se way better speeds.
        inp = Channel(1)
        out = Channel(1)

        # A producer that emits an integer from range(NUMBER)
        # into the inp channel
        loop.create_task(producer(inp))
        # A pump that just moves things from inp to out
        loop.create_task(pump(inp, out))
        # A consumer that sums all items on channel out
        consumer_task = loop.create_task(consumer(out))

        t = time()
        item_sum = loop.run_until_complete(consumer_task)
        loop.close()
        dt = (time() - t)

        message = """
        Example ran in {}, that is {} elements per second
        The result was {} which hopefully is the same as {}
        """.format(dt, NUMBER / dt, item_sum, sum(range(NUMBER)))

        print(message)

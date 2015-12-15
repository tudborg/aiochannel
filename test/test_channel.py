import unittest
import asyncio
from aiochannel import Channel, ChannelClosed, ChannelFull, ChannelEmpty


class ChannelTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_construct(self):
        """
            Test that we can even construct a Channel
        """
        channel = Channel(loop=self.loop)
        self.assertEqual(channel.maxsize, 0)
        channel = Channel(1, loop=self.loop)
        self.assertEqual(channel.maxsize, 1)
        channel = Channel(maxsize=1, loop=self.loop)
        self.assertEqual(channel.maxsize, 1)

    def test_str_and_repr(self):
        channel = Channel(loop=self.loop)
        expt = "<aiochannel.channel.Channel at 0x{:02x} maxsize=0 qsize=0>".format(id(channel))
        self.assertEqual(repr(channel), expt)

        self.assertEqual(repr(channel), str(channel))

    def test_put_nowait_get_nowait(self):
        channel = Channel(1, loop=self.loop)
        channel.put_nowait("foo")
        self.assertRaises(ChannelFull, lambda: channel.put_nowait("bar"))
        self.assertEqual("foo", channel.get_nowait())
        self.assertRaises(ChannelEmpty, lambda: channel.get_nowait())

    def test_put_get(self):
        """
            Simple put/get test
        """
        testitem = {"foo": "bar"}
        channel = Channel(1, loop=self.loop)
        self.loop.run_until_complete(channel.put(testitem))

        self.assertEqual(channel.qsize(), 1)
        self.assertTrue(channel.full())
        self.assertFalse(channel.empty())

        item = self.loop.run_until_complete(channel.get())
        self.assertEqual(item, testitem)
        self.assertEqual(channel.qsize(), 0)
        self.assertFalse(channel.full())
        self.assertTrue(channel.empty())

    def test_fifo_ordering(self):
        """
            Test that items maintain order
        """
        channel = Channel(3, loop=self.loop)
        testitems = [
            "first", "second", "third"
        ]

        @asyncio.coroutine
        def add_items():
            for item in testitems:
                yield from channel.put(item)

        @asyncio.coroutine
        def get_items():
            out = []
            while not channel.empty():
                item = yield from channel.get()
                out.append(item)
            return out

        # add and check for full
        self.loop.run_until_complete(add_items())
        self.assertTrue(channel.full())
        # retreive and check that everything matches
        outitems = self.loop.run_until_complete(get_items())
        self.assertEqual(outitems, testitems)

    def test_get_throws_channel_closed(self):
        """
            Test that even though a blocking .get() is pending
            on an empty queue, a close() to that queue will make
            the .get() throw a ChannelClosed error
        """
        channel = Channel(1, loop=self.loop)

        @asyncio.coroutine
        def wait_close():
            yield from asyncio.sleep(0.01, loop=self.loop)
            channel.close()

        (get_return, _) = self.loop.run_until_complete(
            asyncio.gather(channel.get(), wait_close(),
                           loop=self.loop,
                           return_exceptions=True)
        )
        self.assertIsInstance(get_return, ChannelClosed)

    def test_put_throws_channel_closed(self):
        """
            Test that when a put blocks, and a channel is closed, the
            put will throw a ChannelClosed instead of waiting to add to channel
        """
        channel = Channel(1, loop=self.loop)
        channel.put_nowait("foo")
        self.assertTrue(channel.full())

        @asyncio.coroutine
        def wait_close():
            yield from asyncio.sleep(0.01, loop=self.loop)
            channel.close()

        (put_return, _) = self.loop.run_until_complete(
            asyncio.gather(channel.put("bar"), wait_close(),
                           loop=self.loop,
                           return_exceptions=True)
        )
        self.assertIsInstance(put_return, ChannelClosed)
        self.assertTrue(channel.is_closed())

    def test_multiple_blocking_gets(self):
        """
            Test that a channel with multiple running get() still works
            out fine when the channel is closed
        """
        channel = Channel(1, loop=self.loop)

        @asyncio.coroutine
        def wait_close():
            yield from asyncio.sleep(0.01, loop=self.loop)
            channel.close()

        futures = [channel.get() for _ in range(1000)]
        futures.append(wait_close())

        result = self.loop.run_until_complete(
            asyncio.gather(*futures,
                           loop=self.loop,
                           return_exceptions=True)
        )
        result.pop()
        for res in result:
            self.assertIsInstance(res, ChannelClosed)

    def test_multiple_blocking_puts(self):
        """
            Test that a channel with multiple running put() still works
            out fine when the channel is closed
        """
        channel = Channel(1, loop=self.loop)
        channel.put_nowait("foo")
        self.assertTrue(channel.full())

        @asyncio.coroutine
        def wait_close():
            yield from asyncio.sleep(0.01, loop=self.loop)
            channel.close()

        futures = [channel.put(i) for i in range(1000)]
        futures.append(wait_close())

        result = self.loop.run_until_complete(
            asyncio.gather(*futures,
                           loop=self.loop,
                           return_exceptions=True)
        )
        result.pop()
        for res in result:
            self.assertIsInstance(res, ChannelClosed)

    def test_join(self):
        """
            Test that a channel is joinable (when closed, and queue empty)
        """
        channel = Channel(1000, loop=self.loop)
        [channel.put_nowait(i) for i in range(1000)]
        self.assertTrue(channel.full())
        # create 1000 gets, should complete the queue
        gets = [channel.get() for _ in range(1000)]

        @asyncio.coroutine
        def runner():
            # sleep a bit, then call 1000 gets on channel, calling channel.close() in the middle
            yield from asyncio.sleep(0.01, loop=self.loop)
            n = 0
            for c in gets:
                n += 1
                if n == 500:
                    channel.close()
                yield from c

        @asyncio.coroutine
        def test():
            self.loop.create_task(runner())  # run the getters in the backgrund
            yield from asyncio.wait_for(channel.join(), timeout=2, loop=self.loop)

        self.loop.run_until_complete(test())

    def test_join_timeout(self):
        """
            Test that join() with a timeout actually times out
        """
        channel = Channel(1, loop=self.loop)

        def test():
            self.loop.run_until_complete(channel.join(0.01))

        self.assertRaises(asyncio.TimeoutError, test)

    def test_put_when_closed(self):
        channel = Channel(1, loop=self.loop)
        channel.close()
        self.assertRaises(ChannelClosed, lambda: self.loop.run_until_complete(channel.put("foo")))

    def test_double_close(self):
        channel = Channel(1, loop=self.loop)
        self.assertFalse(channel.is_closed())
        channel.close()
        self.assertTrue(channel.is_closed())
        channel.close()
        self.assertTrue(channel.is_closed())
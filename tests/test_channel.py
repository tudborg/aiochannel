import aiounittest
import asyncio
from aiochannel import Channel, ChannelClosed, ChannelFull, ChannelEmpty


class ChannelTest(aiounittest.AsyncTestCase):
    async def test_construct(self):
        """
            Test that we can even construct a Channel
        """
        channel = Channel(loop=asyncio.get_event_loop())
        self.assertEqual(channel.maxsize, 0)
        self.assertFalse(channel.full())
        self.assertTrue(channel.empty())
        channel = Channel(1)
        self.assertEqual(channel.maxsize, 1)
        channel = Channel(maxsize=1)
        self.assertEqual(channel.maxsize, 1)

        self.assertRaises(TypeError, lambda: Channel([]))
        self.assertRaises(TypeError, lambda: Channel(1.0))
        self.assertRaises(TypeError, lambda: Channel(-1))

    def test_default_loop(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        channel = Channel()
        asyncio.set_event_loop(None)
        self.assertEqual(channel._loop, new_loop)
        new_loop.close()

    async def test_repr(self):
        channel = Channel()
        self.assertEqual(repr(channel),
                         "<Channel at 0x{:02x} maxsize=0 qsize=0>".format(id(channel)))

    async def test_str(self):
        channel = Channel()
        self.assertEqual(str(channel),
                         "<Channel maxsize=0 qsize=0>")

    async def test_put_nowait_get_nowait(self):
        channel = Channel(1)
        channel.put_nowait("foo")
        self.assertRaises(ChannelFull, lambda: channel.put_nowait("bar"))
        self.assertEqual("foo", channel.get_nowait())
        self.assertRaises(ChannelEmpty, lambda: channel.get_nowait())

    async def test_put_get(self):
        """
            Simple put/get test
        """
        testitem = {"foo": "bar"}
        channel = Channel(1)
        await channel.put(testitem)

        self.assertEqual(channel.qsize(), 1)
        self.assertTrue(channel.full())
        self.assertFalse(channel.empty())

        item = await channel.get()
        self.assertEqual(item, testitem)
        self.assertEqual(channel.qsize(), 0)
        self.assertFalse(channel.full())
        self.assertTrue(channel.empty())

    async def test_fifo_ordering(self):
        """
            Test that items maintain order
        """
        channel = Channel(3)
        testitems = [
            "first", "second", "third"
        ]

        for item in testitems:
            await channel.put(item)

        # add and check for full
        self.assertTrue(channel.full())
        # retreive and check that everything matches
        outitems = []
        while not channel.empty():
            item = await channel.get()
            outitems.append(item)
        return outitems

        self.assertEqual(outitems, testitems)

    async def test_get_throws_channel_closed(self):
        """
            Test that even though a blocking .get() is pending
            on an empty queue, a close() to that queue will make
            the .get() throw a ChannelClosed error
        """
        channel = Channel(1)

        async def wait_close():
            await asyncio.sleep(0.01)
            channel.close()

        (get_return, _) = await asyncio.gather(channel.get(), wait_close(), return_exceptions=True)
        self.assertIsInstance(get_return, ChannelClosed)

    async def test_put_throws_channel_closed(self):
        """
            Test that when a put blocks, and a channel is closed, the
            put will throw a ChannelClosed instead of waiting to add to channel
        """
        channel = Channel(1)
        channel.put_nowait("foo")
        self.assertTrue(channel.full())

        async def wait_close():
            await asyncio.sleep(0.01)
            channel.close()

        (put_return, _) = await asyncio.gather(
            channel.put("bar"),
            wait_close(),
            return_exceptions=True
        )
        self.assertIsInstance(put_return, ChannelClosed)
        self.assertTrue(channel.closed())

    async def test_multiple_blocking_gets(self):
        """
            Test that a channel with multiple running get() still works
            out fine when the channel is closed
        """
        channel = Channel(1)

        async def wait_close():
            await asyncio.sleep(0.01)
            channel.close()

        futures = [channel.get() for _ in range(100)]
        futures.insert(50, wait_close())

        result = await asyncio.gather(*futures, return_exceptions=True)
        result.pop(50)  # pop the result for wait_close()
        for res in result:
            self.assertIsInstance(res, ChannelClosed)

    async def test_multiple_blocking_puts(self):
        """
            Test that a channel with multiple running put() still works
            out fine when the channel is closed
        """
        channel = Channel(1)
        channel.put_nowait("foo")
        self.assertTrue(channel.full())

        async def wait_close():
            await asyncio.sleep(0.01)
            channel.close()

        futures = [channel.put(i) for i in range(100)]
        futures.insert(50, wait_close())

        result = await asyncio.gather(*futures, return_exceptions=True)
        result.pop(50)  # pop the result for wait_close()
        for res in result:
            self.assertIsInstance(res, ChannelClosed)

    async def test_join(self):
        """
            Test that a channel is joinable (when closed, and queue empty)
        """
        channel = Channel(1000)
        [channel.put_nowait(i) for i in range(1000)]
        self.assertTrue(channel.full())
        # create 1000 gets, should complete the queue
        gets = [channel.get() for _ in range(1000)]

        async def runner():
            # sleep a bit, then call 1000 gets on channel, calling channel.close() in the middle
            await asyncio.sleep(0.01)
            n = 0
            for c in gets:
                n += 1
                if n == 500:
                    channel.close()
                await c

        async def test():
            asyncio.ensure_future(runner())  # run the getters in the backgrund
            await asyncio.wait_for(channel.join(), timeout=2)

        await test()

    async def test_put_when_closed(self):
        channel = Channel(1)
        channel.close()
        with self.assertRaises(ChannelClosed):
            await channel.put("foo")

    async def test_double_close(self):
        channel = Channel(1)
        self.assertFalse(channel.closed())
        channel.close()
        self.assertTrue(channel.closed())
        channel.close()
        self.assertTrue(channel.closed())

    async def test_putter_cancel(self):
        channel = Channel(1)
        await channel.put("foo")
        # next put will block as channel is full
        self.assertTrue(channel.full())

        async def test_put():
            await channel.put("bar")

        async def test_cancel():
            await asyncio.sleep(0.01)
            channel._putters[0].cancel()

        result = await asyncio.gather(test_put(), test_cancel(), return_exceptions=True)
        self.assertIsInstance(result[0], asyncio.CancelledError)

    async def test_putter_exception(self):
        channel = Channel(1)
        await channel.put("foo")
        # next put will block as channel is full
        self.assertTrue(channel.full())

        async def test_put():
            await channel.put("bar")

        async def test_cancel():
            await asyncio.sleep(0.01)
            channel._maxsize = 2  # For hitting a different code branch in Channel
            channel._putters[0].set_exception(TypeError('random type error'))

        result = await asyncio.gather(test_put(), test_cancel(), return_exceptions=True)
        self.assertIsInstance(result[0], TypeError)

    async def test_getter_cancel(self):
        channel = Channel(1)

        async def test_get():
            await channel.get()

        async def test_cancel():
            await asyncio.sleep(0.01)
            channel._getters[0].cancel()

        result = await asyncio.gather(test_get(), test_cancel(), return_exceptions=True)
        self.assertIsInstance(result[0], asyncio.CancelledError)

    async def test_getter_exception(self):
        channel = Channel(1)

        async def test_get():
            await channel.get()

        async def test_cancel():
            await asyncio.sleep(0.01)
            channel.empty = lambda: False  # For hitting a different code branch in Channel
            channel._getters[0].set_exception(TypeError('random type error'))

        result = await asyncio.gather(test_get(), test_cancel(), return_exceptions=True)

        self.assertIsInstance(result[0], TypeError)

    async def test_getter_already_done(self):
        channel = Channel(2)

        async def test_done_first_then_put():
            await asyncio.sleep(0.01)
            channel.put_nowait("foo")
            channel.put_nowait("foo")

        await asyncio.gather(channel.get(), channel.get(), test_done_first_then_put())

    async def test_get_nowait_raises_closed(self):
        channel = Channel(1)
        channel.put_nowait("foo")
        channel.close()

        item = channel.get_nowait()
        self.assertEqual(item, "foo")

        self.assertRaises(ChannelClosed, lambda: channel.get_nowait())

    async def test_iter(self):
        channel = Channel()
        [channel.put_nowait(n) for n in range(5)]
        self.assertEqual(list(range(5)), list(channel))

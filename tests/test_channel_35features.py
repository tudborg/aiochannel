from .case import TestCase
from aiochannel import Channel


class ChannelTest(TestCase):
    def test_async_iterator(self):
        """
            Test that we can even construct a Channel
        """
        channel = Channel(loop=self.loop)
        [channel.put_nowait(i) for i in range(10)]
        channel.close()

        async def test():
            s = 0
            async for item in channel:
                s += item
            return s

        result = self.ruc(test())
        self.assertEqual(result, sum(range(10)))

    def test_async_iterator_aborts_not_raises(self):
        channel = Channel(loop=self.loop)

        async def test():
            s = 1
            async for item in channel:
                s += item
            return s

        async def abort():
            await self.sleep(0.01)
            channel.close()

        (result, _) = self.rucgather(test(), abort())
        self.assertEqual(result, 1)

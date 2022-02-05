import aiounittest
import asyncio
from aiochannel import Channel


class ChannelTest(aiounittest.AsyncTestCase):
    async def test_async_iterator(self):
        """
            Test that we can even construct a Channel
        """
        channel = Channel()
        [channel.put_nowait(i) for i in range(10)]
        channel.close()

        s = 0
        async for item in channel:
            s += item
        return s

        self.assertEqual(s, sum(range(10)))

    async def test_async_iterator_aborts_not_raises(self):
        channel = Channel()

        async def test():
            s = 1
            async for item in channel:
                s += item
            return s

        async def abort():
            await asyncio.sleep(0.01)
            channel.close()

        (result, _) = await asyncio.gather(test(), abort())

        self.assertEqual(result, 1)

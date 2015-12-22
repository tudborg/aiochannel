import unittest
import asyncio
from aiochannel import Channel


class SimpleUsageTest(unittest.TestCase):
    def test(Self):

        async def main(loop):
            async def producer(ch):
                for i in range(20):
                    await asyncio.sleep(0.1)
                    await ch.put(i)
                    print("produced %d" % i)
                ch.close()

            async def consumer(ch):
                async for i in ch:
                    print("consumed %d" % i)

            channel = Channel(5)  # Note: Horrible buffer size. Example only
            await asyncio.gather(consumer(channel), producer(channel))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))

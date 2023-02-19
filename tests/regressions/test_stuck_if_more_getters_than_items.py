import aiounittest
import asyncio
from aiochannel import Channel


class Issue13(aiounittest.AsyncTestCase):

    async def test_stuck_if_more_getters_than_items(self):
        """
        This is taken literally from issue #13
        """

        async def dummy_worker(ch):
            async for item in ch:
                pass

        concurrency = 2
        ch = Channel()
        tasks = [asyncio.create_task(dummy_worker(ch)) for _ in range(concurrency)]

        # Imagine we get items list asynchroniosly from web or moreover,
        # via async generator from stream and we do not know how items are there.
        # if i remove this context switch - everything works fine
        await asyncio.sleep(0)
        items = [1]

        for item in items:
            await ch.put(item)

        ch.close()
        await asyncio.gather(*tasks)

    async def test_getters_can_still_arrive_late(self):
        async def dummy_worker(ch):
            async for item in ch:
                pass

        ch = Channel()

        for item in [1, 2, 3]:
            await ch.put(item)
        ch.close()

        tasks = [asyncio.create_task(dummy_worker(ch)) for _ in range(2)]
        await asyncio.gather(*tasks)

        assert ch.closed()
        assert ch.empty()

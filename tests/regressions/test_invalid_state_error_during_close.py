import aiounittest
import asyncio
from aiochannel import Channel


class Issue3(aiounittest.AsyncTestCase):
    async def test_invalid_state_error_during_close(self):
        """Getter is waiting in a task, getter is cancelled from here,
           then channel is closed before yielding loop.
           This is the actual issue reported in issue #3."""
        c = Channel(3)
        getter_task = asyncio.ensure_future(c.get())
        await asyncio.sleep(0)
        getter_task.cancel()
        c.close()

    async def test_invalid_state_error_during_close_putter(self):
        """This case is the same idea as above but with a putter
           instead of a getter"""
        c = Channel(1)
        # add an item, filling the queue, allowing is to produce a putter:
        await c.put(1)
        task = asyncio.ensure_future(c.put(2))
        await asyncio.sleep(0)
        task.cancel()
        c.close()

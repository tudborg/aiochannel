import unittest
import asyncio


class TestCase(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def ruc(self, coros_or_future):
        return self.loop.run_until_complete(coros_or_future)

    def gather(self, *coros, return_exceptions=False):
        return asyncio.gather(*coros, loop=self.loop, return_exceptions=return_exceptions)

    def rucgather(self, *coros, return_exceptions=False):
        return self.ruc(self.gather(*coros, return_exceptions=return_exceptions))

    def sleep(self, delay, result=None):
        return asyncio.sleep(delay, result, loop=self.loop)

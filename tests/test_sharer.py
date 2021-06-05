# Copyright (c) 2021 by Kristoffer Paulsson. <kristoffer.paulsson@talenten.se>
import asyncio
import functools
import unittest
from gist.sharer import SharerMixin, share


class Resource(SharerMixin):
    """Resource to be shared."""

    @share
    def computation(self):
        return 100 * 100 / 2

    @share
    def arguments(self, one, two, three=None, four=None):
        return one == 1 and two == 2 and three == 3 and four == 4

    @share
    def crash(self):
        raise RuntimeWarning("Can you read this exception?")


def run_async(coro):
    """Decorator for asynchronous test cases."""

    @functools.wraps(coro)
    def wrapper(*args, **kwargs):
        """Execute the coroutine with asyncio.run()"""
        return asyncio.run(coro(*args, **kwargs))

    return wrapper


class SharerMixinText(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.resource = Resource()

    @run_async
    async def test_computation(self):
        self.assertEqual(await self.resource.computation(), 5000.0)

    @run_async
    async def test_argumants(self):
        self.assertTrue(await self.resource.arguments(1, 2, 3, 4))
        self.assertTrue(await self.resource.arguments(1, 2, three=3, four=4))
        self.assertTrue(await self.resource.arguments(three=3, four=4, one=1, two=2))
        self.assertFalse(await self.resource.arguments(1, 2))

    @run_async
    async def test_crash(self):
        with self.assertRaises(RuntimeWarning):
            await self.resource.crash()


if __name__ == "__main__":
    unittest.main()

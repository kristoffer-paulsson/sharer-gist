# Copyright (c) 2021 by Kristoffer Paulsson. <kristoffer.paulsson@talenten.se>
"""A way of accessing synchronous resources in an asynchronous event loop without conflicts, deadlocks, corruption or
slowdowns."""
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor


class share:
    """Decorator for a method that is being accessed from an event loop and executed in a worker thread."""

    def __init__(self, exe):
        self._exe = exe

    async def __call__(self, *args, **kwargs):
        future = self._obj.pool.submit(self._exe, self._obj, *args, **kwargs)
        await asyncio.sleep(0)
        return future.result()

    def __get__(self, instance, owner):
        self._obj = instance
        return self.__call__


class SharerMixin:
    """Mixin to be inherited by the resource that has to be shared in the asynchronous environment. By using a thread
    pool executor with one worker, all jobs are carried out one at a time. """

    def __init__(self):
        self._pool = ThreadPoolExecutor(max_workers=1)

    @property
    def pool(self) -> ThreadPoolExecutor:
        """Expose the threadpool executor."""
        return self._pool

    def __del__(self):
        self._pool.shutdown()

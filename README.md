# Resource Sharer

This is a sharer of resources that need to run in a safe synchronous manner but may need to be shared in an asynchronous environment. 

The best way to achieve this is to use a thread pool executor, to run activities that can only be carried out one at a time without being corrupted. The object to be shared among many different tasks, for example, while serving requests from a server to several clients, could be a database of some sort or other type of resource. The object to be shared must be a class and should inherit from `SharedResourceMixin` class. This is the most pythonic way of applying resource sharing to activities in the form of a class method, those are in their turn decorated with the `@share` decorator. After applying the decorator you just call the methods and await them, not because they are `async` but, the decorator makes them asynchronous.

## 1. Making the resource

Let's say we are developing a server using third-party resources, for example, databases, caches, and other utilities. The problem with these is that they only allow one connection per instance, and want to reuse the same connecting socket to spare overhead. Therefore we can only use one socket to connect to them, while we need to run a ton of queries.

First, we need to create a class to wrap the connectivity to this resource by declaring it:

```python
class Database:
    def __init__(self, host, port):
        self._conn = Connection(host, port)

    def add_user(self, name, age, gender):
        stmt = self._conn.query("INSERT INTO users (name, age, gender) VALUES (?, ?, ?);")
        stmt.bind(name)
        stmt.bind(age)
        stmt.bind(gender)

        result = stmt.commit()
        if result.error:
            stmt.rollback()
            raise RuntimeError()

    def show_users(self, name):
        stmt = self._conn.query("SELECT name, age, gender FROM users WHERE name LIKE ?;")
        stmt.bind(name)

        result = stmt.commit()
        if result.error:
            raise RuntimeError()
        
        users = list()
        for row in result.group():
            users.append(row)
        return users
```

If we would use this class now, it would be fine in a single-threaded synchronous environment. But that is not possible on a server that needs to serve multiple connections with clients. The other solution would be to make a multi-threaded environment and then use a `Lock` class inside with a `with self._lock:` statement in each method. However asynchronous environments are more favorable for servers because they are more efficient than multithreading.

## 2. Creating the sharer
Second, we need a sharer, a mechanism that can share this resource in a single-threaded event loop environment but execute the activities separately in a worker thread without messing up the execution state. This is easily done with a `ThreadPoolExecutor` that is instructed to only use one worker. By doing so we know that only one task will be carried out at a time, that is synchronously and serially, not in parallel. Also, we can release control to the scheduler in the event loop saving precious execution time on the main thread for other tasks.

```python
from concurrent.futures.thread import ThreadPoolExecutor

class SharerMixin:
    def __init__(self):
        self._pool = ThreadPoolExecutor(max_workers=1)

    @property
    def pool(self) -> ThreadPoolExecutor:
        return self._pool

    def __del__(self):
        self._pool.shutdown()
```
This is a mixin class that should be inherited by the resource to be shared safely. Just inherit from the mixin class, it adds a `ThreadPoolExecutor` that is publicly exposed via a property and used to offload tasks synchronously.

We also need a nice way to apply the sharing to the methods to be used for offload activities:

```python
import asyncio

class share:
    def __init__(self, exe):
        self._exe = exe

    async def __call__(self, *args, **kwargs):
        future = self._obj.pool.submit(self._exe, self._obj, *args, **kwargs)
        await asyncio.sleep(0)
        return future.result()

    def __get__(self, instance, owner):
        self._obj = instance
        return self.__call__
```

This is a decorator that goes on the resources methods to divert it to be executed in the thread pool, yielding control back to the event loop, and then raising awareness the future is completed returning the result. The decorator takes synchronous methods and wraps them in a coroutine, so they have to be awaited upon. It may look counterintuitive but works perfectly.

## 3. Using the sharer

Thirdly, now we have to apply the sharer on the resource that needs to run completely synchronously without being disrupted or changed by outer factors to maintain control over the task.

```python
class Database(SharerMixin):

    @share
    def add_user(self, name, age, gender):
        # ...

    @share
    def show_users(self, name):
        #...

```

This is how easily and pythonic you apply a sharer to a synchronous resource to be shared amongst several users in an event loop without hazzle. If you would like to see more take a look at [Medium](https://angelos-project.medium.com) or join the [Angelos Project](https://github.com/kristoffer-paulsson/angelos).
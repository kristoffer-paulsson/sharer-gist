# Copyright (c) 2021 by Kristoffer Paulsson. <kristoffer.paulsson@talenten.se>
import asyncio

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


async def task():
    resource = Resource()

    for _ in range(10):
        try:
            print(await resource.computation())
            print(await resource.arguments(1, 2, three=3, four=4))
            await resource.crash()
        except RuntimeWarning:
            pass
        else:
            raise RuntimeError("Resource should raise exception.")


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()

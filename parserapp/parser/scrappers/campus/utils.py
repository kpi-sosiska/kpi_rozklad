import functools
import aiohttp

session = aiohttp.ClientSession()


def cache_async(func):
    cache = dict()

    @functools.wraps(func)
    async def wrapper(*args):
        if args not in cache:
            cache[args] = await func(*args)
        return cache[args]

    return wrapper


async def _req(url, **data):
    async with session.get(url, data=data) as resp:
        return await resp.json()

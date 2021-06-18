import asyncio
import logging

import aiohttp

from parserapp.parser.scrappers import RozkladRetryException


def async_bunch(coros, bunch_size=2):
    for i in range(0, len(coros), bunch_size):
        tasks = [asyncio.create_task(coro) for coro in coros[i:i+bunch_size]]
        for t in asyncio.as_completed(tasks):
            yield t


async def try_(func, attempts=5):
    for attempt in range(attempts - 1):
        try:
            return await func()
        except (aiohttp.client.ClientError,
                asyncio.exceptions.TimeoutError,
                RozkladRetryException
                ):
            logging.exception(attempt)
            await asyncio.sleep(5)
    return await func()


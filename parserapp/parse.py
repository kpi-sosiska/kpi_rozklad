import asyncio

import aiohttp

from parserapp.parser.parser import save_faculties_and_cathedras, parse_and_save_all_groups, teachers


async def main():
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20))
    await session.close()

    await save_faculties_and_cathedras()
    await parse_and_save_all_groups()
    await update_all_teachers()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

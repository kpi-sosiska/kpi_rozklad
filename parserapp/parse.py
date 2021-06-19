import asyncio

import aiohttp

from parserapp.parser.parser import save_faculties_and_cathedras, parse_and_save_all_groups, update_all_teachers


async def main():
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20))

    await save_faculties_and_cathedras()
    await parse_and_save_all_groups(session, skip_saved=True, skip_empty=True)
    await update_all_teachers(session, only_without_fullname=True)

    await session.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

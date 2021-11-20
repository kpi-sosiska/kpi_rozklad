import asyncio

import aiohttp

from parserapp.parser.processing import save_faculties_and_cathedras, parse_and_save_all_groups,\
    update_all_teachers, update_subjects


async def main():
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=15))

    await save_faculties_and_cathedras()
    await parse_and_save_all_groups(session) #, skip_saved=True, skip_empty=True)
    await update_all_teachers(session) #, only_without_fullname=True)
    update_subjects()

    await session.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

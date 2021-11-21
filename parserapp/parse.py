import asyncio

import aiohttp

from parserapp.parser.processing import p0_reset, p1_faculties_and_cathedras, p2_rozklad_groups, p3_normalize_subjects,\
    p4_match_campus_group, p5_more_teachers_info


async def main():
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=15))

    p0_reset.reset()
    await p1_faculties_and_cathedras.save_faculties_and_cathedras()
    await p2_rozklad_groups.parse_and_save_all_groups(session)
    p3_normalize_subjects.update_subjects()
    await p4_match_campus_group.match_campus_to_all_groups(session)
    await p5_more_teachers_info.update_all_teachers(session, only_without_fullname=True)

    await session.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

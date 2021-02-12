import asyncio

from parserapp.parser.parser import faculties_and_cathedras, groups, teachers


async def main():
    # await faculties_and_cathedras()
    # await groups()
    await teachers()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

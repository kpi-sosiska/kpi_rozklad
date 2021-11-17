import asyncio
import json


alphabet = 'абвгдеєжзиіїйклмнопрстуфчцчшщюяь'  # todo блять


async def get_groups_list(session):
    async def _req(letter):
        url = 'http://rozklad.kpi.ua/Schedules/ScheduleGroupSelection.aspx/GetGroups'
        data = json.dumps({'prefixText': letter})
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        async with session.post(url, headers=headers, data=data) as resp:
            return await resp.json()

    async def _groups(letter):
        r = await _req(letter)
        if 'd' not in r:
            print('error, sleep 10 sec', r)
            await asyncio.sleep(10)
            return await _groups(letter)
        if r['d']:
            return r['d']
        return []

    res = []
    tasks = [_groups(letter) for letter in alphabet]
    for task in asyncio.as_completed(tasks):
        res.extend(await task)
    return res



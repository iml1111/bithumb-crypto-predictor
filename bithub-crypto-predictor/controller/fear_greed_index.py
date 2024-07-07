"""
This module contains functions to fetch the latest Fear and Greed Index data.
"""
from datetime import datetime
from aiohttp import ClientSession


async def fetch_fear_and_greed_index(
    aiohttp_session: ClientSession,
    limit=1,
    date_format=''
):
    """
    Fetches the latest Fear and Greed Index data.
    Parameters:
    - limit (int): Number of results to return. Default is 1.
    - date_format (str): Date format ('us', 'cn', 'kr', 'world'). Default is '' (unixtime).
    Returns:
    - dict or str: The Fear and Greed Index data in the specified format.
    """
    base_url = "https://api.alternative.me/fng/"
    params = {
        'limit': limit,
        'format': 'json',
        'date_format': date_format
    }
    async with aiohttp_session.get(base_url, params=params) as response:
        if not response.ok:
            raise RuntimeError("Fear and Greed Index API: Error Occured.")

        data = await response.json()

        columns = ['value', 'value_classification', 'timestamp', 'time_until_update']
        results = []
        for item in data['data']:
            document = [item['value'], item['value_classification'], item['timestamp']]
            if 'time_until_update' in item:
                document.append(item['time_until_update'])
            results.append(document)

        return {
            'columns': columns,
            'data': results
        }


if __name__ == '__main__':
    import asyncio

    async def main():
        async with ClientSession() as aiohttp_session:
            data = await fetch_fear_and_greed_index(aiohttp_session, limit=30)
            print(data)

    asyncio.run(main())

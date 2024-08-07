import aiohttp


class BithumbAPI:

    def __init__(self):
        self.domain = "https://api.bithumb.com"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
    
    async def get_minutes_candles(
        self, aiohttp_session: aiohttp.ClientSession, 
        market: str,
        unit: int = 60,
        count: int = 200,
    ):
        """
        분(Minute) 캔들 API
        https://apidocs.bithumb.com/v2.0.0/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1
        """
        url = (
            self.domain + f"/v1/candles/minutes/{unit}"
            f"?market={market}&count={count}"
        )

        async with aiohttp_session.get(url=url, headers=self.headers) as response:
            if not response.ok:
                raise RuntimeError("Bithumb API: get_minutes_candles Error Occured.")
            
            candles = await response.json()
            return {
                'columns': [
                    'candle_datetime_kst', 'opening_price',
                    'high_price', 'low_price', 'closing_price',
                    'timestamp', 'candle_acc_trade_price',
                    'candle_acc_trade_volume',
                ],
                'data': [[
                    i['candle_date_time_kst'], i['opening_price'],
                    i['high_price'], i['low_price'], i['trade_price'],
                    i['timestamp'], i['candle_acc_trade_price'],
                    i['candle_acc_trade_volume'],
                ] for i in candles]
            }
    
    async def get_days_candles(
        self, aiohttp_session: aiohttp.ClientSession,
        market: str,
        count: int = 200,
    ):
        """
        일(Day) 캔들 API
        https://apidocs.bithumb.com/v2.0.0/reference/%EC%9D%BCday-%EC%BA%94%EB%93%A4-1
        """
        url = (
            self.domain + "/v1/candles/days"
            f"?market={market}&count={count}"
        )

        async with aiohttp_session.get(url=url, headers=self.headers) as response:
            if not response.ok:
                raise RuntimeError("Bithumb API: get_minutes_candles Error Occured.")
            
            candles = await response.json()
            return {
                'columns': [
                    'candle_datetime_kst', 'opening_price', 'high_price', 'low_price',
                    'closing_price', 'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume',
                    'prev_closing_price', 'change_price', 'change_rate'
                ],
                'data': [[
                    i['candle_date_time_kst'], i['opening_price'],
                    i['high_price'], i['low_price'], i['trade_price'],
                    i['timestamp'], i['candle_acc_trade_price'],
                    i['candle_acc_trade_volume'], i['prev_closing_price'],
                    i['change_price'], i['change_rate'],
                ] for i in candles]
            }
    

if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    async def main():
        session = await aiohttp.ClientSession().__aenter__()

        api = BithumbAPI()
        res = await api.get_days_candles(
            aiohttp_session=session,
            market="KRW-BTC"
        )
        pprint(res)

        await session.__aexit__(None, None, None)

    asyncio.run(main())

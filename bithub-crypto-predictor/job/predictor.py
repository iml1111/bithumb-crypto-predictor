import asyncio
import json
from loguru import logger
from pprint import pprint
from job import Job
from aiohttp import ClientSession
from controller.bithumb_api import BithumbAPI
from controller.fear_greed_index import fetch_fear_and_greed_index
from controller.openai_api import OpenAIAPI, MessageContext
from controller.job.util import convert_param


class Predictor(Job):

    async def run(self, symbol: str, iteration: int = 1):
        logger.info(f"Predictor Job is running for {symbol}")
        iteration, ok = convert_param(iteration, int)
        aiohttp_session = await ClientSession().__aenter__()
        bithumb_api = BithumbAPI()
        openai_api = OpenAIAPI(api_key=self.settings.openai_api_key)

        user_prompt = {}

        logger.info(f"Fetching candles for {symbol}...")
        symbol_minutes_candles, symbol_days_candles = await asyncio.gather(
            bithumb_api.get_minutes_candles(
                aiohttp_session=aiohttp_session,
                market=symbol
            ),
            bithumb_api.get_days_candles(
                aiohttp_session=aiohttp_session,
                market=symbol
            )
        )
        user_prompt[symbol] = {
            'minutes': symbol_minutes_candles,
            'days': symbol_days_candles
        }

        if symbol != 'KRW-BTC':
            logger.info(f"Fetching candles for KRW-BTC...")
            btc_minutes_candles, btc_days_candles = await asyncio.gather(
                bithumb_api.get_minutes_candles(
                    aiohttp_session=aiohttp_session,
                    market="KRW-BTC"
                ),
                bithumb_api.get_days_candles(
                    aiohttp_session=aiohttp_session,
                    market="KRW-BTC"
                )
            )
            user_prompt['KRW-BTC'] = {
                'minutes': btc_minutes_candles,
                'days': btc_days_candles
            }

        logger.info("Fetching Fear and Greed Index data...")
        fear_and_greed_index = await fetch_fear_and_greed_index(aiohttp_session, limit=30)
        user_prompt['fear_and_greed_index'] = fear_and_greed_index

        # Create Prompt
        with open("assets/instruction.md", "r") as f:
            system_context = f.read()
            system_context = system_context.replace("{crypto}", symbol.split('-')[1])

        logger.info("Extracting user prompt to assets/USER_PROMPT.json...")
        with open("assets/USER_PROMPT.json", "w") as f:
            json.dump(user_prompt, f, ensure_ascii=False, indent=4)

        logger.info("Sending prompt to OpenAI API...")
        message_contexts = [
            MessageContext(content=system_context, role="system"),
            MessageContext(
                content=json.dumps(user_prompt, ensure_ascii=False), role="user"
            )
        ]

        with open("assets/REPORT.md", "w") as f:
            token_usages = []
            f.write("# Report\n\n")

            for i in range(iteration):
                response = openai_api.send_message_contexts(message_contexts, json_mode=True)
                logger.info(f"Iteration {i + 1} Completed...")
                result = json.loads(response.choices[0].message.content)
                token_usages.append(response.usage)

                f.write(f"## Iteration {i + 1}\n")
                f.write(f"- **decision: {result['decision']}**\n")
                f.write(f"- **percentage: {result['percentage']}**\n")
                f.write(f"- reason: {result['reason']}\n\n")

            f.write("\n## Token Usages\n")
            for i, token_usage in enumerate(token_usages):
                f.write(f"- Tokens Usage: {i + 1} - {response.usage}\n")

        logger.info("Creating Report to assets/REPORT.md...")
        await aiohttp_session.__aexit__(None, None, None)


